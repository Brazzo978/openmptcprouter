

OpenMPTCProuter API binary fixes:
- Fixed `omr-ip-intf`, `omr-ip6-intf`, and `omr-mptcp-intf` to use `exit 0` instead of invalid top-level `return` when no interface argument is provided.
- Fixed `omr-ip6-intf` server lookup path to initialize `serverip` correctly and use bracketed IPv6 HTTPS URLs when querying `/clienthost`.
- Fixed `omr-mptcp-intf` IPv6 MPTCP check path to use IPv6 bypass sets (`ss_rules6_dst_bypass_all`, `omr6_dst_bypass_all_6`) instead of incorrectly pushing IPv6 addresses into IPv4 bypass sets.
- Added IPv4-only guardrails in `openmptcprouter-api` RPC helpers so `get_ip6()` and `get_gateway6()` return empty immediately when `openmptcprouter.settings.disable_ipv6=1`, avoiding stale IPv6 status data and unnecessary ubus lookups.
- Fixed top-level guard clauses in `omr-3g`, `omr-huawei`, `omr-modemmanager`, and `omr-qmi` to use `exit 0` instead of invalid `return` when required probe data is missing.

- Fixed remaining illegal `return` guards inside `omr-qmi` LTE/UMTS parsing branches so missing signal values stop cleanly with `exit 0`.
- Fixed `omr-modemmanager` secondary access-technology probe to read from `MODEM_INFO` instead of running a bare `grep`, and corrected the `own-numbers` key typo.
- Fixed `omr-qmi` `all` output payload to return `$STATE` instead of the broken `$TATE` field.
