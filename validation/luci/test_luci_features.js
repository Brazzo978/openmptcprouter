#!/usr/bin/env node
'use strict';

// Exercise the real LuCI method extracted from the pinned or patched source.
// RPC and browser storage are controlled, and the retry clock is fully virtual.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const work = path.resolve(__dirname, '../..');
const baseline = process.argv.includes('--baseline');
const skipTheme = process.argv.includes('--without-theme');
const argument = (key, fallback) => {
  const i = process.argv.indexOf(key);
  return i < 0 ? fallback : path.resolve(process.argv[i + 1]);
};
const sourcePath = argument('--source', path.join(work, 'feeds/6.18/luci/modules/luci-base/htdocs/luci-static/resources/luci.js'));
const footerPath = argument('--footer', path.join(work, 'feeds/openmptcprouter/luci-theme-openmptcprouter/luasrc/view/themes/openmptcprouter/footer.htm'));

if (!fs.existsSync(sourcePath)) {
  console.error(`Source missing: ${sourcePath}`);
  process.exit(2);
}

function extractProbe(source) {
  const match = /^\s*probeSystemFeatures\(\)\s*\{/m.exec(source);
  assert(match, 'LuCI method probeSystemFeatures() is missing');
  const start = match.index + match[0].indexOf('probeSystemFeatures');
  const tail = source.slice(start);
  const next = /\n\s*},\s*\n\s*probePreloadClasses\(\)/.exec(tail);
  assert(next, 'could not locate next method after probeSystemFeatures()');
  return tail.slice(0, next.index + next[0].indexOf('}') + 1);
}

const method = extractProbe(fs.readFileSync(sourcePath, 'utf8'));

// Use the pinned LuCI.raise implementation itself: unlike a plain Error it
// appends stack frames to error.message, which the production classifier sees.
function makeRaise() {
  const source = fs.readFileSync(sourcePath, 'utf8');
  const match = /^\s*raise\(type, fmt, \.\.\.args\)\s*\{/m.exec(source);
  assert(match, 'LuCI.raise() is missing from the pinned source');
  const start = match.index + match[0].indexOf('raise(');
  const end = source.indexOf('\n\t\t},', start);
  assert(end > start, 'could not locate end of LuCI.raise()');
  const raise = source.slice(start, end + '\n\t\t}'.length);
  return vm.runInNewContext(`
    String.prototype.format = function(...args) {
      let i = 0; return this.replace(/%[sd]/g, () => String(args[i++]));
    };
    const luci = { ${raise} };
    luci.raise.bind(luci);
  `, { window: {}, Error });
}

const realRaise = makeRaise();
function rpcError(fmt, ...args) {
  try { realRaise('RPCError', fmt, ...args); }
  catch (error) {
    assert(error.message.includes('\n'), 'LuCI.raise must append its real stack to the error message');
    return error;
  }
  throw new Error('LuCI.raise did not throw');
}
const missingJSON = () => rpcError('RPC call to %s/%s failed with error %d: %s',
  'luci', 'getFeatures', -32000, 'Object not found');
const missingUbus = () => Object.assign(rpcError('RPC call to %s/%s failed with ubus code %d: %s',
  'luci', 'getFeatures', 4, 'Resource not found'), { ubusStatus: 4 });
const valid = Object.freeze({ firewall: true, dnsmasq: { dhcp: true } });

function makeHarness({ replies = [], initialCache, sessionId = 'anon', storage } = {}) {
  const store = storage || {};
  if (initialCache !== undefined)
    (store[sessionId] ||= {}).features = initialCache;
  const states = { sessionId, calls: 0, declarations: [], writes: [], timers: [], queued: [], store };
  const session = {
    getID: () => states.sessionId,
    getLocalData: (key) => states.store[states.sessionId]?.[key] ?? null,
    setLocalData: (key, value) => {
      states.writes.push({ session: states.sessionId, key, value });
      (states.store[states.sessionId] ||= {})[key] = value;
      return true;
    }
  };
  const rpc = {
    declare(options) {
      states.declarations.push(options);
      assert.equal(options.object, 'luci');
      assert.equal(options.method, 'getFeatures');
      return () => {
        states.calls++;
        const reply = replies.shift();
        if (reply instanceof Error && reply.ubusStatus && !options.reject)
          return Promise.resolve(options.expect?.[''] ?? reply.ubusStatus);
        if (reply instanceof Error)
          return Promise.reject(reply);
        if (reply === undefined)
          return Promise.reject(new Error('unexpected extra RPC call'));
        // Match rpc.js expect: { '': {} }: wrong JSON types become {}.
        if (options.expect && Object.hasOwn(options.expect, '') &&
            (reply === null || typeof reply !== 'object' || Array.isArray(reply)))
          return Promise.resolve({});
        return Promise.resolve(reply);
      };
    }
  };
  const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const sandbox = {
    Session: session, classes: { rpc }, Promise, Array, Object, Error,
    setTimeout: (fn, delay) => { states.timers.push(delay); states.queued.push(fn); return states.timers.length; },
    clearTimeout: () => {},
    L: { isObject, env: { sessionid: sessionId } }
  };
  const script = `(function() { let sysFeatures = null; return ({ ${method} }); })()`;
  const instance = vm.runInNewContext(script, sandbox, { filename: sourcePath });
  instance.isObject = isObject;
  return { instance, states };
}

async function finish(promise, states) {
  let completed = false, value, failure;
  Promise.resolve(promise).then(v => { completed = true; value = v; }, e => { completed = true; failure = e; });
  for (let turn = 0; turn < 400 && !completed; turn++) {
    await Promise.resolve();
    if (states.queued.length)
      states.queued.shift()();
  }
  assert(completed, 'promise did not settle with the virtual clock');
  return { value, failure };
}

const cases = [];
function test(name, fn) { cases.push({ name, fn }); }

test('object-not-found twice then success: bounded backoff and real feature cache', async () => {
  const h = makeHarness({ replies: [missingJSON(), missingJSON(), valid] });
  const { value, failure } = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(failure, undefined); assert.equal(value, valid);
  assert.equal(h.states.calls, 3); assert.deepEqual(h.states.timers, [250, 500]);
  assert.equal(h.states.writes.length, 1); assert.equal(h.states.store.anon.features, valid);
});

test('ubus status 4 with actual rpc.js description retries once', async () => {
  const h = makeHarness({ replies: [missingUbus(), valid] });
  const { value, failure } = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(failure, undefined); assert.equal(value, valid);
  assert.equal(h.states.calls, 2); assert.deepEqual(h.states.timers, [250]);
});

test('ubus status 4 with a translated description also retries', async () => {
  const translated = Object.assign(rpcError('RPC call to %s/%s failed with ubus code %d: %s',
    'luci', 'getFeatures', 4, 'Risorsa non trovata'), { ubusStatus: 4 });
  const h = makeHarness({ replies: [translated, valid] });
  const { value, failure } = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(failure, undefined); assert.equal(value, valid);
  assert.equal(h.states.calls, 2); assert.deepEqual(h.states.timers, [250]);
});

test('feature RPC declares reject:true for ubus status failures', async () => {
  const h = makeHarness({ replies: [valid] });
  const { failure } = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(failure, undefined);
  assert.equal(h.states.declarations.length, 1);
  assert.equal(h.states.declarations[0].reject, true);
});

test('six failures propagate and a later call may recover', async () => {
  const original = missingJSON();
  const h = makeHarness({ replies: [original, original, original, original, original, original, valid] });
  const first = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(first.failure, original); assert.equal(first.value, undefined);
  assert.equal(h.states.calls, 6); assert.deepEqual(h.states.timers, [250, 500, 1000, 1000, 1000]);
  assert.equal(h.states.writes.length, 0, 'failure must not cache an empty feature object');
  const second = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(second.failure, undefined); assert.equal(second.value, valid);
  assert.equal(h.states.calls, 7); assert.equal(h.states.writes.length, 1);
});

test('concurrent calls share a single in-flight promise and retry sequence', async () => {
  const h = makeHarness({ replies: [missingJSON(), valid] });
  const a = h.instance.probeSystemFeatures();
  const b = h.instance.probeSystemFeatures();
  assert.equal(a, b, 'callers should share the same in-flight promise');
  const [first, second] = await Promise.all([finish(a, h.states), finish(b, h.states)]);
  assert.equal(first.failure, undefined); assert.equal(second.failure, undefined);
  assert.equal(first.value, valid); assert.equal(second.value, valid);
  assert.equal(h.states.calls, 2); assert.deepEqual(h.states.timers, [250]);
});

test('a valid same-session cache avoids RPC', async () => {
  for (const cache of [valid, { firewall: false }]) {
    const h = makeHarness({ initialCache: cache });
    const { value, failure } = await finish(h.instance.probeSystemFeatures(), h.states);
    assert.equal(failure, undefined); assert.equal(value, cache);
    assert.equal(h.states.calls, 0); assert.equal(h.states.timers.length, 0);
  }
});

test('empty, malformed or wrong-type cache must be reprobed', async () => {
  for (const cache of [{}, { firewall: 'true' }, [], 'bad', { firewall: null }]) {
    const h = makeHarness({ initialCache: cache, replies: [valid] });
    const { value, failure } = await finish(h.instance.probeSystemFeatures(), h.states);
    assert.equal(failure, undefined); assert.equal(value, valid);
    assert.equal(h.states.calls, 1); assert.equal(h.states.writes.length, 1);
  }
});

test('a cache under an old session ID cannot bypass the new session probe', async () => {
  const storage = { oldSession: { features: valid } };
  const h = makeHarness({ storage, sessionId: 'newSession', replies: [valid] });
  const { value, failure } = await finish(h.instance.probeSystemFeatures(), h.states);
  assert.equal(failure, undefined); assert.equal(value, valid);
  assert.equal(h.states.calls, 1); assert.equal(h.states.writes[0].session, 'newSession');
});

test('permission, transport, method and unrelated JSON-RPC errors do not retry', async () => {
  const failures = [
    rpcError('RPC call to %s/%s failed with ubus code %d: %s', 'luci', 'getFeatures', 6, 'Permission denied'),
    rpcError('RPC call to %s/%s failed with ubus code %d: %s', 'luci', 'getFeatures', 3, 'Method not found'),
    new Error('HTTP error 503 while calling /ubus'),
    rpcError('RPC call to %s/%s failed with error %d: %s', 'luci', 'getFeatures', -32000, 'Invalid argument'),
    rpcError('RPC call to %s/%s failed with error %d: %s', 'other', 'getFeatures', -32000, 'Object not found')
  ];
  for (const original of failures) {
    const h = makeHarness({ replies: [original] });
    const { failure } = await finish(h.instance.probeSystemFeatures(), h.states);
    assert.equal(failure, original); assert.equal(h.states.calls, 1);
    assert.deepEqual(h.states.timers, []); assert.equal(h.states.writes.length, 0);
  }
});

test('malformed success is rejected, never cached or retried, and later recovery works', async () => {
  for (const malformed of [{}, { firewall: 'yes' }, [], null, 'not JSON']) {
    const h = makeHarness({ replies: [malformed, valid] });
    const first = await finish(h.instance.probeSystemFeatures(), h.states);
    assert(first.failure, 'malformed reply must reject');
    assert.equal(h.states.calls, 1); assert.deepEqual(h.states.timers, []);
    assert.equal(h.states.writes.length, 0);
    const second = await finish(h.instance.probeSystemFeatures(), h.states);
    assert.equal(second.failure, undefined); assert.equal(second.value, valid);
    assert.equal(h.states.calls, 2);
  }
});

// Render the footer's supported dispatcher-session if/end blocks using a mocked
// Lua context. This intentionally is not a general Lua template interpreter.
function renderFooter(template, authsession) {
  const directive = /<%-?\s*(if\s+(.+?)\s+then|else|end)\s*-?%>/g;
  const sessionExpr = /^(?:(?:luci\.)?dispatcher|disp|require\s*\(\s*(['"])luci\.dispatcher\1\s*\))\s*\.\s*context\s*\.\s*authsession$/;
  const stack = []; let active = true, offset = 0, rendered = '', match;
  while ((match = directive.exec(template))) {
    if (active) rendered += template.slice(offset, match.index);
    if (match[2]) {
      assert(sessionExpr.test(match[2].trim()), `unsupported footer guard: ${match[2]}`);
      const condition = authsession !== null && authsession !== undefined && authsession !== false;
      stack.push({ parent: active, condition });
      active = active && condition;
    }
    else if (match[1] === 'else') {
      assert(stack.length, 'unexpected Lua else');
      const top = stack[stack.length - 1];
      active = top.parent && !top.condition;
    }
    else {
      assert(stack.length, 'unexpected Lua end');
      active = stack.pop().parent;
    }
    offset = directive.lastIndex;
  }
  assert.equal(stack.length, 0, 'unterminated footer guard');
  if (active) rendered += template.slice(offset);
  return rendered;
}

if (!skipTheme) test('theme footer starts menu only for an authenticated dispatcher session', async () => {
  const footer = fs.readFileSync(footerPath, 'utf8');
  const calls = text => (text.match(/L\.require\(['"]menu-openmptcprouter['"]\)/g) || []).length;
  assert.equal(calls(renderFooter(footer, null)), 0, 'login footer must not start the menu');
  assert.equal(calls(renderFooter(footer, false)), 0, 'false session must not start the menu');
  assert.equal(calls(renderFooter(footer, 'fixture-authenticated-session')), 1,
    'authenticated footer must load the menu once');
});

(async () => {
  let failed = 0;
  for (const { name, fn } of cases) {
    try { await fn(); console.log(`PASS ${name}`); }
    catch (error) { failed++; console.error(`FAIL ${name}\n  ${error.stack || error}`); }
  }
  console.log(`${cases.length - failed}/${cases.length} passed (${baseline ? 'baseline' : 'patched'} source)`);
  process.exitCode = failed ? 1 : 0;
})();
