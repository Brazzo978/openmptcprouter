## IPv6 Removal

This build tree now forces IPv6 off and removes IPv6 controls from the LuCI wizard/settings UI.

### What Changed

- `luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - Force `openmptcprouter.settings.disable_ipv6='1'` in wizard save path.
  - Force `openmptcprouter.settings.disable_6in4='1'` in settings save path.
  - Normalize any submitted `dhcpv6` interface config to `dhcp`.
  - Clear per-interface IPv6 fields on save:
    - `ip6addr`
    - `ip6gw`
    - `ipv6`
    - `reqaddress`
    - `reqprefix`
    - `iface_map`
    - `iface_dslite`
    - `iface_464xlate`
  - Force `dns64='0'`.
  - Clear `network.globals.ula_prefix`.

- `luci-app-openmptcprouter/luasrc/view/openmptcprouter/settings.htm`
  - Removed the visible `Enable IPv6` setting.
  - Removed the visible `Disable 6in4` setting.

- `luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`
  - Removed the dedicated IPv6 settings fieldset.
  - Removed dual-stack server IP input logic and kept only a single server IP field.
  - Removed `DHCPv6` from the protocol selector.
  - Removed per-interface IPv6 address/gateway inputs.

- `luci-app-openmptcprouter/root/etc/uci-defaults/openmptcprouter`
  - Ensure `disable_6in4='1'` is seeded by default.

### Extra Low-Risk Wizard Fixes

While touching the same controller path, two unrelated wizard bugs were corrected:

- Missing `or {}` guard on `formvaluetable(\"intf\")` to avoid nil iteration.
- Fixed interface-device handling for:
  - `ncm`
  - `qmi`
  - `modemmanager`
- Fixed delete-interface fallback so it uses `network.<if>.device` when `ifname` is empty.
- Completed first-boot IPv4-only defaults in `feeds/openmptcprouter/luci-app-openmptcprouter/root/etc/uci-defaults/openmptcprouter`: `disable_6in4=1` and `mptcpovervpn=openvpn` are now explicitly seeded when missing.

Reapplied in feed views/controllers after the first rebuild showed the GUI templates were still using legacy files. The wizard and settings pages now hide IPv6 controls again, and the controller forces IPv6, 6in4 and per-interface IPv6 settings off at save time.
