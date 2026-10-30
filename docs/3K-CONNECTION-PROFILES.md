# Connection profiles: source candidate and test handoff

Implemented in the `omr-v0.64.2-3K-next` feed/build branches and paired
`omr-vps-0.1163-3K-next` source. The exact feed is pinned in `source-lock-3k.json`.
The candidate is not included in existing published firmware or VPS bundles.

## Using the GUI

OMR Status has a compact switcher. **System → OpenMPTCProuter → Connection
profiles** shows built-ins, custom profiles, router/VPS settings and their
verification status. Select a profile, wait for both sides to verify, then
choose **Keep profile** within 60 seconds or **Revert**. The interface reports
an incomplete restore for retry rather than claiming success.

| Preset | MPTCP scheduler | TCP congestion | MQVPN scheduler | MQVPN congestion |
|---|---|---|---|---|
| Default | default | BBRv3 (`bbr`) | minrtt | bbr2 |
| Performance | default | nanbbr3_light | wlb | bbr2 |
| Gaming | bpf_red | BBRv3 (`bbr`) | minrtt | bbr2 |

The labels state intended use, not benchmark results. Default resets the complete
managed tuning set; Gaming/Performance change the four fields shown and retain
the other tuning. Custom profiles save supported current settings separately for
router and VPS. In particular Default keeps the original client reorder enabled
and server reorder disabled. Profiles preserve network addresses, WAN/LAN setup,
credentials, forwarding, remote-access gates and VPN type. This first version
requires MQVPN already selected/configured; it does not switch other VPN types.

Profile changes can restart services and interrupt traffic. This differs from
the MQVPN WAN-failure continuity fix. Unsupported algorithms, stale/unavailable
VPS capabilities, pending external UCI edits and missing configuration prevent
application rather than producing an unverified partial switch.

## Runtime and VPS prerequisite

The feed adds `omr-profiles` and `luci-app-omr-profiles`; the existing main LuCI
app depends on the new frontend so its Status module is present on upgrade.
The backend provides `omr.profiles` with separate read/write RPC permissions,
a procd worker, private persistent presets/journal, kernel locks and isolated
libuci updates of only the managed fields. Ordinary VPS synchronization honors
the profile worker's active lease.

The paired VPS needs admin candidate **0.18+20261030-3k5**. Its new API modifies
only tuning, without resubmitting MQVPN's global authentication key. It uses a
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
3k5. Preparation verifies its metadata, package name/version/architecture and
SHA-256 before reporting success. Thirteen fixture cases and an actual
isolated prepare with real dpkg passed, including a stale 3k4 package present.
This does not fetch the kernel/frozen assets or perform an installation.

## Completed checks and limits

The full profiles page includes a preview selector and three simultaneous
animated path diagrams: ICMP and UDP inside MQVPN, and TCP through the MPTCP
proxy. Gaming illustrates identical redundant TCP copies and a minrtt MQVPN
path; Performance illustrates automatic TCP scheduling and equal-weight WLB
for MQVPN. Default uses automatic TCP scheduling and minrtt MQVPN. This is a
schematic example, not sampled WAN health, packet capture or a performance
measurement. WAN-bound diagnostic pings and TCP forced into the VPN are outside
the illustration. Preview selection never applies tuning. Pause and reduced
motion are supported, and polling does not rebuild the animation's DOM.

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
- The combined VPS test run passed **572 tests and two subtests**, covering the
  new API plus existing API, NanBBR, WireGuard manager/helper, candidate preparation,
  DSCP, Xray and frozen-update checks.
  DEB modules/systemd units were compared byte-for-byte to reviewed sources.
- API transport regression cases passed, including preserving IPv6 address
  colons in the ordinary synchronization context.

Before release, run inventory T16 on a built OpenWrt image and paired installed
VPS: actual rpcd/procd permissions, daemon startup/reboot recovery, systemd timer
and CC loading, custom persistence/backup, GUI availability during switch,
credentials/routes/forwarding preservation and real traffic. Retain the earlier
failover T15 and WireGuard/native-LAN gates. Host tests do not establish throughput,
latency improvement or a complete package-upgrade path.
