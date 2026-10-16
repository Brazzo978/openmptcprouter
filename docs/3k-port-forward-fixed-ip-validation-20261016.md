# Port-forwarding and fixed MQVPN IP validation, 2026-10-16

The user configured VPS TCP/80 using forced Xray reverse forwarding and TCP/8080 using MQVPN, both targeting router 192.168.100.1:80.

## Findings and changes

Initially public TCP/80 reached the router, while TCP/8080 timed out. The router had reconnected as 10.255.220.2 after the VPS MQVPN restart, but the VPS DNAT and LAN route still referenced the prior dynamic address 10.255.220.3.

The omrvpn iface hotplug event did run; its public set_vpn_ip command lacked servername, API address/port and token context. Logs showed 'No credentials for server  yet'. The normal full service initialized this context, while hotplug and the RPC backend-switch polling path did not.

The corrected public command chooses one enabled, configured active VPS (current before master, unambiguous non-backup fallback), requires an IPv4 address on the actual VPN interface, initializes per-server API context, and fetches authenticated configuration before synchronization. Ambiguous configurations, down tunnels and read-only users do not write. Actual POST failures no longer count as success; alternate API addresses can be tried.

The user clarified that this deployment uses one router at a time. The primary MQVPN user is now pinned to 10.255.220.2; the server remains 10.255.220.1. This uses the existing per-user fixed_ip capability, with no new MQVPN C patch. The source VPS template and installer upgrade merge include this default, preserve existing explicit assignments and keys, and avoid taking another user's already fixed address.

## Results

- Corrected synchronization immediately changed TCP/8080 DNAT and the VPS LAN route to 10.255.220.2; public access then succeeded.
- External request series: 12/12 plus 10/10 HTTP root-page responses on each port, all HTTP 200 with the same 664-byte router index and identical body hash.
- Both /cgi-bin/luci/ URLs return the actual LuCI login form. LuCI's unauthenticated login response uses HTTP 403; form fields and login button were verified, so this is not a tunnel denial.
- VPS socket TCP/80 belongs to Xray. The rule is explicitly marked Xray reverse forwarding.
- TCP/8080 has nft DNAT to 10.255.220.2 and router-side DNAT to 192.168.100.1:80. tcpdump observed incoming external-client TCP/8080 packets on router tun0, and the corresponding rule counters increased.
- After pinning the address: one VPS MQVPN service restart and two client MQVPN service restarts retained 10.255.220.2 with peer 10.255.220.1; public forwarding recovered.
- A replay of the omrvpn ifupdate hook through sh exited 0 with the initialized API context. Hotplug files are sourced by the hotplug dispatcher; direct executable invocation is not the correct replay mechanism.
- Isolated BusyBox regression checks: 12/12 wrapper selection/guard/retry scenarios, plus 4/4 actual private POST-result scenarios.
- Isolated installer jq checks: 6/6 fresh/upgrade/explicit-IP/conflict/key-preservation fixtures.
- Final VPS services mqvpn, xray and omr-admin active. DNAT and LAN route both point at .2.
- git diff --check passed.

No Xray stall occurred in these request series. This is a successful bounded functional/reconnect test, not proof that the previously observed intermittent Xray stall can never recur.

Live and source changes are saved for the next final build. They are not committed or pushed, and the previously delivered OVA and published frozen VPS bundle have not been replaced by these changes. The live private configuration backup is under /root/3k-liveqa-20261016; no credentials are included in this report.
