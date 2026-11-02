# LuCI feature discovery at login

The next v0.64.3-3K candidate includes a downstream patch against the locked
LuCI a3cc0e1 checkout. Upstream 0.64.2, kernel 6.18 and package-feed URLs stay
unchanged. The patch is tracked in `patches/luci-features-startup-retry.patch`
and applied idempotently by `apply-luci-startup-fix.py` during normal preparation.
A different upstream HEAD or non-applicable patch stops preparation.
The patch tool runs in forced-direction mode, with source postconditions. Its
automatic reverse-direction guessing must not classify unpatched originals as
already patched. The 2026-11-02 first rebuilt image was rejected by the final
marker/package checks for exactly that helper error; it was not published.

The reported error is `luci/getFeatures`, JSON-RPC -32000 `Object not found`.
The pinned core probes features during initialization, including the login page;
its anonymous ACL intentionally permits that read. In the candidate image, the
ucode plugin, rpcd-mod-ucode and live `luci` object were present and a real
`ubus call luci getFeatures` succeeded. The affected testers' own logs were not
available, so their backend outage/startup cause has not been established.

Feature discovery now shares one in-flight request and retries only temporary
missing-object replies: at most six calls, with 250/500/1000/1000/1000 ms delays.
Both JSON-RPC missing-object and native ubus status 4 are recognized. LuCI puts
stack frames inside `Error.message`, so classification uses its first line.
Translated descriptions of numeric ubus status 4 do not affect classification.
Permission denial, HTTP/transport, missing method, unrelated server errors and
malformed replies remain errors. Persistent missing objects still produce a
visible failure after the bounded attempts; they are not silently accepted.

Only a feature object with the real mandatory boolean `firewall` field is
cached. Empty/malformed caches are reprobed; native ubus errors reject rather
than becoming a cached empty object. Failure clears the rejected in-flight
promise so a later initialization can recover. Session permissions are unchanged.
The OMR theme starts its navigation only when the dispatcher has an authenticated
session; login and logout pages do not load that authenticated menu.

The patched luci-base has explicit version `26.210.61729~a3cc0e1-r1` in both APK
metadata and the runtime revision used by asset URLs. This distinguishes it
from the upstream package and invalidates the previous browser script cache.

## Verification

The source-derived Node suite passed 12/12, using actual `LuCI.raise()` with
stack-bearing messages; the original pinned core is a negative control. See
`validation/luci/README.md` for commands and limits.

A disposable x86 QEMU snapshot booted the already compiled candidate. The real
backend answered feature queries and default TCP congestion was `bbr`. In the
browser, one injected missing-object response reproduced the original red
notification. With reviewed sources installed in that snapshot, two injected
missing-object replies recovered on the third real-backend request and the
login page stayed usable without that notification. Password rejection,
successful authentication, authenticated navigation and logout also passed.
This is real guest/browser testing with injected RPC faults, not evidence of
the original testers' outage cause or final rebuilt-image acceptance.

Rebuild luci-base, the OMR theme and base-files, verify installed patched bytes,
runtime/package revision, preserved profiles and the full image manifest, then
repeat login/logout on that rebuilt image before public release. A test build
must not be described as published because these source/VM checks passed.
