# Connection profiles: source candidate and test handoff

Implemented in the `omr-v0.64.2-3K-next` feed/build branches and paired
`omr-vps-0.1163-3K-next` source. The exact feed is pinned in `source-lock-3k.json`.
The candidate is not included in existing published firmware or VPS bundles.

## Using the GUI

OMR Status has a native A/B switch with two configurable profile slots. Saving
the pair does not apply a profile; changing the switch starts a guarded apply.
Its position changes after confirmation. If the active configuration is outside
the pair, either labelled endpoint can activate its profile. The pair is stored
privately with the presets and survives local backup/sysupgrade.
**System → OpenMPTCProuter → Connection
profiles** shows built-ins, custom profiles, router/VPS settings and their
verification status. Select a profile, wait for both sides to verify, then
choose **Keep profile** within 60 seconds or **Revert**. The interface reports
an incomplete restore for retry rather than claiming success.

| Preset | VPN | MPTCP scheduler | TCP congestion | MQVPN scheduler / congestion |
|---|---|---|---|---|
| Default | MQVPN | default | BBRv3 (`bbr`) | minrtt / bbr2 |
| Performance | MQVPN | default | nanbbr3_light | wlb / bbr2 |
| Stability / Gaming | MQVPN | bpf_red | BBRv3 (`bbr`) | minrtt / bbr2 |
| Performance (old) | Glorytun TCP | default | BBRv3 (`bbr`) | inactive |
| Stability (old) | Glorytun TCP | bpf_red | BBRv3 (`bbr`) | inactive |

The labels state intended use, not benchmark results. Default resets the complete
managed MQVPN tuning set; Stability / Gaming and Performance retain other tuning.
The `gaming` ID is stable. The old profiles set the main proxy to none so normally
VPN-routed TCP, UDP and ICMP pass inside Glorytun TCP; returning to an MQVPN
profile restores the recorded MQVPN proxy flags, including Xray choices.
Custom profiles save supported tuning and transport snapshots separately for
router and VPS; older custom profiles without transport data need to be saved
again. Default keeps client reorder enabled and server reorder disabled.
Both tunnels require existing valid configuration. WAN/LAN settings, keys,
forwarding definitions, independent Xray port forwarding and WireGuard LAN
permission are preserved. Existing bypass/local/management routes still apply;
these profiles do not promise IPv6 coverage or a kill switch.

Profile changes can restart services and interrupt traffic. This differs from
the MQVPN WAN-failure continuity fix. Unsupported algorithms, stale/unavailable
VPS capabilities, pending external UCI edits and missing configuration prevent
application rather than producing an unverified partial switch.

Glorytun readiness includes its running process with the MPTCP argument, the
expected local tunnel IPv4 and an interface-bound ping to its configured peer.
If the peer blocks ICMP, switching is rejected and rolled back. Different
configured MQVPN/Glorytun device names are supported. The tracker is restarted
even when a service transition fails.

Keep other configuration editors closed during switching. The profile writer
preserves existing staged WAN data, and pending network/firewall/proxy changes
block application. Legacy proxy init/tracker scripts can still commit UCI, so
an external edit created between the checks is not atomically excluded.

## Runtime and VPS prerequisite

The feed adds `omr-profiles` and `luci-app-omr-profiles`; the existing main LuCI
app depends on the new frontend so its Status module is present on upgrade.
The backend provides `omr.profiles` with separate read/write RPC permissions,
a procd worker, private persistent presets/journal, kernel locks and isolated
libuci updates of only the managed fields. Ordinary VPS synchronization honors
the profile worker's active lease.

The paired VPS needs admin candidate **0.18+20261030-3k6** and explicit v2
discovery. Legacy clients can still discover the v1 contract. The v2 transaction
manages tuning and transport/proxy selection without resubmitting authentication
keys. After tunnel verification, a required route phase updates the configured
router tunnel IPv4 and refreshes DNAT/WireGuard before confirmation. Rollback
restores the previous target as well as the selection and tuning. It uses a
persisted transaction and an independent systemd recovery timer; the server
rollback window is 240 seconds. Monotonic time plus boot identity protects the
deadline against clock changes/reboot. Confirmation-response loss is reconciled
using the recorded transaction decision.

The locally built DEB is a test candidate, not installed or published as a new
VPS release. `validation/profiles/candidate-20261030.json` records its SHA-256
and checks; the published installer/frozen lock remains unchanged. Install and
timer/module-loader acceptance must be performed in a disposable VPS VM before
shipping an updated bundle.

The next-branch preparation wrapper and frozen API version guard both require
3k6. Preparation verifies its metadata, package name/version/architecture and
SHA-256 before reporting success; older packages and metadata are rejected.
This does not fetch the kernel/frozen assets or perform an installation.

## Completed checks and limits

The full profiles page includes a preview selector and three simultaneous
animated path diagrams: ICMP and UDP inside MQVPN, and TCP through the MPTCP
proxy. Stability / Gaming illustrates identical redundant TCP copies and a
minimum-RTT eligible MQVPN path; Performance shows distinct simultaneous TCP
packets on both paths and equal-weight WLB for MQVPN. Its denser TCP stream is
visual emphasis, not a speed measurement. Default uses automatic TCP scheduling
and minrtt MQVPN. Both old profiles show all three protocols through Glorytun
TCP: Performance distributes distinct packets and Stability duplicates them.
This is a
schematic example, not sampled WAN health, packet capture or a performance
measurement. WAN-bound diagnostic pings and TCP forced into the VPN are outside
the illustration. Preview selection never applies tuning. Pause and reduced
motion are supported, and polling does not rebuild the animation's DOM.

The revised diagrams use SVG coordinates and a single logical frame clock.
Distributed packets cycle A on WAN 1, B on WAN 2, C on WAN 1, D on WAN 2,
then repeat; matching letters on both paths represent redundant copies. Fixed
router/cloud anchors match the path fan-out and fan-in. Performance shows at
most two packets per lane with an 8px minimum gap; narrow lanes reduce density.
Preset changes reset the shared epoch, while status polling and pause/resume
preserve it. Deterministic fixture checks and sampled browser frames cover the
sequence, reset, collision bounds, icon placement and 320px layout.

- Lua model tests passed for apply, rollback, timeouts, uncertain confirmation,
  Default asymmetry, custom profiles and algorithm/FEC availability.
- Real nixio lock tests passed: a live owner cannot lose its lock due to age;
  process death releases the lock. Real libuci tests preserved unrelated WAN
  configuration and file permissions while updating managed tuning.
- The real Lua model and Python VPS manager communicated through localhost HTTP
  for Default, Performance with a lost confirmation, Gaming timeout/rollback and
  custom save/revert. Kernel/service/UCI effects were fixtures in this contract test.
- Node frontend cases and Chromium/Playwright checks passed for apply/confirm,
  revert, custom save, literal handling of HTML-like names, desktop and mobile.
  The browser used a simulated service; it was not an installed LuCI router.
- The primary selected VPS test run passed **597 tests and two subtests**, covering the
  new API plus existing API, NanBBR, WireGuard manager/helper, candidate preparation,
  DSCP, Xray and frozen-update checks.
  DEB modules/systemd units were compared byte-for-byte to reviewed sources.
- The full admin suite separately passed 1090 tests with nine skips and two
  subtests. The WireGuard manager lab passed 41 checks again after the installer
  version update; the cross-transport forwarding lab passed nine checks with
  real WireGuard/nft and simulated MQVPN/Glorytun endpoints.
- Real dpkg preparation of 3k6 passed in an isolated copy with an old package
  present. Fourteen fixture cases passed for package/metadata validation.
- API transport regression cases passed, including preserving IPv6 address
  colons in the ordinary synchronization context.

Before release, run inventory T16 on a built OpenWrt image and paired installed
VPS: actual rpcd/procd permissions, daemon startup/reboot recovery, systemd timer
and CC loading, custom persistence/backup, GUI availability during switch,
credentials/routes/forwarding preservation and real traffic. Retain the earlier
failover T15 and WireGuard/native-LAN gates. Host tests do not establish throughput,
latency improvement or a complete package-upgrade path.
