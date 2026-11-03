# Paired VMware candidate acceptance, 2026-11-03

Build source: `21e416687c9b549d9f4fc8701c6a24f430f50614`.
Client feed: `04a25941f4dd39c1371feb4ebd05bda800042091`.
Paired clean-installed/rebooted VPS: admin `0.18+20261030-3k7`, frozen
kernel `6.18.41-20261013.x64v3-omr-3k`. Its source branch subsequently adds
the mirrored MQVPN recovery patch for maintenance; its deployed server
MQVPN binary remains unchanged.

The test router started from the 2026-11-02 API-fix OVA. Corrections were first
verified as staged source files, then the signed candidate APKs were installed
offline: MQVPN 0.16.2-r6, omr-profiles 1-r4, tracker 2.0-r3 and dashboard
26.307.40508~04a2594. The exact runtime file checks and the stripped binary
extracted from that signed APK are recorded in `installed-packages.json`.

| Evidence | Passed | Scope |
| --- | ---: | --- |
| `installed-packages.json` | 23 | Installed files, versions, preserved profile state, r6 hold, compiled FEC, live peer traffic |
| `failover-r6.json` | 20 | Each virtual WAN interrupted separately; existing TCP/MPTCP session and MQVPN UDP progressed; API discovery, restoration and cleanup |
| `forwarding-r6.json` | 17 | Native MQVPN and independent Xray HTTP forwarding from another host; distinct backend rules; public ports and owned sections removed |
| `wireguard-r6.json` | 13 | GUI rescue, full IPv4 tunnel/VPS egress, peer lifecycle and cleanup with actual r6 client |
| `wireguard-real-lan.json` | 28 | Earlier complete distinct-host LAN global/peer AND gate, GUI continuity and revocation of an existing TCP exchange |

The four LAN combinations deny access except global=allow AND peer=allow.
The Windows LAN canary had another ordinary gateway, so temporary return
routes were required on that test host. No Windows firewall rule was changed.
Test peers, namespaces, listeners and temporary forwarding rules were removed;
the initial LAN gate and existing peers were preserved.

During actual r6 WAN1 loss, the maximum observed TCP reply gap was 8.67 seconds;
WAN2 was 0.22 seconds. UDP gaps were 0.22 seconds for each. The existing TCP
socket survived. MQVPN PID and TUN ifindex stayed unchanged; those identities
alone do not establish an unchanged QUIC connection. Two independently routed
virtual WANs are not a physical fiber/5G throughput benchmark.

Additional recorded installed tests cover all six built-ins, explicit rollback,
automatic confirmation timeout through the dashboard slider, custom capture and
A/B management (9 checks), actual Glorytun TCP Internet traffic and No tunnel
master-only UDP/ICMP with TCP proxy egress. The final APKs also repeated
Performance (old) traffic and return to Default. The router was left on Default,
with the saved A/B pair unchanged and no pending transaction.

See [the findings and corrections](../../docs/3K-PROFILE-INSTALLED-QA-20261103.md).
Fresh final-image boot, VMware packaging and hashes are separate artifact
evidence. These files do not assert mobile QR onboarding, IPv6, zero-loss
failover or a legacy-install upgrade.
