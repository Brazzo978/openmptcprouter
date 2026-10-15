# 3K local VMware validation - 2026-10-15

These changes are saved for the final build. No new image, GitHub tag or release was created for this validation. The previously delivered RC3 OVA does not contain these subsequent source fixes; the running test router has the live patches.

Client feed commit: f12f6d3f9c1d4a508d483b524b6d4e0e5fc805ca.
VPS source commit: ee030cffcbae5537be71c118e306e8db153575b6.
The root source lock pins the corrected feed commit and retains the exact existing upstream commits.

## Corrections

- Seed IANA KSK-2024 DS 38696 before Unbound starts. Retain existing RFC 5011 state and recognize the exact learned VALID DNSKEY. Create only missing anchor copies with daemon ownership. DNSSEC remains enabled.
- Correct the extra bracket in omr-tracker's no-bind condition that caused continuous `[: too many arguments` errors.
- Use the same DHCP gateway recovery in interfaces_only_status as in full status, so healthy WANs show the gateway and path/link MTU.
- New server configuration defaults bulk forwarding to off. Explicit opt-in remains possible. UPnP no longer implicitly enables the bulk redirect.
- Correct the VPS GET /config mapping: absent/false bulk_redirect_v4 means disable; true means enable.

## Live observations

- RC3 running in VMware, client kernel 6.18.39; VPS kernel 6.18.41-20261013.x64v3-omr-3k.
- Both DHCP WANs up; MQVPN server accepted the client and created paths for eth1 and eth2.
- Tunnel ping returned no loss, approximately 13-15 ms.
- HTTPS with normal DNS succeeds and exits with the test VPS public address.
- VPS reaches the actual router GUI over its MQVPN address (HTTP 200).
- Valid DNSSEC domain returns NOERROR/AD directly from Unbound; intentionally broken dnssec-failed.org returns SERVFAIL.
- Router DNS on its LAN address resolves successfully through dnsmasq/Unbound.
- Router UTC was two hours ahead. NTP synchronization recovered after DNS repair and corrected the offset. Historical log entries retain their original timestamps.
- No new tracker, anchor-priming or Unbound-restart errors appeared after the post-fix log marker.
- Both interface statuses return OK, gateway UP, link MTU 1500, reported path MTU 1500. MQVPN tunnel MTU is 1382.
- Router redirect_ports=0; VPS bulk_redirect_v4=false and bulk_redirect_v6=false; nftables user_dnat has no rules. GET /config reports disable after the API patch.
- WG remote LAN access gate remains deny. No disruptive WAN failover, scheduler change, external WireGuard peer or Xray forwarding test was performed in this pass.
- Router diagnostic RPC successfully retrieves authenticated VPS log entries.

## Checks

- VPS test/test_api.py: 342 passed, including all three bulk redirect state cases.
- Shell syntax and focused no-bind condition test passed.
- DNS anchor migration: nine temporary-file cases, repeated execution, ownership and unchanged learned VALID state checks passed.
- Live Lua loadfile syntax check passed before RPC installation.
- Git diff --check passed in the client feed and VPS repositories.

No secrets are stored in this report. Live file backups are kept privately on the corresponding test hosts.
