# Installed profile candidate: 2026-11-03 findings

The subsequent clean VMware import exposed an MQVPN r6 first-start route
failure during initial pairing. Publication is held pending its correction;
see [the first-start investigation](3K-MQVPN-FIRST-START-20261103.md). The
successful results below retain their recorded scope.

Source feed `04a25941f4dd39c1371feb4ebd05bda800042091` includes
`omr-profiles` 1-r4, MQVPN 0.16.2-r6, tracker 2.0-r3 and dashboard revision 2.
It preserves the preceding 3K modifications. These
findings came from the rebuilt x86 VMware candidate paired with a clean-installed,
rebooted Debian VPS running admin 3k7 and the frozen 3K kernel. Published release
assets have not been replaced.

## Corrections found with the actual installed image

1. An authentication token staged by the normal VPS synchronization was treated
   as unsaved user configuration and disabled the profile controls. Ignore only
   syntactically valid JWT assignments to existing `server` sections. Mixed edits,
   deletion, malformed tokens, unknown/non-server sections and other packages
   still block. No user delta is committed or discarded by this correction.
2. Four readiness commands used nonexistent `/sbin/ubus`; the package installs
   `/bin/ubus`. A working Glorytun TCP connection therefore failed validation
   and rolled back. Fix Glorytun, interface, proxy and stopped-service checks;
   fixtures must model the actual command layout instead of accepting a
   substring in an impossible command.
3. Stopping MQVPN could leave netifd's persistent tunnel and metric-zero default.
   No tunnel now brings down only the logical `omrvpn`, selects the live default
   on the unique configured master WAN and replaces OMR's metric-one WAN default.
   This handover must happen within the transaction rather than waiting for
   health polls from the restarted tracker. Return transitions enable `omrvpn` again. LAN/WAN
   UCI parameters and unrelated pending changes are preserved.
4. Service transition failures now identify the service/action or failed
   readiness check. Worker exceptions log only their source location, avoiding
   exception text that might contain private values.
5. A restored WAN could remain missing from MQVPN's explicit path list until a
   later tracker state change. The hotplug hook and healthy tracker poll now add
   only missing eligible paths, preserving backup flags and respecting profile
   transactions. The control helper requires an affirmative API reply. No live
   daemon restart is used by this reconciliation.
6. MQVPN's recovery timer now survives the reconnecting state and stops at
   CLOSED/shutdown. This lets a late route/IP event recover a failed path without
   relying on the same event being delivered twice. Explicit API removal still
   stays removed until explicitly re-added. Patch 040 is mirrored in the VPS
   source repository; its deployed frozen server binary is unchanged.
7. The dashboard now displays the same quick A/B profile control as OMR Status.
   Its dependency is explicit and its package revision is incremented.

`coreutils-sleep` and `omr-api-paths` 1-r2 from the preceding installed API fix
remain required. The earlier 2026-11-02 API-fix OVA contains profiles 1-r3;
installing a hotfix on the test router does not update that OVA. The next complete
image must use this source lock, carry 1-r4 and repeat built-image/fresh-boot checks.

## Completed installed tests

- Fresh candidate router retrieved its actual VPS keys and established MQVPN.
- Default, Performance and Stability / Gaming applied and confirmed through the
  real profile RPC. Explicit Gaming rollback restored the preceding Performance
  settings on both ends.
- Performance (old) and Stability (old) applied and confirmed after correcting
  the deployed ubus path. Real Glorytun TCP peer and Internet ICMP, DNS and HTTPS
  egress passed. A live Glorytun MPTCP socket was observed. Return to MQVPN passed.
- With balancing disabled and one available master, No tunnel applied and
  confirmed. TCP through the actual SOCKS/MPTCP proxy exited from the VPS; Internet
  ICMP and UDP DNS passed, and forwarded LAN UDP/ICMP route lookups resolved to
  the master WAN. The old TUN was absent. Return to Default re-established MQVPN.
  Balancing mode correctly marks this profile unavailable; do not silently bypass
  this prerequisite.
- Real WireGuard peers in two independent Linux namespaces reached the GUI via
  the actual VPS and MQVPN router. The full peer exited Internet through the VPS.
  Add/list/disable/enable/remove and cleanup passed; re-enable recovery took
  approximately 12 seconds without resetting the client.
- The WireGuard LAN matrix passed with an actual distinct LAN host: global deny
  overrides a peer grant, peer deny overrides a global grant, and only both grants
  allow the echo service. GUI access survived all four combinations. Revoking the
  peer grant stopped a previously established TCP exchange. The initial deny gate
  and pre-existing peer were restored. The final driver reports **28/28 checks**.
  The test host needed temporary return routes because its ordinary gateway was
  outside OMR; this was test-environment setup, not a client firewall change.
- Lua model/transport tests, real nixio lock/quick-store tests, real libuci staged
  change preservation, runtime route/proxy tests and paired Lua/Python contract
  tests passed again with these source changes.
- Custom profile capture, asymmetric router/VPS settings, A/B selection without
  applying, A/B/A application, deletion and restoration passed **9/9 checks**.
- The real dashboard slider started a profile change; leaving it unconfirmed
  restored Gaming automatically on router and VPS. The saved A/B pair was
  unchanged, and the browser showed the timeout result without a feature RPC
  error. This also verifies the dashboard control through a real UI click.
- Actual installed MQVPN r5 plus the candidate path wrappers passed **20/20
  failover checks**: each WAN was interrupted separately, TCP and UDP progressed,
  API discovery worked with either WAN down, and the MQVPN PID and tunnel ifindex
  stayed unchanged. Maximum observed TCP reply gaps were 7.64 seconds for the
  first interruption and 0.23 seconds for the second; UDP gaps were 0.22 and 0.21
  seconds. TCP used the MPTCP proxy, while UDP used MQVPN. These identities alone
  do not prove an unchanged QUIC connection.
- The native MQVPN recovery lab reproduced a late-route timeout with the old
  engine and recovered tunnel traffic with patch 040. Explicit remove/re-add
  preserved the surviving path and passed TCP/UDP traffic. The sanitized source
  evidence is `mqvpn/tests/reconnect-path-recovery-lab-20261103.json` in the feed.
  This is engine-level Linux lab evidence, separate from the final OpenWrt r6 APK.
- The signed r6/r4/r3/dashboard APKs were subsequently installed on the paired
  VMware router. **23/23 checks** passed, including exact installed runtime
  files, the stripped binary extracted from the signed APK, preserved profile
  store and unrelated world constraints, the exact r6 world hold, peer traffic
  and `fec_enabled=1`. Compiled FEC capability is distinct from enabling FEC in
  a chosen profile. The QA verifier initially compared an unstripped build copy
  and expected a JSON boolean instead of the API's numeric flag; those verifier
  assumptions were corrected before acceptance.
- Actual r6 repeated **20/20 failover checks**. WAN1/WAN2 TCP reply gaps were
  8.67/0.22 seconds; UDP gaps were 0.22/0.22 seconds. No daemon restart or TUN
  replacement occurred during either single-WAN interruption.
- Actual r6 native MQVPN and independent Xray TCP forwarding passed **17/17
  smoke checks**, including distinct public listeners, HTTP response markers,
  backend rules, exact temporary-section removal and unchanged existing rules.
  The GUI was never used as the public canary. Both test ports were released.
- Actual r6 repeated **13/13 WireGuard checks**: GUI and full-tunnel traffic,
  public VPS egress, peer lifecycle and complete cleanup. The earlier distinct
  LAN host matrix remains the 28/28 run; it was not silently counted again.

These are functional tests with two virtual WANs and namespace WireGuard clients.
They do not establish physical fiber/5G throughput, zero-loss failover, mobile QR
onboarding, IPv6 parity or legacy-package upgrade safety.

## Final rebuilt image

The complete x86 build finished successfully on 2026-11-03 at 12:18:39 UTC.
Its root revision is `21e416687c9b549d9f4fc8701c6a24f430f50614`, with the feed
revision above. The first package attempt failed while recovering the libbpf
source archive; a serial diagnostic compile succeeded, and the pinned build
resumed without a source change. Both attempt logs are retained in the job.

All **54 built-filesystem/manifest checks** passed. The exact raw image then
booted in an isolated QEMU snapshot without source overlays or VPS credentials:
**16/16 checks** passed, including actual `luci/getFeatures`, fractional sleep,
BBR default, package versions, r6 world hold, hotplug executable and a MQVPN
binary hash equal to the signed package used in paired traffic tests.

VMware disk conversion, OVF Tool verification and `qemu-img` comparison of the
canonical VMDK to the verified source disk passed. The local OVA is
`openmptcprouter-0.64.3-3K.ova` (107591680 bytes), SHA-256
`84651d6ded830aa845a94c4861c522708f854dd4d27975e7b660251941e3e8fe`.
It is a factory test candidate, with LAN/WAN1/WAN2 E1000 adapters, two vCPUs,
2048 MiB RAM and BIOS VMX-13. Public release assets remain unchanged.

See [the recorded results](../validation/paired-20261103/README.md). The isolated
guest and browser were stopped; the paired router remains on Default with no
pending transaction and its saved A/B pair preserved.
