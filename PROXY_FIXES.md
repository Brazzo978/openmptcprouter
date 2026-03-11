# Proxy Fixes

This file tracks the proxy-side review and fixes applied in the `0.62` client build tree.

## Scope

These changes were applied in `/root/openmptcprouter-v0.62-build`.

The review covered:
- Shadowsocks libev / Shadowsocks Rust
- V2Ray / XRay
- `omr-bypass`
- the VPS sync path in `openmptcprouter-vps`
- the proxy tracker helper scripts (the tracker-specific fixes are also listed in `TRACKER_FIXES.md`)

## Fixed

1. Wrong V2Ray port option lookup in VPS sync
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- Fixed `v2ray.omrout.s_vmess.port` to `v2ray.omrout.s_vmess_port`.
- Impact: the V2Ray sync logic now compares against the real UCI option instead of an invalid path.
- Before this fix, the V2Ray config refresh condition could trigger unnecessarily and rewrite / restart V2Ray when only the bad lookup was causing a mismatch.

2. Wrong XRay port option lookup in VPS sync
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- Fixed `xray.omrout.s_vmess.port` to `xray.omrout.s_vmess_port`.
- Impact: same as above, for XRay.

3. Broken validator type in V2Ray init scripts
- Files:
  - `feeds/openmptcprouter/v2ray-core/files/etc/init.d/v2ray`
  - `feeds/openmptcprouter/v2ray-core/files/etc/init.d/v2ray-nft`
- Fixed `uiterger` to `uinteger` for `s_dokodemo_door_user_level`.
- Impact: the UCI validator now uses a real numeric type instead of an invalid validator token.

4. Broken validator type in XRay init scripts
- Files:
  - `feeds/openmptcprouter/xray-core/files/etc/init.d/xray`
  - `feeds/openmptcprouter/xray-core/files/etc/init.d/xray-nft`
- Fixed `uiterger` to `uinteger` for `s_dokodemo_door_user_level`.
- Impact: same as above, for XRay.

5. `omr-bypass` per-protocol IP list import bug
- Files:
  - `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass`
  - `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass-nft`
- `_add_proto()` was loading the configured IP list into `ip=...` but iterating over `$ips`.
- Fixed by loading the list into `ips=...` and iterating over the same variable.
- Impact: protocol-specific bypass IP entries are now actually written to the nDPI / bypass tables instead of being silently skipped.

6. `omr-bypass` migration script created invalid UCI section references
- File: `feeds/openmptcprouter/omr-bypass/files/etc/uci-defaults/41_omr-bypass`
- The migration path used invalid constructs like `set omr-bypass.dpi[-1]=dpi`.
- Fixed by creating anonymous sections with `add omr-bypass <type>` and then configuring them through `@type[-1]`.
- Impact: legacy `dpi`, `ips`, and `domains` entries can now be migrated into the current anonymous-section layout instead of writing broken UCI operations.

7. Ray port forwarding with empty destination port was internally inconsistent
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- When a forwarded port did not explicitly set `dest_port`, the script built the VPS firewall comment before applying the implicit fallback to `src_dport`.
- This produced mismatched state:
  - Shorewall comment could contain an empty destination port
  - V2Ray/XRay redirect was created with the effective fallback port
- Fixed by normalizing `dest_port` to `src_dport` before all comparison / sync logic.
- Impact: Ray-based forwards that rely on the default destination port now compare, create and delete consistently.

8. Ray unredirect parsing broke on IPv6 and could mismatch on normal cleanup
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- The close-path parser handled destination extraction inconsistently:
  - IPv4 used a simplistic split
  - IPv6 did not pass `destip` / `destport` at all to `v2rayunredirect` / `xrayunredirect`
- Fixed by parsing the destination token from the firewall comment using shell expansion:
  - `destip=\"${destaddr%:*}\"`
  - `destport=\"${destaddr##*:}\"`
- This now runs for both IPv4 and IPv6 close paths.
- Impact: Ray redirects can now be removed reliably even when the target is IPv6.

9. Source IP parsing in VPS close-path was truncating IPv6 addresses
- File: `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- The close-path used `awk -F\":\" '{print $2}'`, which only kept the first segment after `net:`.
- Fixed by extracting everything after the first colon with shell expansion.
- Impact: cleanup requests now preserve the full IPv6 source filter instead of collapsing it to the first hextet.

## Review notes

1. No new high-impact bug was found in the Shadowsocks init paths during this pass.
- `shadowsocks-libev` and `shadowsocks-rust` service wrappers were rechecked for obvious UCI / process-management defects.
- The earlier tracker-side commit issues for proxy status are already covered in `TRACKER_FIXES.md`.

2. The main concrete proxy bugs found in this pass were low-level config-path and validator issues.
- These are the kinds of defects that cause silent misconfiguration, unnecessary restarts, or skipped bypass rules rather than immediate crashes.

## Validation

The touched shell scripts were checked with `sh -n` after patching:
- `feeds/openmptcprouter/openmptcprouter/files/etc/init.d/openmptcprouter-vps`
- `feeds/openmptcprouter/v2ray-core/files/etc/init.d/v2ray`
- `feeds/openmptcprouter/v2ray-core/files/etc/init.d/v2ray-nft`
- `feeds/openmptcprouter/xray-core/files/etc/init.d/xray`
- `feeds/openmptcprouter/xray-core/files/etc/init.d/xray-nft`
- `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass`
- `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass-nft`
- `feeds/openmptcprouter/omr-bypass/files/etc/uci-defaults/41_omr-bypass`

Additional sanity checks were run to confirm that:
- no `uiterger` validator typos remain
- no `s_vmess.port` typos remain

## Related documents

- `MPTCP_GUI_FIXES.md`
- `VPN_FIXES.md`
- `TRACKER_FIXES.md`
