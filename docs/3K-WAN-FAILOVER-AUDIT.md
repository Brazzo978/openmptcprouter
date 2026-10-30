# WAN failure audit: MPTCP redundant, MQVPN minrtt and VPS API routing

Reviewed 2026-10-30. This is a source-level investigation of tester reports,
with isolated reproductions. No affected router was available, no customer
network was accessed and no WAN, service or installed configuration was changed.
The original audit changed no production implementation.

Subsequent candidate development is tracked in `omr-v0.64.2-3K-next`. This document
describes the original baseline; consult the maintained inventory and the new
candidate's test evidence before using these findings as a current status report.

## Scope and provenance

- Build-root snapshot: `eee8592aa66c1f6458ded45954dc93e65feef433`.
- 3K feed: `0060b841b1130be31db8b6826d14d3d02520add6`.
- Client package `mqvpn/Makefile`: 0.16.2-r4, upstream MQVPN commit
  `ee78205d3db491ca7727b974bda0c91ae1523236`, with the native-LAN and FEC
  capability patches. The forced path-0 connection-close code already exists
  in that upstream source; it is not introduced by the native-LAN patch.
- Engine review used `mqvpn_engine/native-routing`; compare the exact functions
  to the pinned upstream snapshot before attributing behavior to other builds.
- The nine reproducible cases and limitations are in
  [validation/failover](../validation/failover/README.md). Generated results
  record the actual input-file SHA-256 values. All nine reproduced the expected
  current behavior, including undesirable behavior. This is not failover acceptance.

## What should survive a WAN failure

With an established, usable alternative subflow, an MPTCP connection can continue
after losing one subflow; this does not guarantee zero loss or zero delay. See
[RFC 8684, reliability and failure handling](https://www.rfc-editor.org/rfc/rfc8684.html#section-3.3.6).
The reviewed `mptcp-bpf-red/src/mptcp_bpf_red.c` schedules the available subflows;
it does not contain a special rule that closes the connection when the configured
WAN master disappears. Kernel behavior and real application continuity were not
executed in this audit.

MPTCP `bpf_red` and MQVPN `minrtt` are different mechanisms. MQVPN uses QUIC over
UDP and its own connection/path lifecycle. A redundant MPTCP scheduler cannot
prevent an MQVPN connection from being explicitly closed by its engine or
restarted by a watchdog. Correlate the TCP/proxy and VPN sessions separately.

## Finding A: removing initial QUIC path intentionally closes the connection

The reviewed control flow is:

1. `omr-tracker/files/usr/share/omr/post-tracking.d/005-mqvpn-path`, on a new
   `ERROR` transition for a registered WAN path, invokes
   `mqvpn-path remove "$OMR_TRACKER_DEVICE"`. The error branch has no master-only
   condition. Isolated executions reproduce removal for both `master` and `on`.
2. `mqvpn/files/usr/bin/mqvpn-path` sends `remove_path` to the **local** MQVPN
   control socket. This is independent of the remote VPS administration API.
3. Engine `src/platform/linux/control_socket.c` dispatches to
   `platform_remove_path` in `src/platform/linux/platform_linux.c`. It refuses
   removal of the last platform path; otherwise it invokes
   `mqvpn_client_remove_path` and removes the corresponding platform socket.
4. `src/mqvpn_client.c::mqvpn_client_remove_path` calls `xqc_h3_conn_close` when
   the removed live path has `xqc_path_id == 0`. It does so without checking
   whether an alternative usable path could preserve the connection. A successful
   secondary-path removal instead uses `xqc_conn_close_path`; failure of that
   operation also falls back to closing the whole H3 connection.
5. The close/reconnect lifecycle enters `RECONNECTING`; the Linux platform's
   state callback deliberately destroys the TUN and cleans routing resources,
   then recreates them when tunnel configuration is ready again.

The C reproducer executes the actual extracted removal functions against mocked
xquic calls. With two fixture paths marked live, removing path 0 calls connection
close while the second fixture path remains live. This proves the branch decision;
it does not prove that the surviving path in a tester's router was validated,
reachable, or able to transmit during a real failure.

The source comment explains the forced close as a workaround for a path-0 xquic
blackhole after `xqc_conn_close_path`. Its stated recovery/PING durations are
historical author commentary, not measurements from this audit. Simply deleting
the workaround is not a validated fix. Initial QUIC path ID 0 is a connection
identity, not the current configured WAN master label; these can differ.

## Finding B: link events and tracker removal take different engine branches

`mqvpn_client_on_platform_path_dropped`, used for platform/netlink drops, calls
`xqc_conn_close_path` even for path 0, without the API-removal branch's explicit
connection close. It ignores that call's return value. Both differences reproduce
in the C fixture. An upstream outage with Ethernet carrier still up may produce
tracker removal without a preceding netlink drop. Physical unplug and upstream
blackhole therefore require separate tests; races can produce different outcomes.

Correction from subsequent real-engine testing: the comments around
`client_check_failover` describe creation on demand for `minrtt`, but
`activate_pending_paths` can already create and validate a configured `BackupPath`
at startup. Actual behavior depends on the activation path. Do not infer that a
configured backup is absent, validated, or usable from that comment alone. The
new lab also found missing `SO_BINDTODEVICE` on startup backup sockets, allowing
their traffic to follow the primary WAN instead. The candidate corrects this
binding and tests a backup whose own veth is blackholed.

## Finding C: VPS API is not master-only, but interface fallback is incomplete

`openmptcprouter/files/etc/init.d/openmptcprouter-vps` functions `_login`,
`_get_json` and `_set_json` initially use ordinary OS routing. On an empty reply,
they iterate interfaces obtained from `multipath | awk '/default/ { print $1 }'`
and bind curl to each one. An ordinary non-master WAN can therefore work; the
offline case confirms that fallback succeeds after an initial route failure.

The filter excludes output labeled `backup` or `subflow`. If the ordinary route
has not converged and the surviving usable interface has one of those labels,
that explicit fallback never attempts it. Ordinary routing may still succeed
once routes converge, so this is a blind spot rather than proof of failure in
every backup topology. A nonempty HTTP error body also stops the empty-response
fallback; response validity and transport reachability are not distinguished.
Preserve deliberate authentication/fail2ban handling when revising retries.

`omr-tracker/files/bin/omr-tracker-server` similarly derives `mp_default_intfs`.
Its `_check_server_intf` and `_ping_server_intf` probe that list; `_do_check_ip`
does not first try the ordinary-route API request used above. With only a healthy
backup labeled interface remaining, the offline API-probe fixture makes no curl
attempt and retains `server_ping=false`. The list may also remain cached briefly.
This can produce a false VPS-down decision, followed by server/proxy state changes.
The helper also accepts a nonempty curl response without requiring a valid API body.

An empty administration response alone is not shown to restart MQVPN directly:
the MQVPN settings-sync branch requires a nonempty key and a real configuration
difference. An API outage and a tunnel outage must be correlated before assigning
causality. Finding A can occur even when the VPS administration API is healthy.

## Finding D: recovery watchdog can amplify tunnel transitions

The virtual-VPN failure branch of post-tracking `002-error` can restart MQVPN.
`omr-schedule/.../010-services` separately recovers a missing process. The shared
60-second cooldown is already present and must be preserved; this audit does
not claim that fix is missing. A TUN teardown during engine reconnect can still
interact with tracker recovery. Whether that happened to testers is unproven.
Do not describe every physical-WAN error as a direct MQVPN service restart.

## Next implementation and acceptance boundaries

1. Repair the MQVPN path-0 lifecycle with verified alternate-path readiness and
   xquic behavior; retain the TUN/session when safe and retain a bounded whole-
   connection recovery when all paths are unusable. Do not blindly remove the
   current workaround. Exercise client and matching server builds.
2. Define a shared eligible-interface/reachability policy for administration and
   server tracking, including usable backup paths during failure, without changing
   normal backup-cost policy or authentication retry safeguards.
3. Make watchdog recovery aware of connection recovery/path health to avoid a
   second unnecessary reset; retain cooldown and true all-paths-down recovery.
4. Execute inventory T15/F1-F7 in a disposable two-WAN router/VPS lab, observing
   long-running TCP and UDP, session identity, TUN lifetime, monotonic timestamps,
   API health, physical unplug versus blackhole, master change, recovery and churn.
   Existing path-abandon/dellink tests do not alone establish unchanged connection
   identity or uninterrupted traffic. Add these acceptance criteria explicitly.

No production fix, new image, performance claim or confirmed explanation of every
tester incident is delivered by this audit. The concrete control-flow problems
are reproduced and the next changes have a defined validation scope. Preset work
must retain the complete [3K inventory](3K-MODIFICATIONS.md) and pass these gates.
