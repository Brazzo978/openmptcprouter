# Tracker Fixes

This file tracks the post-review fixes applied to the `omr-tracker` logic in the `0.62` client build tree.

## Scope

These changes were applied in `/root/openmptcprouter-v0.62-build`.

The focus was on real routing / failover issues in the connection-state handling path, not cosmetic cleanup.

## Fixed

1. `mptcpovervpn` multipath role recovery in `003-up`
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/003-up`
- The script was reading the VPN-specific role into `multipath_config_route` but later using `multipath_config`.
- Fixed by writing the VPN override back into `multipath_config`.
- Impact: interfaces marked `multipathvpn=1` now recover with the correct `master/on/backup` role.

2. IPv6 default-route check in `003-up`
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/003-up`
- The IPv6 recovery branch was checking `ip route show default` before applying an IPv6 route change.
- Fixed to use `ip -6 route show default`.
- Impact: master recovery for IPv6 no longer relies on the IPv4 routing table.

3. Interface weight fallback typo in balancing helpers
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/lib/common-post-tracking.sh`
- Fixed `openmtpcprouter` -> `openmptcprouter` in both weight lookup paths.
- Impact: interface weights saved in `openmptcprouter.<if>.weight` are now actually used by the balancing route builder.

4. MTU fallback logic in `020-status`
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/020-status`
- In the branch without a specific server IP, the script measured MTU against `1.1.1.1` and then immediately retried against an empty `$serverip`.
- Fixed by applying the successful `1.1.1.1` result directly.
- Impact: automatic MTU updates no longer invalidate themselves in the no-server fallback path.

5. Empty `latency_previous` guard in `021-latencies`
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/021-latencies`
- Added a safe default for `latency_previous` before the numeric comparison used by `master=dynamic`.
- Impact: avoids shell numeric-test errors and makes the dynamic master-switch logic behave deterministically on first use.

6. Hardcoded `tun0` in `002-error` for Glorytun UDP path shutdown
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/002-error`
- Replaced the hardcoded `tun0` with the configured `glorytun-udp.vpn.dev`, with a fallback to `tun0`.
- Impact: UDP path teardown now targets the actual configured tunnel device.

7. Stale `servers` state in `omr-tracker`
- File: `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker`
- `_ping_server_all()` and `_httping_server_all()` now reset `servers=false` before recounting configured servers.
- Impact: the tracker no longer carries an old “servers exist” state across loop iterations.

8. Wrong variable in server-wide fallback checks
- File: `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker`
- The IPv4 and IPv6 fallback branches were checking `server_ping`, but this script actually uses `serverip_ping`.
- Fixed both checks.
- Impact: server-wide fallback validation now correctly detects whether any server answered.

9. Broken `_disable_current()` helper in `omr-tracker-server`
- File: `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-server`
- Fixed the function to use its argument (`serv`) instead of the undefined variable `server`.
- Impact: when switching servers, the previous `current=1` flags are now cleared on the intended sections.

10. Runtime test typo in `omr-tracker-server`
- File: `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-server`
- Fixed the malformed test `[ -n "$OMR_TRACKER_FAILURE_LATENCY"]` by restoring the missing space before `]`.
- Impact: the latency failure threshold branch now evaluates correctly instead of erroring at runtime.

11. Broken UCI batch commands for `glorytun-udp` host updates
- File: `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-server`
- Fixed two invalid batch lines that were missing `set` and committing the wrong package.
- The script now uses:
  - `set glorytun-udp.vpn.host="$ip"`
  - `commit glorytun-udp`
- Impact: server failover / recovery now updates the UDP tunnel host correctly.

12. Wrong UCI commit target in proxy helper trackers
- Files:
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-ss`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-v2ray`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-xray`
- Replaced `uci -q commit openmptcprouter.omr` with `uci -q commit openmptcprouter`.
- Impact: the proxy-health state (`up` / `down`) is now actually persisted in the right UCI package instead of silently targeting an invalid commit path.

13. Invalid delete syntax in `omr-tracker-ss`
- File: `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-ss`
- Fixed `uci -q delete openmptcprouter.omr.shadowsocks=\"\"` to a valid delete of the option itself.
- Impact: the tracker cleanly resets the cached Shadowsocks status before entering its loop.

14. Remaining helper review
- Files:
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-gre`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-ss`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-v2ray`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-xray`
- The GRE / proxy helper scripts were rechecked after the main tracker fixes.
- No extra high-impact bug was found in `omr-tracker-gre`; the concrete fixes in this pass were limited to the proxy helpers above.

15. Shell interpreter mismatch in tracker scripts
- Files:
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-server`
  - `feeds/openmptcprouter/omr-tracker/files/bin/omr-tracker-ss`
  - `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/020-status`
  - `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/022-speedtest`
- These scripts were using `#!/bin/bash`, but `omr-tracker` does not depend on the `bash` package.
- Fixed by switching them to `#!/bin/sh`.
- Impact: the tracker package no longer relies on an interpreter that may be missing on the target image.

16. Invalid `uci batch` syntax in tracker defaults migration
- File: `feeds/openmptcprouter/omr-tracker/files/etc/uci-defaults/omr-tracker`
- Two migration blocks were embedding `uci set` / `uci commit` inside a `uci -q batch` heredoc.
- Fixed by using batch-native commands:
  - `set ...`
  - `commit ...`
- Impact: legacy `shadowsocks -> proxy` migration now actually runs instead of silently failing in the defaults script.

17. Conflicting `failure_interval` default on fresh installs
- File: `feeds/openmptcprouter/omr-tracker/files/etc/uci-defaults/omr-tracker`
- One block migrated `omr-tracker.defaults.failure_interval` to `20`, but a later initialization block reset it back to `5` when `defaults.family` was unset.
- Fixed by making the later initialization block seed `failure_interval='20'` as well.
- Impact: fresh installs now keep the intended `20` second failure interval instead of reverting to the older `5` second value.

18. Removed dead ModemManager board-specific tracker code
- File: `feeds/openmptcprouter/omr-tracker/files/usr/share/omr/post-tracking.d/001-initialize`
- The script still contained board-specific USB path rewrites for `z8102ax` / `z8109ax` when `network.modem1.proto=modemmanager`.
- This is now dead code in the ethernet-only build and was removed.
- Impact: no behavior change for the current target, less legacy code in the tracker path.

19. Hotplug restart now also reacts to `ifdown` on `omrvpn`
- File: `feeds/openmptcprouter/omr-tracker/files/etc/hotplug.d/iface/40-omr-tracker`
- Previously the script only restarted the tracker for `ifup`, `ifupdate` and `iflink`.
- The hotplug gate still filters to `omrvpn`, but now any accepted action on `omrvpn` triggers the tracker restart, including `ifdown`.
- Impact: tracker state is refreshed when the main VPN interface drops, not only when it comes back.

20. IPv4-only tracker families aligned with the custom build
- Files:
  - `feeds/openmptcprouter/omr-tracker/files/etc/config/omr-tracker`
  - `feeds/openmptcprouter/omr-tracker/files/etc/uci-defaults/omr-tracker`
- The custom build forces IPv6 off, but the proxy/default tracker families still seeded `ipv4ipv6` in part of the config path.
- Fixed by aligning the effective defaults to `ipv4`.
- The defaults script now also forces `omr-tracker.defaults.family='ipv4'` and `omr-tracker.proxy.family='ipv4'` when `openmptcprouter.settings.disable_ipv6=1`.
- Impact: tracker behavior now matches the IPv4-only policy of this build instead of carrying unnecessary dual-stack defaults.

## Validation

The touched tracker scripts were rechecked with `sh -n` after patching:
- `bin/omr-tracker`
- `bin/omr-tracker-server`
- `bin/omr-tracker-gre`
- `bin/omr-tracker-ss`
- `bin/omr-tracker-v2ray`
- `bin/omr-tracker-xray`
- `common-post-tracking.sh`
- `002-error`
- `003-up`
- `020-status`
- `021-latencies`

Sanity checks were also run to confirm the corrected variable names and command paths are present.

## Notes

This file covers only the tracker-specific logic fixes.

Related documentation lives in:
- `MPTCP_GUI_FIXES.md`
- `VPN_FIXES.md`
- Corrected IPv4-only tracker defaults in both `feeds/openmptcprouter/omr-tracker/files/etc/config/omr-tracker` and `feeds/openmptcprouter/omr-tracker/files/etc/uci-defaults/omr-tracker`: `proxy.family` now defaults to `ipv4`, and the fallback seed keeps `failure_interval=20`.
