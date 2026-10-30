# OpenMPTCProuter 3K modification inventory and regression checklist

This file is the maintained acceptance inventory for future 3K client and VPS
versions. It records the behavior that must survive a rebase, package update or
new image. A changed file or a passing build does not by itself prove runtime
behavior. Never turn a historical result into a claim about a new image.

## Baseline and scope

The audited source snapshot is client build root `eee8592aa66c1f6458ded45954dc93e65feef433`, client feed `0060b841b1130be31db8b6826d14d3d02520add6`, and VPS source branch at `954d12ff3bd40d3a705f502ecba57a0d643581b9`. The x86 client release was built from root `c9ee1c832b80f138d057c4fbb18e44c11414c5be`; the ARM batch 3 additions use `65b700cb305078e7efb577edff134850e746224e`. These are distinct build roots: inspect the artifact manifest rather than assuming the checked-out HEAD built every image.

- Client reference: `v0.64.2-3K`, upstream OMR v0.64.2, OpenWrt `c0e9507c32f5f3729b324fe27308a9a63007f6c0`, client kernel 6.18.39. The prior custom reference was v0.62.14-3K.
- Feed upstream baseline is `818fa5116eefc99325e0f231e819dc51b062ef85`. The current feed tip above contains the client behavior inventory below.
- VPS reference: `v0.1163-3K`; Debian 13 amd64/x86-64-v3, frozen kernel `6.18.41-20261013.x64v3-omr-3k`. The client and VPS kernels are deliberately different builds.
- MQVPN is based on 0.16.2, pinned client source `ee78205d3db491ca7727b974bda0c91ae1523236`, with the 3K native LAN-routing and FEC capability patches. Client release package is 0.16.2-r4; the VPS release used 0.16.2-3k2. Verify exact package provenance when changing either end.
- Paths use four repository prefixes: **B/** = build-root repository; **C/** = `openmptcprouter-feeds`; **V/** = `openmptcprouter-vps`; **Q/** = reviewed MQVPN native source. These are separate repositories/source trees; use their own release revisions, not a shared HEAD. Workspace validation evidence may live outside these repositories and must be retained with the release.
- The published baseline predates the connection profile switcher, smooth-failover candidate and multi-client WireGuard manager. Their next-branch implementations and host/contract checks are described below; complete installed-image and physical-WAN acceptance remains pending.
- Full 0.62.14 advanced-diagnostics parity is a release requirement, not yet proven by the existence of the port. Compare it with the original implementation and a real telemetry session under T08; record omissions against 3K-NET-08.

## How to use and maintain this inventory

The `omr-v0.64.2-3K-next` source candidate adds the shared API path package and
MQVPN 0.16.2-r5 smooth-failover patch. Its feed revision is pinned by this
branch's `source-lock-3k.json`. Published image/bundle identities above remain
historical. Candidate host-engine and localhost tests are separate evidence;
OpenWrt image, BusyBox ash, APK upgrade and physical-WAN acceptance must still
be recorded for a built candidate. See [candidate details](3K-SMOOTH-FAILOVER.md).

Each `3K-*` ID is stable. For a new change, add an ID with behavior, source and checks; do not recycle IDs. Update paths and the table when implementation moves. Each release must keep a separate result record with commit/tag, image or bundle SHA-256, hardware/VM model, date, operator, test IDs, results and evidence links. Save logs and sanitized reports outside this file; never commit credentials, client profiles, tokens, LAN addresses or customer logs.

Status vocabulary:

- **Source**: corresponding source exists in the audited snapshot. It does not mean the assembled image contains it or that it works.
- **Build/static**: exact artifact contains the component and static checks passed. It is not a boot or traffic test.
- **Historical runtime**: an identified prior artifact/scenario was exercised. Re-run for a changed artifact or topology.
- **Planned/unverified**: requested behavior without current end-to-end evidence. No silent pass or implied support.
- **N/A** requires a reason, target and reviewer; an unavailable test is **not run**, never pass.

For each ID, run the referenced check group in **Regression procedures** and record PASS / FAIL / NOT RUN / N/A per artifact. Review the exact source delta as well as these grouped invariants: at the audited feed tip `git diff --name-status 818fa5116eefc99325e0f231e819dc51b062ef85 0060b841b1130be31db8b6826d14d3d02520add6` lists 87 changed files. An updated comparison against the intended upstream base is required on every rebase, including new files, deleted functionality and package dependencies. A file count is coverage guidance, not a substitute for behavioral checks.

## Source, builds and package policy

| ID | Required behavior | Principal source | Checks |
|---|---|---|---|
| 3K-SRC-01 | Pin the root, OpenWrt, LuCI, routing, packages and custom feed to reviewed commits. A normal build never resets or overwrites modified feed work. | B/`source-lock-3k.json`, B/`bootstrap-3k.py`, B/`run-build-3k.sh` | T01 |
| 3K-SRC-02 | Keep the 3K image/channel identity separate from the real upstream package repository path. APK uses the resolved architecture and upstream `v0.64.2-6.18` feeds; no fictitious 3K package path. | B/`common/package/base-files/3k-apk-repositories.mk`, C/`openmptcprouter/files/etc/uci-defaults/2093-opkg` | T01, T04 |
| 3K-SRC-03 | Version/update notices recognize the 3K channel and do not propose an upstream-only replacement as the current 3K version. | C/`luci-app-openmptcprouter/htdocs/luci-static/resources/view/openmptcprouter/settings.js` | T04, T05 |
| 3K-SRC-04 | VPS installs the 21 locked OMR packages and the locked kernel/header pair from verified 3K inputs. Automatic OMR updating cannot replace the frozen payload. OS dependencies remain a separate Debian APT dependency, including the documented legacy runtime source caveat. | V/`frozen/omr-amd64.lock.json`, V/`frozen/freeze.py`, V/`cc/package-lock.json`, V/`run-vps-3k.sh` | T01, T03, T13 |
| 3K-SRC-05 | Keep normal DHCP, static IP, PPPoE, Ethernet, supported USB Ethernet and Wi-Fi WAN operation. No ModemManager, MBIM, QMI/NCM modem control or SIM/APN/operator management in the client image; the exact Qualcomm Wi-Fi kernel helper exemption is not a modem-control exemption. USB cellular/NCM and iPhone-tethering drivers are not promised by this image. | B/`validate-3k-config.sh`, C/`openmptcprouter-full/Makefile`, C/`openmptcprouter-mini/Makefile` | T02, T04, T14 |
| 3K-SRC-06 | Client omits MLVPN and OpenVPN bonding, while retaining ordinary OpenVPN. The VPS retains the frozen MLVPN package for older clients. | B/`validate-3k-config.sh`, C/`openmptcprouter-full/Makefile`, V/`frozen/README.md` | T02, T04 |
| 3K-SRC-07 | Client ships English only, Ookla `speedtest`, `speedtestcpp` and `btop` by default. ARM speedtest binaries must match target architecture and locked checksums. | B/`validate-3k-config.sh`, B/`common/package/3k-speedtest/Makefile`, B/`README-ARM-3K.md` | T02, T04 |
| 3K-SRC-08 | Preserve x86 BIOS/UEFI, ext4/squashfs and requested virtual disk/OVA outputs. VMware OVA uses the documented LAN/WAN NIC order; no credentials or test configuration in the factory image. | B/`README-3K.md`, B/`validation/rc2/client-ova-verification.json` | T04, T05 |
| 3K-SRC-09 | Preserve the reviewed ARM maintenance policy and variants in `arm-targets-3k.json`; minimum RAM 1024 MiB, Pi 3B+/4/5 retained, uncertain ZBT variants pending, BPi R2 dropped after recovery partition overflow. Historical published assets and future maintenance are different states. Recheck current selection rather than assuming a stale count. | B/`arm-targets-3k.json`, B/`hardware-inventory-3k.json`, B/`run-arm-release-3k.py` | T01, T04, T06 |
| 3K-SRC-11 | Shared VPS API helper is an explicit standalone package dependency of both consumers, including partial upgrades. Source declarations are checked; built APK install/solver acceptance is still required. | C/`omr-api-paths/Makefile`, C/`openmptcprouter/Makefile`, C/`omr-tracker/Makefile` | T02, T04, T17 |
| 3K-SRC-10 | Release queue retains provenance, fails on mismatched source/selection, records exclusions separately, and archives/removes cache only after validated evidence. A passed ARM build is not a physical-board boot. | B/`run-arm-release-3k.py`, B/`README-ARM-3K.md` | T01, T06 |

## MPTCP, congestion, SQM and traffic behavior

| ID | Required behavior | Principal source | Checks |
|---|---|---|---|
| 3K-NET-01 | BBRv3, kernel name `bbr`, is the default on a fresh router and VPS. Preserve a user's explicit existing congestion selection. | B/`6.18/target/linux/generic/hack-6.18/999-tcp_bbr-v3-update-TCP-bbr-congestion-control-module-.patch`, C/`mptcp/files/etc/uci-defaults/mptcp-defaults`, V/`cc/patches/omr/tcp-bbr-v3.patch` | T02, T07 |
| 3K-NET-02 | Preserve all 18 verified TCP controls: Reno, CUBIC, BBRv3, BBR1, BBR2, nanqinlang and 12 NanBBR variants, including BTF/kfunc/module and ARM32 math64 adaptations. TCP controls require the matching kernel ABI on client and VPS. | B/`6.18/target/linux/generic/hack-6.18/9999-tcp-custom-cc-3k.patch`, B/`6.18/target/linux/generic/hack-6.18/9999-zzz-tcp-bbr1-kfunc.patch`, V/`cc/patches/3k-tcp-custom-cc.patch` | T02, T07 |
| 3K-NET-03 | NanBBR VAR selection exposes aggression 1–100; validate input, read back the requested value and synchronize a capable VPS. New connections/subflows use new parameters; existing connections may retain prior parameters. | C/`mptcp/files/etc/init.d/mptcp`, C/`luci-app-mptcp/htdocs/luci-static/resources/view/mptcp/mptcp.js`, V/`admin/test/test_nanbbr.py` | T03, T07 |
| 3K-NET-04 | Keep eight BPF scheduler packages with target-kernel CO-RE/BTF compatibility, scheduler selection, fallback and corresponding proxy/TCP service handling. Legacy `redundant` is not a synonym blindly written to a 6.x kernel; use the actual registered BPF name. | B/`validate-3k-config.sh`, C/`mptcp/files/etc/init.d/mptcp`, C/`mptcp-bpf-red/src/mptcp_bpf_red.c` | T02, T07, T15 |
| 3K-NET-05 | WAN MPTCP scheduler weights and DSCP pins work on both configured sides where synchronization is enabled; include `bpf_weight_rr` in automatic weight synchronization. An old README reports a historical gap; the audited hook includes it, so verify behavior rather than relying on the README. | C/`mptcp-weight-manager/files/usr/share/omr/post-tracking.d/040-multipath-weight`, C/`mptcp-bpf-dscp/src/mptcp_bpf_dscp.c`, V/`admin/test/test_dscp_sync.py` | T03, T07, T15 |
| 3K-NET-06 | Fixed SQM download and upload use 90% of measured rates. Autorate maximum/base/minimum use 100%/65%/25%, separately for each direction and WAN. Preserve explicit settings and zero/unavailable measurements correctly. | C/`omr-tracker/files/usr/share/omr/post-tracking.d/022-speedtest`, C/`openmptcprouter/files/etc/uci-defaults/2040-omr-sqm` | T08 |
| 3K-NET-07 | Restore the 0.62 custom bandwidth presentation and monitoring functionality on the modern LuCI implementation. Monitoring distinguishes configured, active and usable paths and per-connection subflows; do not confuse displayed configured WANs with traffic-bearing paths. | C/`luci-app-mptcp/htdocs/luci-static/resources/view/mptcp/multipath.js`, C/`luci-app-mptcp/htdocs/luci-static/resources/view/mptcp/mptcp_monitor.js`, C/`luci-app-mptcp/root/usr/libexec/rpcd/luci.mptcp` | T05, T08 |
| 3K-NET-08 | Retain complete custom advanced MPTCP/Path Live diagnostics and per-path state, latency, errors and live updating. Broken/missing telemetry must be visibly unavailable rather than a fabricated healthy zero. | C/`luci-app-mptcp/htdocs/luci-static/resources/view/mptcp/mptcp_paths.js`, C/`luci-app-mptcp/htdocs/luci-static/resources/view/mptcp/mptcp_diagnostics.js`, C/`luci-app-mptcp/root/usr/libexec/rpcd/luci.mptcp` | T05, T08, T15 |
| 3K-NET-09 | `omr-test-speed` retains the .62 custom IPv4/IPv6 host lists, config-file preservation and fallback behavior; include both speedtest utilities. | C/`openmptcprouter/files/bin/omr-test-speed`, C/`openmptcprouter/files/etc/omr-test-speed-hosts.list`, C/`openmptcprouter/files/etc/omr-test-speed-hosts6.list` | T04, T08 |
| 3K-NET-10 | Status reports calculated path MTU and link MTU, with bounded VPS probes, cache and graceful missing/error results. Do not block the status page for long timeouts. | C/`openmptcprouter-api/files/usr/libexec/rpcd/openmptcprouter`, C/`luci-app-openmptcprouter/htdocs/luci-static/resources/view/openmptcprouter/wanstatus.js` | T05, T08 |
| 3K-NET-11 | DNS bootstrap/DNSSEC recovery and tracker shell argument handling survive a fresh image and WAN changes. Bulk `Redirects all ports from server to this router` is OFF on a fresh install and requires explicit opt-in. | C/`openmptcprouter/files/etc/uci-defaults/1940-omr-dns`, C/`openmptcprouter/files/etc/uci-defaults/1980-omr-firewall`, C/`omr-tracker/files/bin/omr-tracker` | T05, T08, T15 |
| 3K-NET-12 | Race harmless VPS probes on all eligible WANs, including backup/subflow/signal and IPv6; serialize actual operations. Distinguish auth rejection, permissions, failed delivery and uncertain delivery; do not replay a possibly applied mutation through another IP. Never interpret error/HTML as configuration. | C/`omr-api-paths/files/api-paths.sh`, C/`openmptcprouter/files/etc/init.d/openmptcprouter-vps`, C/`omr-tracker/files/bin/omr-tracker-server` | T15, T17 |

## MQVPN, forwarding and remote access

| ID | Required behavior | Principal source | Checks |
|---|---|---|---|
| 3K-VPN-01 | Retain MQVPN 0.16.2 and the reviewed client/server native LAN-prefix patch. Registration rejects conflicting prefixes; route lifetime follows the correct connected session and does not break public port forwarding. | C/`mqvpn/patches/010-omr-native-lan-routes.patch`, V/`patches/mqvpn/010-omr-native-lan-routes.patch`, V/`wg-remote-lan-route` | T03, T09, T10 |
| 3K-VPN-02 | Build FEC/XOR/RSC/PKM capability into XQUIC/MQVPN and report linked capability accurately. Compiled capability is not runtime FEC activation; runtime selection is configurable and must be tested separately. | C/`mqvpn/Makefile`, C/`mqvpn/patches/020-report-linked-fec-capability.patch`, V/`patches/mqvpn/020-report-linked-fec-capability.patch` | T02, T04, T09 |
| 3K-VPN-03 | MQVPN metrics page identifies reachability, build/FEC capability, scheduler and counters without claiming traffic is protected merely because FEC is compiled. | C/`luci-app-mqvpn/htdocs/luci-static/resources/view/services/mqvpn_metrics.js`, C/`mqvpn/files/usr/libexec/rpcd/mqvpn` | T05, T09 |
| 3K-VPN-04 | Client tracks paths/weights/DSCP through the MQVPN control plane. The published baseline can close H3 when QUIC path ID 0 is removed; the next candidate changes this behavior under 3K-VPN-11. Its host-lab continuity is demonstrated in the recorded scenarios; complete OpenWrt/physical-WAN acceptance remains pending. Causality for every tester incident is not asserted. | C/`mqvpn/files/usr/bin/mqvpn-path`, C/`omr-tracker/files/usr/share/omr/post-tracking.d/005-mqvpn-path`, C/`omr-tracker/files/usr/share/omr/post-tracking.d/006-mqvpn-weight`, C/`omr-tracker/files/usr/share/omr/post-tracking.d/007-mqvpn-dscp` | T09, T15 |
| 3K-VPN-05 | Preserve the guarded NTP time-step recovery hook and prevent ordinary NTP events from creating repeated MQVPN restarts. The exact patched MQVPN package is protected from unwanted upstream APK replacement. | C/`mqvpn/files/etc/hotplug.d/ntp/30-mqvpn-time-step`, C/`mqvpn/files/etc/uci-defaults/4103-mqvpn-world-hold` | T04, T09 |
| 3K-VPN-06 | Keep the documented single-primary-router tunnel address policy and preserve explicitly assigned/existing users. Authenticated tunnel-IP synchronization follows reconnects without silently changing or colliding with an existing assignment. | C/`mqvpn/files/etc/init.d/mqvpn`, C/`openmptcprouter/files/etc/init.d/openmptcprouter-vps`, V/`admin/omradmin.py` | T03, T09, T10 |
| 3K-VPN-07 | Separate Xray reverse bridge forwards TCP from VPS to the correct router/LAN destination. The per-rule GUI option works when another proxy or VPN is selected; UDP uses the normal VPN. Forced TCP does not support DMZ or source filters. The dedicated instance must not enable the main transparent-proxy firewall. Verify public traffic, not just listening processes. | C/`luci-app-firewall/htdocs/luci-static/resources/view/firewall/forwards.js`, C/`xray-core/files/etc/init.d/xray`, C/`openmptcprouter/files/etc/init.d/openmptcprouter-vps`, V/`admin/test/test_xray_rpf.py`, V/`admin/test/test_xray_reverse.py` | T03, T10 |
| 3K-VPN-08 | Ordinary public-port forwarding through MQVPN works with router-VPN-address DNAT then router LAN forwarding. This is distinct from direct LAN-prefix routing; toggling the WireGuard LAN gate must not break ordinary MQVPN forwarding. | V/`admin/omradmin.py`, V/`wg-remote-lan-route`, C/`openmptcprouter/files/etc/init.d/openmptcprouter-vps` | T03, T10, T11 |
| 3K-VPN-09 | A remote WireGuard PC/phone can reach the router GUI through VPS → MQVPN by default; LAN devices remain denied until explicitly enabled by the GUI/API gate, including with a full-tunnel profile. The GUI label is `Allow remote WireGuard access to LAN` in Advanced Settings. | C/`luci-app-openmptcprouter/htdocs/luci-static/resources/view/openmptcprouter/settings.js`, V/`wg-remote-lan-route`, V/`admin/test/test_wireguard_remote_access.py` | T03, T11 |
| 3K-VPN-10 | WireGuard `0.0.0.0/0` IPv4 clients can reach external DNS/HTTPS through the VPS public IPv4/NAT without granting access to OMR LAN. LAN opt-in and revocation apply to already-open flows; gate, native LAN route and ordinary forwarding remain independent. IPv6 full-tunnel behavior is not implied. | V/`wg-remote-lan-route`, V/`admin/test/test_wg_remote_lan_route.py`, V/`admin/test/test_wireguard_remote_access.py` | T03, T11 |
| 3K-VPN-11 | Candidate r5: preserve MQVPN session/TUN on initial or secondary path failure when a usable alternative remains; correctly bind startup backup sockets, skip detached reconnect choices and recover from missing survivor feedback without resetting on transient loss. Preserve native LAN/FEC and the exact package hold. Full OpenWrt/WAN acceptance remains pending. | C/`mqvpn/patches/030-3k-smooth-failover.patch`, C/`mqvpn/files/etc/uci-defaults/4103-mqvpn-world-hold`, C/`mqvpn/tests/smooth-failover-lab-20261030.json` | T09, T15, T17 |
| 3K-VPN-12 | Candidate root-only Bash manager controls existing `client-wg0` peers without restarting the interface: add/remove/disable/enable, status, explicit profile/QR export and per-client LAN grants. New clients need both individual permission and the existing global checkbox; legacy public-key identities retain prior global-gate behavior. Preserve GUI rescue, full IPv4 NAT, existing peers and separate router `wg0`. Never inherit a removed peer's grant when reusing its IP; revocation must block established LAN flows even if the ruleset file is missing but live nft rules remain. | V/`omr-wg-manager`, V/`omr_wg_manager.py`, V/`wg-remote-lan-route`, V/`docs/WIREGUARD-REMOTE-MANAGER.md`, V/`tests/results/wg-manager-netns-20261030.json` | T03, T11, T18 |

## User interface, diagnostics and backup

| ID | Required behavior | Principal source | Checks |
|---|---|---|---|
| 3K-UI-01 | Wizard is one scrollable settings page, not four tabs, with one effective Save & Apply footer. Save/add-interface flows work without duplicate buttons or lost configuration. | C/`luci-app-openmptcprouter/htdocs/luci-static/resources/view/openmptcprouter/wizard.js` | T05 |
| 3K-UI-02 | Advanced diagnostic logs aggregate router/VPS sources, support bounded retrieval, filters and support report redaction. The page has read-only permissions and no unintended Save/Apply actions; processes and private transient files are cleaned up. | C/`luci-app-openmptcprouter/htdocs/luci-static/resources/view/openmptcprouter/logs.js`, C/`openmptcprouter-api/files/usr/share/omr/diagnostic.lua`, V/`admin/test/test_diagnostic_logs.py` | T03, T05, T12 |
| 3K-UI-03 | Remove router-to-VPS backup tab, upload/restore commands and server backup endpoints. Normal local OpenWrt configuration backup remains available; removing VPS backup must not remove server failover. | C/`luci-app-openmptcprouter/root/usr/share/luci/menu.d/luci-app-openmptcprouter.json`, V/`admin/test/test_api.py` | T03, T05, T12 |
| 3K-UI-04 | Preserve relevant modern LuCI bandwidth/monitor styles, status and access ACLs, wizard/footer and advanced diagnostic page; test rendered UI and browser console, not source presence alone. | C/`luci-app-mptcp/htdocs/luci-static/resources/mptcp/css/mptcp_bandwidth.css`, C/`luci-app-mptcp/htdocs/luci-static/resources/mptcp/css/mptcp_monitor.css`, C/`luci-app-openmptcprouter/htdocs/luci-static/resources/view/openmptcprouter/wizard.js` | T04, T05 |
| 3K-UI-05 | Next candidate implements Status quick switch and Connection profiles page, Default/Performance/Gaming/custom, independent router/VPS snapshots, safe save/delete, Keep/Revert, timeout/reboot recovery, narrow RPC permissions and availability checks. Three illustrative ICMP/TCP/UDP animations share a preview-only selector, support pause/reduced motion and survive status polling; ICMP/UDP depict MQVPN traffic and TCP depicts the MPTCP proxy. Profile changes preserve WAN/LAN, credentials, forwarding and WG gate; installed-image acceptance remains pending. | C/`omr-profiles/README.md`, C/`luci-app-omr-profiles/htdocs/luci-static/resources/omr/profiles.js`, V/`admin/omr_profiles.py` | T16 |

## Regression procedures

Execute runtime/network-disruption tests in a disposable lab or during an explicitly agreed maintenance window. Record both expected behavior and observations; do not alter a customer's live WAN merely to satisfy this checklist. Run commands from their indicated repository. Paths in examples are illustrative; use reviewed artifacts and appropriate test credentials held outside this document.

### T01 — source, provenance and ARM policy

1. In B/, run `python3 bootstrap-3k.py verify` in a fully materialized matching checkout. Expect every pinned nested source to match; any local-edit override is development-only, not release evidence.
2. Inspect `source-lock-3k.json`, `arm-targets-3k.json`, the checked-out Git revision and each artifact's build-root/feed/OpenWrt commits. Verify file SHA-256s against the release manifest and cross-check the published tag/asset identities.
3. Compare changes against the selected upstream/client/VPS baselines with `git diff --name-status`; review every addition, deletion and modified overlay against a 3K ID. For VPS compare the chosen upstream ancestor explicitly; do not assume all historical branches share the same base.
4. For ARM, verify every target has a `keep`, `drop` or `pending` decision; resolve pending hardware evidence before claiming eligibility. Confirm R2 remains dropped unless explicitly reapproved. Test requested target selection and cache safety with the release runner's maintained fixture suite in a disposable environment.

### T02 — build configuration and kernel features

1. Build or prepare each intended target using the pinned sources and `OMR_TARGET=<target> ./run-build-3k.sh prepare`; this command materializes overlays and changes the build tree, so use a build workspace, never a router.
2. Expect `validate-3k-config.sh <prepared-source-dir> <target>` to pass. Check the installed package manifest independently: required scheduler/BTF tools, both speedtests, btop and ordinary OpenVPN present; modem management, MLVPN, bonding client and additional LuCI translations absent. `kmod-qcom-qmi-helpers` is allowed only for the reviewed Wi-Fi dependency.
3. Verify kernel configuration, actual registered controls and BPF objects; a config selection without successful registration is not sufficient. Verify both client and VPS defaults and explicit saved CC preservation.
4. Inspect MQVPN build flags and linked output for FEC/XOR/RSC/PKM; separately test runtime enabled and disabled states.

### T03 — automated source tests

Run the VPS Python tests in a disposable test environment with the reviewed dependencies installed; tests use mocks/fixtures but are not production maintenance commands:

```sh
cd /path/to/openmptcprouter-vps
python3 -m pytest admin/test/test_xray_rpf.py admin/test/test_xray_reverse.py \
  admin/test/test_wireguard_remote_access.py admin/test/test_wg_remote_lan_route.py \
  admin/test/test_nanbbr.py admin/test/test_dscp_sync.py \
  admin/test/test_diagnostic_logs.py admin/test/test_frozen_update.py \
  admin/test/test_frozen_independence.py admin/test/test_api.py
```

Expect zero failures and document skipped tests and missing dependencies. Also execute the client feed's `openmptcprouter-api/tests/diagnostic_logging.lua` with its documented Lua/OpenWrt dependencies, and MQVPN's applicable `ctest` cases against the exact reviewed native source/build. E2E/network namespace tests require an isolated lab; unit success does not replace them.

### T04 — image, packages and distribution

On the built, mounted image or a disposable guest, compare installed scripts, Lua/JS, configs, ACLs, init links, patch binaries and modes against the selected source. Check package manifest and APK architecture, default scheduler/CC, FEC capability, optional utilities, absence of excluded packages, local backup and absence of VPS backup. Verify all distribution artifacts, indexes, metadata and checksums; test real public download URLs where publication is part of acceptance. Do not treat a Git tag or the sum file alone as proof of matching bytes.

For feeds, verify signed APK index refresh and a safe dependency-resolution simulation in an isolated root; test kernel module ABI compatibility separately. A full package upgrade was not covered by the historical RC2 index test.

### T05 — boot and GUI

Boot the exact x86 image in BIOS and UEFI guests as applicable; verify installed version, GUI, BBRv3 and services. Validate OVA manifest/virtual disk bytes and import on the intended VMware product; a successful import is separate from guest boot. On ARM, boot each supported physical target when hardware is available, record model/revision/storage and network port mapping, and distinguish not tested from failed.

In the GUI verify single-page wizard and one Save & Apply, normal add/remove/save of WANs, status PMTU/link MTU, logs/filter/report redaction, Path Live, bandwidth/monitor pages, MQVPN metrics/FEC indicator, remote WG LAN checkbox and no VPS-backup tab. Check browser HTTP/JS errors. Confirm original local backup still exists. Verify redirect-all is OFF on a fresh configuration; preserve explicit existing opt-in on upgrade.

### T06 — ARM target and hardware acceptance

Each published image needs its own artifact manifest, file hashes, board ID/profile, package archive and exact source revisions. Before flashing, verify board revision, RAM, flash/storage variant, installation path and recovery image. Raspberry Pi 3B+ is maintained in a shared profile whose other DTBs are not automatically accepted. Do not infer ZBT RAM from NAND suffixes. BPi R2 is dropped due to an oversized recovery vs the existing partition; do not relax the guard or overwrite partition boundaries to force a build. Preserve R1's CPU-low caveat if it passes. User-directed one-final-attempt policy applies to R1/QNAP; recheck actual state rather than claiming success.

### T07 — MPTCP and congestion acceptance

Verify default `bbr` means BBRv3 on each exact kernel; inventory all 18 registered controls and eight BPF schedulers in a disposable booted guest. Exercise real loopback transfers under each supported CC and register/select each BPF scheduler. Test NanBBR VAR minimum, typical, maximum, invalid input, readback failure and previous-value preservation; verify propagation to a capable VPS. Test scheduler weights/DSCP and remote sync, including `bpf_weight_rr`. Existing connections may need reconnection before a change applies.

### T08 — user-facing measurements and SQM

Use synthetic controlled measurements and known line rates. Verify 90% fixed SQM, 100/65/25% autorate max/base/min for upload and download; check per-WAN interface binding, disabled/zero handling and no accidental overwrite of saved settings. Compare host-list files to the reviewed .62 originals; exercise reachable IPv4 and IPv6 endpoints without assuming every public test host is always available. Validate PMTU cache, DF-probe timeout and missing-data display. Compare the original .62.14 advanced diagnostics, bandwidth and monitoring views field-by-field to the 3K port: labels, IPv4/IPv6 data, units, time series, configured/operational/usable paths, per-connection subflows, errors, refresh and behavior with missing data. Record any missing feature explicitly; a visual resemblance alone does not establish 100% parity.

### T09 — MQVPN build and runtime

Inspect the installed binary's build info/metrics, not only a CMake flag: FEC compiled capability, active scheduler, counters and version must match the release. Run applicable unit tests including native client routes, scheduler, path state and reconnect; establish a real tunnel with at least two paths in an isolated lab and transfer TCP and UDP. Test FEC on/off and each advertised scheme where supported, clock-step hook behavior, VPN-IP stability and authenticated client/VPS synchronization. Do not infer throughput or seamless failover from an established handshake.

### T10 — forwarding and registration

Use a controlled TCP listener and separately verify public-port → Xray reverse bridge → LAN and public-port → MQVPN router address → router DNAT → LAN. Compare payload/hash, source/destination and expected rule counters; repeat after reconnect. Verify forced-Xray UDP takes the normal VPN path, unsupported DMZ/source-filter combinations are rejected or clearly reported, and the dedicated Xray instance does not activate main transparent-proxy rules. Separately verify direct native LAN-prefix registration, permitted destination routing, overlapping/invalid-prefix rejection and removal on disconnect. Confirm that disabling the WireGuard LAN gate does not remove the ordinary forwarding path. No GRE substitution is accepted as evidence of the native route feature.

### T11 — remote WireGuard policy

From an independent WG client, verify default router GUI TCP 80/443 access, denied LAN device access and continued denial under `AllowedIPs = 0.0.0.0/0`. Under the full IPv4 tunnel, verify external HTTPS and DNS use VPS egress; separately enable LAN and transfer a known file/hash to a LAN canary, then disable LAN and verify both new connections and an existing connection are blocked or interrupted. Repeat GUI and external Internet checks after revocation. Verify split-tunnel AllowedIPs are sufficient when that mode is used; do not infer IPv6 coverage from the IPv4 tests.

### T12 — diagnostic and backup privacy

Feed synthetic secrets and representative router/VPS events through collection, filtering and export; verify redaction, bounded storage and that read-only users cannot mutate configuration. Check rotation and reader termination/temporary-file cleanup. Test that former VPS backup endpoints are absent, while local backup/restore works in a disposable guest without removing server failover. Do not place real keys, full profiles or support logs in release metadata.

### T13 — clean VPS installation and frozen independence

Use the exact release bundle and checksum on a disposable clean Debian 13 amd64/x86-64-v3 VM snapshot. Record input SHA, installer exit code, service readiness, all 21 OMR package identities, local OMR APT provenance and rebooted kernel version. Deny upstream OMR package access for the independence check while allowing documented OS dependencies; inspect installation trace to prove origin. Exercise API authorization, FEC/native MQVPN and T10/T11 as separate tests. A successful old installation is not proof a later bundle installs.

### T14 — client network/package exclusions

Test normal wired/USB Ethernet, Wi-Fi, static/DHCP and PPPoE configurations on appropriate hardware or lab interfaces. Inspect both `defconfig` and actual installed package manifests; no modem/APN/SIM tooling or unrelated language packs should be installed. Verify ordinary OpenVPN still works, while removed bonding/MLVPN client selections are unavailable. Server-side legacy compatibility remains a separate requirement.

### T15 — two-WAN failure and recovery matrix: required, not yet accepted

The current user reports tunnel loss when either master or another WAN fails. Code inspection established one plausible mechanism: the tracker path-removal hook can reach the pinned upstream MQVPN engine's path-ID-0 branch, which closes the H3 connection. Whether this explains an observed incident depends on the actual path mapping and event timeline. Nine offline cases reproduce the reviewed current behavior, including API/server-tracker interface-selection blind spots; this is not a seamless-failover acceptance result. See [the investigation](3K-WAN-FAILOVER-AUDIT.md) and [reproducers](../validation/failover/README.md). No single root cause for all reports is asserted. Use a disposable paired router/VPS with two independently functional WANs and restore original link/routing/firewall state after each test. Record control-plane/API health separately from user data and do not print credentials.

| Case | Stimulus | Observe throughout | Required interpretation |
|---|---|---|---|
| F1 | Physical master link down, then restore | MQVPN process PID, connection/session ID, active paths, tracker events, API route/interface, public egress, GUI/DNS | Identify actual surviving path and any process/session restart; measure disruption and restored service. |
| F2 | Physical non-master down, then restore | Same as F1 | Verify path-specific removal without assuming a master event is equivalent. |
| F3 | Master carrier stays up but external traffic blackholes | Same plus detection/timeout times and route tables | Distinguish link-down handling from reachability failure. |
| F4 | Non-master carrier stays up but external traffic blackholes | Same as F3 | Prove surviving master path actually passes traffic. |
| F5 | Repeated failure/return and master role change | Restart counters, old/new session IDs, logs and path registration | Detect restart storms, stale paths and race conditions. |
| F6 | Baseline and each event with MPTCP `bpf_red` + MQVPN `minrtt` | Long-running TCP, UDP sequence/loss/jitter, QUIC path stats, VPN/proxy forwarding | MPTCP protects only its own TCP flows; do not infer UDP behavior from its scheduler. |
| F7 | Repeat with alternate reviewed scheduler combinations | Same as F6 plus DNS/API requests and per-WAN routing | Attribute behavior to scheduler, control-plane routing, tracker or VPN restart only with evidence. |

For each case capture a monotonic event timeline, packet loss and outage duration, established-vs-new connection behavior, OS route/rule changes, VPN and proxy PID/session IDs, MQVPN live paths and relevant sanitized tracker/API logs. An API failure may coexist with a healthy data tunnel; only call it causal if logs/timing and controlled reproduction prove it. Distinguish brief loss during failover from connection identity being destroyed by a process restart. Restore and verify the initial test setup.

### T16 — connection profile candidate regression gate

Implementation was authorized on 2026-10-30. The next candidate has Lua, native nixio/libuci, browser-preview and paired-model contract checks; see [profile handoff](3K-CONNECTION-PROFILES.md) and `validation/profiles/candidate-20261030.json`. Before/after each installed-image preset switch, compare the full set of 3K invariants and the user-selected WAN, LAN, tunnel credentials, per-port forwarding and WireGuard LAN-gate state. Test missing algorithms, client/VPS disagreement, tunnel restart, failed apply, timed rollback, partial API failure, last-working/default restoration and GUI accessibility. Repeat T05, T07–T11 and T15 under each supported preset. Do not label a candidate preset faster or lower-latency without a controlled workload and documented WAN topology.

### T17 — candidate control-plane and MQVPN acceptance

In the feed checkout run `python3 -m unittest discover -s openmptcprouter/tests -v` on Linux/WSL. The 22 cases include real concurrent shell workers in Bash/Dash and real curl/TLS localhost traffic; JSONfilter remains a Python fixture. Verify a fast backup wins without waiting for a dead master, all eligible modes are probed, losing probes are cleaned, auth HTTP 400 stops across VPS IPs, permission denial is preserved, and a lost POST response is not replayed. Separately build/install `omr-api-paths` and its consumers and verify actual APK dependency resolution and BusyBox ash/JSONfilter on the image.

Build the pinned MQVPN source with patches 010, 020 and 030 in order and run its complete CTest suite. In a disposable namespace lab run `scripts/ci_e2e/run_3k_smooth_failover.py` against a reviewed server, retain its JSON, and distinguish unchanged-session cases from intentional full-reconnect recovery. Include initial/secondary link loss, blackhole after tracker-style removal, returned path and reverse switchover, real backup isolation, no validated alternate, both paths previously validated then blackholed, short survivor outage, and FEC enabled. These tests complement T15; they do not assert automatic tracker detection time, physical-WAN performance or full image acceptance. Keep the previous native LAN/forwarding/WireGuard gates in the image acceptance run.

### T18 — multi-client WireGuard candidate regression gate

On isolated Linux, run V/`tests/test_omr_wg_manager.py` together with the existing V/`admin/test/test_wg_remote_lan_route.py`, then run V/`tests/run_omr_wg_netns.py --report PATH` as root. The candidate passed 65 unit/fixture checks and 41 checks using kernel WireGuard and the shipped nftables rules in namespaces. Preserve the sanitized report and source hashes. Repeat default GUI-only access, external IPv4/DNS, selective LAN permission, both gate revocations during an established flow, legacy preservation, adding a peer without interrupting another, crash recovery, IP reuse and denial while live rules remain but the disk ruleset is missing or older than the active table. A legacy export must match the registered public key and IPv4 address. Missing/unverifiable firewall state must report failure rather than a successful revocation.

Run V/`tests/test_vps_candidate_prepare.py` to reject stale packages, mismatched metadata, wrong package/version/architecture and wrong SHA-256; 13 fixture cases passed. The actual `run-vps-3k.sh prepare` also passed in an isolated source copy with real dpkg and a stale 3k4 file present, producing the recorded 3k5 digest without installation or fetching frozen assets.

Before release, rebuild the frozen VPS bundle, test a clean install and an upgrade from a real legacy configuration, boot/timer recovery, actual MQVPN/router LAN return traffic and at least two real WireGuard devices. Verify existing public port forwards and the independent router `wg0` before/after. The namespace router and Internet endpoint are synthetic; this is not proof of a production clean install, real MQVPN connectivity, IPv6 coverage or mobile onboarding. Do not edit `client-wg0` concurrently with external configuration tools.

## Historical evidence and known limits

- B/`validation/rc2/README.md` and B/`validation/rc2/` contain prior x86 image/BIOS/EFI, PMTU, APK-index and OVA-import reports. These describe RC2; later release images need their own checks.
- The `v0.64.2-3K` client release notes record an x86 final build with BIOS/UEFI VM checks, 18 TCP controls, eight schedulers, MQVPN FEC capability, and a real fiber + 5G router observation with two MPTCP subflows. They explicitly do not claim a controlled aggregate-throughput benchmark or long-term Xray stability.
- The `v0.1163-3K` VPS release notes report a clean Debian snapshot install and reboot, 67 live checks plus bundle identity, and 1042 API tests with nine skips. Its WG GUI/LAN endpoints were simulated, and the real router was not reattached after that clean install. Native MQVPN packet/route checks were separate.
- Prior direct WG → VPS → MQVPN → real LAN canary checks used a QA-only SNAT rule; retain that context and separately verify normal production LAN return routing. A successful local handshake alone is not proof of the end-to-end path.
- ARM batch 3 metadata/release notes report static checks and public downloads for R6S and BPi R64; physical-board boot and network validation were not recorded. Recheck current asset contents and last job outcome before publishing anything else.
- WAN failover, long-lived UDP/TCP continuity under path failure and master/API causality remain open under T15. The profile source implementation is complete in the next candidate; installed-image acceptance and performance measurements remain open under T16.
