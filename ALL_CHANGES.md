# 0.62 3KTEST Consolidated Changes

This file is the single consolidated log for the current `v0.62` 3KTEST client tree in `/root/openmptcprouter-v0.62-build`.

## Core areas patched

1. MPTCP UI + backend
- Added/normalized MPTCP controls (including `allow_join_initial_addr_port`), fixed backend variable mismatches, updated defaults (`subflows`, `add_addr_accepted`), and fixed multiple runtime script issues.
- Main files:
  - `feeds/openmptcprouter/luci-app-mptcp/...`
  - `feeds/openmptcprouter/mptcp/files/etc/init.d/mptcp`
  - `feeds/openmptcprouter/mptcp/files/etc/uci-defaults/mptcp-defaults`

2. WAN/UI scope reduction
- WAN setup limited to `static` / `dhcp` / `pppoe`.
- Removed modem-manager/QMI/NCM/other wizard paths and country preset block.
- IPv6 controls removed from UI and forced off in backend.
- Main files:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/settings.htm`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/root/etc/uci-defaults/openmptcprouter`

3. Master selection behavior
- Re-enabled master selection block and clarified behavior (`balancing`, `change`, `dynamic`, `static`).
- Backend default/fallback handling fixed.
- Main files:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/settings.htm`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`

4. Proxy/VPN/tracker/bypass reliability fixes
- Multiple sync, parser, validator, and state handling fixes across:
  - `openmptcprouter-vps` init flow
  - VPN service integration
  - `omr-tracker*`
  - `omr-bypass`
  - API helper scripts
- Main files:
  - `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
  - `feeds/openmptcprouter/omr-tracker/files/...`
  - `feeds/openmptcprouter/omr-bypass/files/...`
  - `feeds/openmptcprouter/openmptcprouter/files/bin/...`

5. Build stability fixes
- Rust/SS-rust build chain adjustments to avoid toolchain resolution failures.
- Main files:
  - `feeds/openmptcprouter/rust/Makefile`
  - `feeds/openmptcprouter/shadowsocks-rust/Makefile`

## New fixes added in this latest pass

1. Wizard proxy section regression fixed
- Restored Proxy/VPN/Encryption blocks in wizard after the previous UI prune regression.
- File:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`

2. XRay VLESS Reality disabled client-side (intentional)
- Removed `xray-vless-reality` from wizard proxy list.
- Added backend fallback so any incoming `xray-vless-reality` is normalized to `xray`.
- Added runtime normalization/filtering in `openmptcprouter-vps`:
  - force legacy `proxy=xray-vless-reality` -> `xray`
  - filter `xray-vless-reality` out of `available_proxy`
- Files:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`

3. SQM defaults changed to opt-in
- On first boot, WAN SQM is now disabled by default (`enabled='0'` for wan1/wan2/wan3/wan4).
- `omrvpn` remained disabled as before.
- File:
  - `feeds/openmptcprouter/openmptcprouter/files/etc/uci-defaults/2040-omr-sqm`

4. V2Ray/XRay UDP redirect default enabled
- First-boot defaults for transparent proxy UDP are now enabled by default.
- Files:
  - `feeds/openmptcprouter/v2ray-core/files/etc/uci-defaults/3010-omr-v2ray` (`redirect_udp='1'`)
  - `feeds/openmptcprouter/xray-core/files/etc/uci-defaults/3010-omr-xray` (`redirect_udp='1'`)

5. LuCI translations removed (English-only target)
- Build config now disables all `luci-i18n-*` packages for the next image build.
- File:
  - `x86_64/6.6/source/.config`

6. Wizard speed field description clarified
- Updated the download/upload help text to explain exactly how SQM/QoS uses those values:
  - with autorate: max `100%`, base `65%`, min `10%`
  - without autorate: shaping uses `95%`
- File:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`

7. SQM/QoS shaping ratios updated
- Updated automatic ratios as requested:
  - autorate minimum changed from `10%` to `25%`
  - non-autorate shaping changed from `95%` to `90%`
- Applied both in wizard apply logic and tracker speedtest post-processing.
- Updated wizard descriptions accordingly.
- Files:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/022-speedtest`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`

8. "Calculate speed" help text clarified
- Expanded the wizard description to explain that the test is run per-WAN against the VPS API, with multiple short download/upload probes and best result kept.
- Clarified that the saved result is then used by SQM/QoS.
- File:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`

9. Proxy selector help text rewritten
- Replaced the default proxy description with a practical overview:
  - Shadowsocks as TCP-focused best-performance/compatibility option
  - XRay/V2Ray VLESS as recommended balanced TCP+UDP option
  - VMESS/Trojan positioned as camouflage/obfuscation-focused modes
  - Kept note that only Shadowsocks supports VPS multi-IP setups
- File:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`

10. Forced XRay backend for proxy port-forward rules
- Added a new firewall advanced flag: `force_xray_pf` ("Force XRay for this port forward").
- Behavior:
  - if a rule uses `Use V2Ray/XRay` and `force_xray_pf=1`
  - and main proxy is not Ray-based
  - the client auto-enables `xray.main.enabled=1` so proxy port-forward API calls can still use XRay.
- The redirect sync logic now prefers XRay for that rule even when V2Ray is unavailable.
- Files:
  - `feeds/openmptcprouter/luci-app-firewall/htdocs/luci-static/resources/view/firewall/forwards.js`
  - `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`

## Live validation done

- On live client `5.182.48.31`:
  - removed all installed `luci-i18n-*` packages (`576` packages removed, `0` failures)
  - forced LuCI language to English (`luci.main.lang='en'`)
  - final verification: `count=0` installed `luci-i18n-*`, `lang=en`

## Detailed companion logs (kept for audit trail)

- `MPTCP_GUI_FIXES.md`
- `WAN_UI_PRUNE.md`
- `IPV6_REMOVAL.md`
- `MASTER_SELECTION.md`
- `PROXY_FIXES.md`
- `VPN_FIXES.md`
- `TRACKER_FIXES.md`
- `API_FIXES.md`
- `OMR_BYPASS_FIXES.md`
- `SETTINGS_REVIEW.md`
- `BUILD_FIXES.md`
