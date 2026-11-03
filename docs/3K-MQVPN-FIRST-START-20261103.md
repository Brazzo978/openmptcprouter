# MQVPN first-start route failure found on the clean VMware import

The user imported the complete x86 OVA on 2026-11-03. Read-only attestation
passed the release, kernel, package versions and exact MQVPN/runtime hashes.
Both initially empty WANs were configured with DHCP under a timed rollback;
fresh SSH and both leases were verified before disarming that rollback.

The normal wizard paired the router with the test VPS and retrieved its real
configuration. During the first synchronization a network reload withdrew both
WAN addresses briefly. MQVPN's first tunnel callback reported:

```
failed to pin server route
route setup failed, aborting tunnel
```

The WAN routes subsequently recovered, while the same MQVPN r6 process stayed
alive with its control API reachable and no TUN. No restart or local bypass was
used to turn this observation into a successful acceptance result. The private
original log was preserved on the router, without copying credentials into
this repository.

The failure path calls `mqvpn_client_disconnect()`, which means intentional
shutdown to the library. It transitions to CLOSED and suppresses reconnect.
The platform event loop remains alive because the local shutdown flag was not
set. The r6 path-recovery correction covers dropped paths during reconnect
after a working tunnel; it does not repair this initial platform-setup failure.

The r7 correction retries local tunnel setup asynchronously, using
only configuration belonging to the live connection. It backs off between failed
attempts, recovers paths before the first TUN and cancels retries on teardown,
explicit stop or reconnect-disabled operation. Preserve native LAN routes, FEC,
existing API path-removal semantics and successful established-session failover.

Patch 050 is mirrored identically in the VPS source repository. Its SHA-256 is
`ea1ce72382baa3042978c37b6532c864f6580d51aeb0778168fe7a762ec417ce`.
The full 010–050 chain applies to pinned source
`ee78205d3db491ca7727b974bda0c91ae1523236`; resulting source files match the
native binary's compiled inputs. The correction keeps its stream-liveness
guard private and preserves the public library API and server protocol.

Native GCC/CMake compilation and these isolated Linux cases passed:

- Recover after the initial `/32` server-pin failure with RouteViaServer,
  keeping the same PID and passing tunnel traffic. The r6 comparison fails to
  recover under the same fault.
- Reconnect disabled: remain CLOSED, never recreate the TUN and stop on SIGTERM
  even when already CLOSED.
- Stop during deferred setup: never recreate the TUN afterward.
- Lose the path before the first TUN, restore its link before its route and
  recover periodically once the route returns, without an API path-add or
  reusing stale tunnel information.
- Retain patch 040's established-session late-route recovery behavior.

The pin-error shim is bind-mounted only inside a verified private mount and
network namespace; it does not replace the host's `ip` command. Four package
hold fixtures also pass for r7, including stale-pin migration and preservation
of unrelated world constraints.

The signed OpenWrt r7 package was installed normally on the actual VMware
router. Its extracted binary matches the installed binary byte for byte.
Eleven package/runtime checks, twenty WAN failover checks, seventeen native
MQVPN/independent Xray forwarding checks and thirteen WireGuard GUI/full IPv4
tunnel/lifecycle checks passed. The router was returned to confirmed Default,
without a pending transaction or a changed saved A/B pair.

The replacement factory image was built from root
`b9c7e8cedfd5ad7077c30d9c95766b66a4eb32df` and client feed
`c5730aab311781467f19e4898b2ce82b77b08235`. All 57 filesystem/manifest
checks and 16 fresh-boot checks passed, including the installed MQVPN hash.
The exact factory image also passed 19 first-pairing and restoration checks
in an isolated snapshot, without an overlay, SSH key or preconfigured VPS
credentials. The ordinary wizard retrieved the VPS configuration; the TUN,
peer ping, DNS and HTTPS Internet egress through the VPS all worked. That
particular run observed no initial route error: the native fault-injection
comparison above separately proves recovery from the reported error path.

Only one client used VPS user 0 at a time. The isolated guest was proven stopped
before restoring the actual router's executable mode and service. Fresh SSH,
peer traffic, confirmed Default and no pending transaction were verified before
disarming rollback. Independent timers are best-effort protection, not an
ordering guarantee during host/watchdog failure.

The raw image hash remained unchanged after pairing: QA credentials are not
embedded in the deliverable. VMware OVF verification and canonical VMDK content
comparison passed. The replacement OVA is ready for local testing; no public
release asset was replaced. See
[the r7 acceptance records](../validation/first-start-r7-20261103/README.md).
The earlier r6 OVA remains held and its preceding filesystem and boot reports
retain their original, narrower scope.
