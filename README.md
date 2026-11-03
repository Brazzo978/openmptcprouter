# OpenMPTCProuter 0.64.3-3K

Custom 3K client release based on upstream OpenMPTCProuter **0.64.2**, frozen kernel **6.18.39** and the `0.64.2-6.18` package-feed base. This release publishes **x86_64** images and the complete compiled APK archive. ARM images remain on the separate previous ARM release until rebuilt.

- [Download client v0.64.3-3K](https://github.com/Brazzo978/openmptcprouter/releases/tag/v0.64.3-3K)
- [Paired VPS v0.1164-3K and installation command](https://github.com/Brazzo978/openmptcprouter-vps/tree/omr-vps-0.1164-3K)
- [Inventory of every 3K change and regression procedure](docs/3K-MODIFICATIONS.md)
- [Expanded clean-OVA acceptance](validation/paired-qa-r7-clean-import-20261103/README.md)
- [Build/source-freeze instructions](README-3K.md)

## Features

Six built-in profiles cover Default, Performance, Stability / Gaming, Performance (old), Stability (old), and No tunnel. The dashboard provides an A/B quick switch; both slots may use built-in or custom saved profiles. Changes coordinate router/VPS settings, validate readiness and require confirmation, with automatic rollback. The profile page includes illustrative ICMP/TCP/UDP packet-path animations.

MQVPN 0.16.2-r7 adds recovery from transient initial TUN/route setup failures and retains healthy-path recovery. The LuCI login feature probe retries bounded transient missing-object errors. The original 3K advanced diagnostics, Path live, bandwidth/monitoring views, PMTU, redacted diagnostic logs, schedulers, congestion controls and native/independent Xray forwarding are retained.

The image includes btop and speedtest tools. Modem-management packages, MLVPN and OpenVPN bonding are removed; LuCI translations other than the built-in English UI are excluded. Ordinary OpenVPN support is distinct from removed OpenVPN bonding.

## Installation and test scope

The VMware OVA uses 2 vCPU, 2 GiB RAM, BIOS/VMX-13 and three E1000 adapters in LAN/WAN1/WAN2 order. Factory LAN is `192.168.100.1`. The release also provides generated BIOS/EFI ext4/squashfs and VM disk formats; verify downloads with `SHA256SUMS-client-0.64.3-3K`.

The exact OVA passed clean import, ordinary VPS pairing, Internet/DNS, WAN-loss continuity, native and Xray forwarding, distinct-host WireGuard LAN gating and revocation, all six profiles, custom A/B management and real GUI confirmation/rollback tests. See the linked evidence for individual scopes. Existing-install upgrades, physical throughput, IPv6, ARM hardware and phone QR onboarding are not established by these virtual IPv4 tests.

On the tested VMware VMnet2 NAT path the router sent MP_CAPABLE but the VPS received plain TCP; the other WAN negotiated MPTCP correctly. This lab path limitation must not be mistaken for proof of two-path aggregation. Observed TCP failover gaps were 8.57 seconds on WAN1 and 0.23 seconds on WAN2; UDP gaps were about 0.23 seconds. No tunnel intentionally suspends tunnel-based remote GUI/LAN access and requires a unique master WAN and independent management access.

## Reproducibility

The shipped image was built from root commit `b9c7e8cedfd5ad7077c30d9c95766b66a4eb32df` with client feed `c5730aab311781467f19e4898b2ce82b77b08235`. The release source adds documentation/evidence without changing that client payload. Manifest assets retain these exact build identities.

OpenMPTCProuter, OpenWrt, MPTCP, Shadowsocks, Glorytun and the other upstream projects retain their respective attribution and licenses. Source ancestry remains documented independently from the frozen 3K release distribution.
