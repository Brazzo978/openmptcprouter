## WAN UI Prune

This build tree now limits WAN setup to ethernet-style links only.

### Scope

- Keep:
  - `static`
  - `dhcp`
  - `pppoe`
  - physical interface selection
  - optional VLAN tag

- Remove from the LuCI wizard/settings UI:
  - `ModemManager`
  - `NCM`
  - `QMI`
  - generic `Other` protocol
  - modem-specific fields:
    - device selectors
    - APN
    - PIN code
    - modem mode
    - modem init timeout

### Backend Changes

- `luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - Any submitted unsupported WAN protocol is normalized to `dhcp`:
    - `dhcpv6`
    - `ncm`
    - `qmi`
    - `modemmanager`
    - `mbim`
    - `ecm`
    - `other`
  - `disable_modemmanager` is forced to `1`.
  - `modemmanager` is forced to `0`.
  - The ModemManager service is stopped during settings save.

### UI Changes

- `luci-app-openmptcprouter/luasrc/view/openmptcprouter/settings.htm`
  - Removed both visible `Disable ModemManager` controls.

- `luci-app-openmptcprouter/luasrc/view/openmptcprouter/wizard.htm`
  - Removed modem protocol choices.
  - Removed `Other` protocol choice.
  - Removed the `Country settings` block.
  - Adjusted protocol descriptions to match the reduced scope.
  - Kept PPPoE authentication fields, now only shown for PPPoE.

### Result

The wizard is now aligned with an ethernet-only deployment model and no longer exposes cellular/modem setup paths.
Country-specific wizard tweaks are also disabled and `openmptcprouter.settings.country` is forced to an empty value.

Reapplied directly to the LuCI templates after verification against the built rootfs. The wizard now exposes only static, DHCP and PPPoE for WAN interfaces, removes modem-specific fields, and removes the country preset block.
