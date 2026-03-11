## Settings / Wizard Review

Remaining high-impact issues in the LuCI settings and wizard paths were checked after the IPv6 and WAN pruning changes.

### Fixed

- `luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - Added `or {}` guards to server form tables in:
    - wizard save path
    - settings-add path
  - This avoids `pairs(nil)` crashes on incomplete submits or empty server lists.

### Current State

- No other obvious high-impact settings/wizard bugs remain in the still-active paths.
- The main remaining logic in this area is now:
  - server definition
  - proxy selection
  - VPN selection
  - per-WAN ethernet/PPPoE setup
  - advanced toggles in settings

### Notes

- The tracker behavior controlled by `openmptcprouter.settings.master` still supports:
  - `balancing`
  - `change`
  - `dynamic`
  - `static`
- The selector is visible again in settings and now preserves the current value when omitted from the form.
- Corrected wizard/controller fallback for `mptcpovervpn`: OpenVPN is now the default selection when no value is set (`luasrc/controller/openmptcprouter.lua` and `luasrc/view/openmptcprouter/wizard.htm`).

After rootfs verification, the missing LuCI-side pruning patches were re-applied in the source tree. The next rebuild should now include the same UI restrictions that were already present in the backend/default scripts.
