# Expanded clean VMware r7 acceptance — 2026-11-03

The user imported the actual factory `v0.64.3-3K` OVA, SHA-256
`60c8fa9f4020064fc852c73385cdaccdf78654a26e9075abd54b36a38ae06e1e`.
Build root is `b9c7e8cedfd5ad7077c30d9c95766b66a4eb32df`, client feed
`c5730aab311781467f19e4898b2ce82b77b08235`, MQVPN 0.16.2-r7 and kernel
6.18.39. No firmware code changed during this expanded test run.

| Evidence | Passed | Scope |
| --- | ---: | --- |
| `identity.json` | 13 | Exact new VMware import, hashes, versions, LuCI backend |
| `pairing.json` | 18 | Ordinary first pairing, native/proxy traffic, WAN leases, FEC, DNS |
| `failover.json` | 22 | Each virtual WAN lost/restored, same TCP stream and MQVPN UDP, API availability, stable tracker/endpoint readiness |
| `forwarding.json` | 17 | Native MQVPN and independent Xray public HTTP forwarding and cleanup |
| `wireguard-real-lan.json` | 28 | GUI, full IPv4 Internet, peer lifecycle, distinct Windows LAN AND-gate matrix and revocation of an existing TCP exchange |
| `profiles.json` | 46 | Six built-ins, router/VPS state, Internet/DNS, actual WireGuard GUI target changes, No tunnel direct UDP/ICMP and return to Default |
| `custom-quick.json` | 9 | Capture, A/B save without apply, transitions, deletion, restored pair |
| `gui-views.json` | 21 | Wizard/PMTU/logging/bandwidth/monitoring/FEC/preview structural checks |
| `gui-additional.json` | 9 | Loaded profile cards/options, populated logs, original Path live and kernel diagnostics |
| `gui-slider.json` | 4 | Actual dashboard clicks, explicit Revert and confirmed A/B transitions |
| `gui-timeout.json` | 4 | Actual GUI-started change automatically rolls back without confirmation |
| `final-state.json` | 7 | Confirmed Default, restored balancing, healthy WAN trackers, saved pair, no QA proxy exceptions, redirect-all disabled |

The original filesystem and clean-boot checks (57 and 16), isolated first pairing
(19) and native r6-negative/r7-positive pin-failure comparison remain in
`../first-start-r7-20261103/` and `../paired-20261103/` with their original scopes.

## Readiness and failover interpretation

The initial exploratory runner used only netifd `up` and stopped UDP when its
TCP sender timed out. Its failed observation is retained separately; it does
not establish an independent UDP outage. The revised runner leaves UDP running
after TCP failure and requires two stable snapshots of DHCP/device/address,
tracker `up` and matching MPTCP endpoint before each outage and after recovery.
It does not lower the tracker threshold: five recovery cycles at a configured
20-second failure interval produced observed endpoint-restoration waits of
97.35 and 108.95 seconds. Both phases then passed.

The same TCP socket survived, with maximum reply gaps of 8.57 seconds on WAN1
and 0.23 seconds on WAN2; UDP gaps were 0.23 seconds. MQVPN PID and TUN ifindex
stayed unchanged during these outages. These facts do not prove an unchanged
QUIC connection, two active MPTCP subflows, zero loss or aggregate throughput.
The runner's generic `ss -M -t` observation may include TCP/fallback rows and
is not evidence of MPTCP negotiation.

## Actual MPTCP handshake path limitation

`mptcp-header-correlation.json` records one bound handshake per WAN with no
application bytes. Headers were reduced to counts/capability booleans in memory;
no packets or MPTCP keys were saved. WAN1 sent MP_CAPABLE, but the VPS received
a plain TCP SYN and the client received no MP_CAPABLE SYN-ACK. The host's
VMware NAT configuration confirms VMnet2/gateway 192.168.184.2. WAN2 preserved
MP_CAPABLE in both directions and returned valid MPTCP information, remote-key
received and fallback=false. This isolates a limitation of the tested WAN1
path; it does not characterize all NAT implementations. The one-bound-socket
probe does not establish aggregation or the proxy's subflow count.

## Additional checks and cleanup

`extras/client-baseline/` records modem/bonding/translation exclusions, harmless
tool version checks, 18 available TCP controls, eight BPF scheduler packages/
objects and service boot state. It also checks the installed custom speedtest
script, host lists and tracker hook against source. SQM rates were not activated
or benchmarked; consumed first-boot scripts are distinct from missing package
payloads.

`extras/offline-regressions/` records passing UI fixtures, 12 LuCI cases, 14 Linux
VPS-preparation cases and the cached-Lua No tunnel runtime fixture. These are
isolated model tests, not additional live-device traffic tests.

`extras/log-redaction.json` records one synthetic info message and successful
password/token/Authorization redaction via the normal diagnostic RPC. No raw
logs were saved. That clearly tagged synthetic entry remains until log rotation.

`extras/vps-freeze.json` records installed versions/hashes, 21/21 package assets,
three helpers, kernel pair, admin 3k7 and health. The historical installed source
commit differs from the then-current checkout only by two client MQVPN patch
mirrors; this is retained as provenance, not rewritten to manufacture a match.

All test peers, namespaces, listeners, temporary forwarding rules, master-mode
timer and proxy exceptions were removed. Original WAN configuration, tracker
thresholds and saved A/B pair were preserved. The Windows return route was
temporary and expires independently. Final state is confirmed, unmodified
Default with VPS agreement and no pending transaction. Physical WAN throughput,
IPv6, ARM devices, mobile QR onboarding and arbitrary legacy upgrades remain
outside this acceptance scope.
