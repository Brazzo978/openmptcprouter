# MPTCP UI and Backend Changes for 0.62.1-3KTEST

This build tree includes the following MPTCP-related changes on top of upstream `v0.62`.

## UI changes

- Improved labels and descriptions in both LuCI implementations:
  - `luci-app-mptcp/luasrc/model/cbi/mptcp.lua`
  - `luci-app-mptcp/htdocs/luci-static/resources/view/mptcp/mptcp.js`
- Renamed and clarified several controls so they match actual kernel behavior on `6.6`.
- `Max subflows` is now presented as `Max additional subflows`.
- `Max additional subflows` description explicitly explains that it helps in networks that rate-limit per flow.
- `Max additional subflows` default changed from `3` to `8`.
- `Max add address` is now described as `Max accepted peer addresses`.
- `Max accepted peer addresses` default changed from `1` to `8`.
- Added `Allow joins on initial address`:
  - UCI key: `network.globals.mptcp_allow_join_initial_addr_port`
  - Default: `1`
  - Purpose: allow `MP_JOIN` on the original address/port pair.

## Follow-up fixes after image validation

- Fixed the backend typo in `feeds/openmptcprouter/mptcp/files/etc/init.d/mptcp` so `net.mptcp.allow_join_initial_addr_port` now uses the correct `mptcp_allow_join_initial_addr_port` value.
- Raised the initial seed in `feeds/openmptcprouter/mptcp/files/etc/uci-defaults/mptcp-defaults` so `mptcp_add_addr_accepted` starts at `8` on first boot, instead of relying on the later migration block to correct `1`.

## Backend fixes

- Fixed the `allow_join_initial_addr_port` runtime bug in:
  - `mptcp/files/etc/init.d/mptcp`
- The backend now writes:
  - `net.mptcp.allow_join_initial_addr_port=$mptcp_allow_join_initial_addr_port`
- Backend default for `mptcp_pm_type` is aligned to `0` (in-kernel path manager).

## Config consistency fixes

- Fixed `force_multipath` source mismatch:
  - backend now reads `network.globals.mptcp_force_multipath`
  - this matches the UI, defaults, and tracker logic
- `Initial endpoint setup` is now always visible in the UI
- `Force multipath mode` is now always visible in the UI
- These two options were previously hidden when `mptcp_pm_type=0`, even though they still affected runtime behavior

## Defaults and migrations

- `mptcp-defaults` now seeds:
  - `mptcp_add_addr_accepted=8`
  - `mptcp_allow_join_initial_addr_port=1`
- Added migration logic so existing configs get:
  - `mptcp_allow_join_initial_addr_port=1` if the key is missing

## Small UI consistency fix

- In the JS LuCI view, BPF scheduler values are normalized before being added to the dropdown:
  - `mptcp_bpf_red.o` is shown/stored as `bpf_red`
- This now matches the Lua UI behavior and the kernel runtime naming.

Additional backend fixes:
- Corrected off-state handling for interface offload toggles in `mptcp/files/etc/init.d/mptcp` so `gro`, `gso`, `lro`, `ufo`, and `tso` now apply `ethtool ... off` when set to `0` instead of incorrectly forcing `on`.
- Fixed invalid `uci -q delete network.<if>.dns=0` to `uci -q delete network.<if>.dns` so DNS cleanup for multipath-enabled interfaces actually removes the custom DNS list.

The LuCI MPTCP UI patches were also re-applied after rootfs verification. `luci-app-mptcp` now exposes `Allow joins on initial address`, keeps the initial setup and force-multipath controls visible on 6.x, normalizes BPF scheduler names in the JS view, and uses the updated labels/defaults again.
