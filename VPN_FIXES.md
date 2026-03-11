# VPN Fixes

This file tracks the VPN-side fixes applied in the `0.62` client build tree after the initial stable image set.

## Scope

These changes were applied in `/root/openmptcprouter-v0.62-build`.

They intentionally do **not** change the existing Glorytun TCP behavior that can cause an extra restart during VPS sync, because that was accepted as non-blocking.

## Fixed

1. `glorytun-udp` VPS sync section lookup
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- Fixed the section check from `glorytun.udp` to `glorytun-udp.vpn` so the UDP tunnel now receives key/port/chacha updates from the VPS.

2. OpenVPN fallback port during VPS sync
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- Corrected the fallback OpenVPN port from `65001` to `65301` in both client-key and static-key update paths.

## Follow-up fixes after image validation

- Restored `reload_service()` in `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps` so a config reload executes the same sync path as a manual service start.
- Re-enabled the full `procd_add_reload_trigger` set for `openmptcprouter`, `network`, `openvpn`, and the proxy/VPN services, so scheduler and congestion-control changes propagate automatically after saving settings.

3. `dsvpn` enable-state sync stability
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- Reloads the selected VPN mode before computing `dsvpn_state`, so `dsvpn` is not disabled due to a stale shell variable.

4. `mlvpn` loss tolerance naming mismatch
- Files:
  - `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
  - `feeds/openmptcprouter/mlvpn/files/etc/init.d/mlvpn`
- The runtime and VPS sync code now prefer `loss_tolerance` and fall back to the legacy typo `loss_tolerence` for compatibility.
- This keeps old configs readable while making new configs consistent.

5. Glorytun watchdog accuracy
- File: `feeds/openmptcprouter/omr-schedule/files/usr/share/omr/schedule.d/010-services`
- Fixed the `glorytun-udp` typo `glorytun-usp.vpn.enable`.
- Switched process detection to `pgrep -x` so `glorytun` and `glorytun-udp` do not match each other by substring.

6. Default VPN coherence on first boot
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/uci-defaults/2020-omr-vpn`
- Aligned the default setting with the already-enabled tunnel:
  - default VPN is now `glorytun_tcp`
  - `glorytun` starts enabled
  - `glorytun-udp` starts disabled
- This removes the previous mismatch where the setting said `openvpn` while Glorytun was enabled.

7. OpenVPN migration cleanup
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/uci-defaults/2020-omr-vpn`
- Fixed the invalid UCI delete command for `openvpn.omr.ncp_disable`.

8. `dsvpn` port consistency
- File: `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
- The wizard now writes the same `dsvpn` port used by the defaults and API (`65011`), instead of the inconsistent `65401`.

9. `mptcpovervpn` default consistency
- Files:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`
- The UI/controller default now matches the service fallback: `openvpn` is selected when the setting is unset.

10. Narrow UCI commits in VPN init scripts
- Files:
  - `feeds/openmptcprouter/mlvpn/files/etc/init.d/mlvpn`
  - `feeds/openmptcprouter/glorytun-udp/init`
  - `feeds/openmptcprouter/dsvpn/files/init`
- Replaced bare `uci commit` with `uci commit network` in the VPN startup path.
- This avoids committing unrelated staged config changes during a tunnel restart.

11. Safer temporary key files
- Files:
  - `feeds/openmptcprouter/glorytun/init`
  - `feeds/openmptcprouter/glorytun-udp/init`
  - `feeds/openmptcprouter/dsvpn/files/init`
- Added `chmod 0600` after writing temporary key files in `/tmp`.

12. OpenVPN bonding removed from the client flow
- Files:
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - `feeds/openmptcprouter/luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`
  - `feeds/openmptcprouter/openmptcprouter-api/files/usr/libexec/rpcd/openmptcprouter`
  - `feeds/openmptcprouter/openmptcprouter/files/etc/uci-defaults/2020-omr-vpn`
  - `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openvpnbonding`
- Removed `openvpn_bonding` from the wizard and from the global restart paths.
- Added a migration that converts legacy `openvpn_bonding` selections to standard `openvpn` and restores `network.omrvpn` to `tun0` / `dhcp`.
- The `openvpnbonding` init script now acts as a migration-and-disable path only; it no longer builds the bonding interface.
- Impact: OpenVPN bonding is no longer selectable or activated in the new client release.

## Validation

The touched shell scripts were checked with `sh -n` after the patch set:
- `openmptcprouter-vps`
- `2020-omr-vpn`
- `openvpnbonding`
- `glorytun`
- `glorytun-udp`
- `mlvpn`
- `dsvpn`
- `010-services`

## Deferred on purpose

1. Glorytun TCP can still restart unnecessarily during some VPS syncs.
- This comes from the existing Glorytun change-detection condition in `openmptcprouter-vps`.
- It was left unchanged because the extra restart was accepted as non-blocking.
- Corrected first-boot VPN defaults in `feeds/openmptcprouter/openmptcprouter/files/etc/uci-defaults/2020-omr-vpn`: default VPN is now `glorytun_tcp`, with `glorytun` enabled and `glorytun-udp` disabled by default.
