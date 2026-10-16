# Updated local-test OVA, 2026-10-16

The client was rebuilt from the pinned prior source base plus the recorded unpublished source overlay after the live VM tests. No commit, push or GitHub release was made.

Artifact: openmptcprouter-0.64.2-3K-20261016.ova
Size: 107622400 bytes.
SHA256: 0ad8a79fb48a5018f24fd302733fb667d1eb9f67f30155e57b2ea5f9e672b0b1

## Included updates

Single-page wizard; custom MPTCP Bandwidth and Monitoring; advanced diagnostic logging; removal of VPS backup UI/client commands; MQVPN 0.16.2-r4 with FEC/XOR/RSC/PKM build support and correct capability reporting; guarded NTP clock-step recovery; authenticated VPN-IP synchronization on tunnel hotplug, including explicit API-failure accounting.

All prior 3K changes remain: scheduler/congestion stack, BBRv3 default, SQM weights, PMTU display, custom speed-test hosts, Xray reverse forwarding, and WireGuard remote GUI access with LAN opt-in.

The primary router fixed_ip 10.255.220.2 is a VPS-side configuration, already tested on the current test VPS. The OVA is a factory image without VPS credentials, the test VPS address, or user forwarding rules.

## Build provenance and validation

Build root base: 29c00e70e78519e3a19bbb9286381924e30a1d11.
Feed base: c419eeae920c334ea38ede8f4d89dbf8bb20ea0d.
Source overlay SHA256: 62b73cf8b6ad00c78454c634844c2ce57a4f95755aa628acaab3800e5731f6ae.
The overlay manifest records 16 modified/new files and three explicit deletions. This is an unpublished test build, not an immutable release-commit claim.

Full make completed with exit 0. Both image and patch validators passed. Required packages, absence of banned modem/translation/bonding packages, kernel congestion configuration, BBRv3 default, scheduler objects, advanced diagnostics, exact updated UI/RPC/ACL/menu installation, MQVPN r4, world pin, NTP hook and removed backup view passed.

Fresh isolated QEMU boot: kernel 6.18.39, release v0.64.2-3K, all 18 expected congestion controls available, default bbr, mqvpn=0.16.2-r4 world pin, advanced log collector running, Monitoring RPC returns data for three interfaces, LuCI login form available. The exact installed MQVPN executable reports fec_enabled=1 via its loopback control API using a temporary QA-only client. No real VPS pairing was performed in this fresh-boot check; snapshot changes are discarded.

VMware vdiskmanager converted the staged disk to streamOptimized VMDK. qemu-img check passed and raw/canonical comparison was identical. VMware ovftool --verifyOnly passed; OVF references, hardware, manifest and archive member hashes were verified.

Hardware: vmx-13 BIOS, 2 vCPU, 2048 MiB RAM, IDE disk, E1000 LAN/WAN1/WAN2. GUI 192.168.100.1.

## Remaining operational validation

The user will test the new OVA on independent fiber and 5G WANs. MPTCP bandwidth aggregation has not yet been demonstrated on that topology. The bounded external forwarding/reconnect tests passed earlier on the live patched VM, with no observed Xray stall during those series; long-term Xray stability is a separate observation.

Stop the old router VM before pairing the replacement with the same primary VPS account.
