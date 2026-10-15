# Native MQVPN LAN routing and remote WireGuard validation - 2026-10-15

The next client image is the final v0.64.2-3K, without an RC suffix. This report records development source and live patches on the VMware test client. No new image, tag or release was created during this validation. The previously delivered RC3 OVA predates these fixes.

## Behavior and scope

Stock MQVPN 0.16.2 supports normal OMR port forwarding through double DNAT: VPS public port to router VPN address, then router-side DNAT to the LAN target. A temporary public TCP 18080 forward returned HTTP 200 with the original stock binaries and was removed after the baseline test. Stock forwarding must not be described as generally broken.

The native patch adds routing for packets that retain their actual LAN destination when they reach the MQVPN server. The authenticated VPS control API assigns canonical private IPv4 prefixes to a user. The server requires exactly one active authenticated session for that owner, rejects overlapping owners and protected VPN ranges, and verifies LAN-source replies. The client explicitly permits only its generated LAN source prefixes. This extends MQVPN; future upstream updates must reapply and validate the isolated patch.

The WireGuard permission is a separate firewall gate. Default deny preserves router HTTP/HTTPS on its VPN address and public Internet through the VPS. Enabling LAN access requires both this gate and the destination subnet in the remote client's AllowedIPs (or 0.0.0.0/0). Native route registration remains present when the WireGuard gate is disabled, so ordinary port forwarding is independent.

Client feed source commit: c419eeae920c334ea38ede8f4d89dbf8bb20ea0d.
VPS source commit: d16b4109c2e0d09e36363e60890b7053800d94e6.
The root source lock retains the existing upstream commits and now targets final v0.64.2-3K.

## Source and build provenance

- MQVPN upstream source commit: ee78205d3db491ca7727b974bda0c91ae1523236, version 0.16.2.
- Client package release: 0.16.2-r3.
- Patch: mqvpn/patches/010-omr-native-lan-routes.patch.
- Patch SHA-256: 416aa9768b6a774b3edb7ab7e03043fdf0fb79118d3a1bcbe1510ce7a1feae50.
- Original cached source archive mqvpn-0.16.2.tar.zst SHA-256: 3864a72f92d0d1c567c2dc21030121e195883a4415aea86a48323b90e8d8d680. It includes xquic and BoringSSL source trees. Their individual Git metadata was unavailable; no dependency commit is inferred.
- Linux server binary SHA-256: 5d090b29ce51691ce190372582ab8a316abc6014a80da01dda503920de218a93.
- OpenWrt musl client binary SHA-256: aa0f4fcb4ca3416239e10d54760f5762fd9af3f99776036886505aedeec7f496.
- Candidate VPS DEB 0.16.2-3k1: 1451624 bytes, SHA-256 526d33a9201f2cfc3372917d7b9298c579e068609465a27bb0a469019f4fd1e0; verified repack succeeded without altering dependencies or the published bundle.
- Linux Release CTest: 46/46 passed, including always-active route assertions under NDEBUG.
- VPS API/helper Python suite: 391 passed.
- OpenWrt GCC 14.4.0 musl cross compilation: exit 0.

Both live binaries and the required init/API/helper files were installed with private stock backups retained on the corresponding test host. This was a live binary deployment, not installation of a newly built APK/DEB or a clean installation of a new frozen bundle. The current client package database still reports 0.16.2-r2. The final image must contain r3 and its exact world hold; the hold intentionally does not activate against the r2 package metadata.

## Real network observations

The actual VMware router uses MQVPN, two active WANs and LAN 192.168.100.0/24. The server has max_clients=64 but exactly one configured user and one active router; server tunnel address is 10.255.220.1 and this router is 10.255.220.2. Real concurrent multi-router behavior was not exercised. A real external WireGuard peer ran in an isolated network namespace on the build host with AllowedIPs 0.0.0.0/0. The test namespace was removed at completion.

- WireGuard handshake succeeded.
- Rescue GUI at router VPN IPv4 10.255.220.2 returned HTTP/HTTPS 200.
- Public HTTPS exited with the test VPS public IPv4, including with LAN permission disabled.
- DNS using 1.1.1.1 resolved successfully through the full tunnel.
- With LAN permission enabled, direct HTTP to router LAN address 192.168.100.1 returned 200 through native MQVPN.
- A controlled LAN host at 192.168.100.2:18098 returned HTTP 200. A 1 MiB payload matched SHA-256 fbbab289f7f94b25736c58be46a994c441fd02552cc6022352e3d86d2fab7c83.
- That Windows fixture uses another default gateway. An exact temporary router SNAT rule for only the fixture TCP port supplied its return path. The rule was removed afterward. Direct access to the router LAN IP required no such fixture rule. Real LAN hosts need OMR as their gateway or an equivalent return route.
- The actual LuCI checkbox was enabled and disabled with Save, exercising authenticated router RPC and VPS API.
- After disabling it, new LAN connections timed out. An already active 1 MiB slow HTTP stream stopped at 458752 bytes and timed out, proving revocation of an established connection. Rescue GUI still returned 200 and public HTTPS still exited with the VPS IP.
- Final state: lan_access=false, empty VPS wg_remote_lan_v4 set, MQVPN user prefix still registered with one active session.
- The user's separate Xray reverse TCP forward on public port 80 returned HTTP 200 with the main proxy still Shadowsocks Rust. The scheduler now retains xray.rpf and RPF-only startup does not create main transparent-proxy rules.
- No GRE workaround was deployed.

## APK repository regression

First-boot 2093-opkg regenerated ten invalid custom-version repository URLs, despite the original image containing correct feeds. The generator now maps this 3K version to upstream v0.64.2 plus the running kernel series. On kernel 6.18.39 it writes exactly five v0.64.2-6.18 flat feeds (luci, packages, base, routing, telephony) and clears the obsolete generated distfeeds list.

On the live router, the corrected generator followed by apk update succeeded without repository errors and reported 10420 distinct packages. No package upgrade was performed. The source Makefile also verifies the exact cached source archive and refuses a missing bundled BoringSSL tree instead of cloning HEAD. The archive is preserved on the build host and locally for the final source mirror. The native MQVPN package is protected in the final image with an exact mqvpn=0.16.2-r3 world constraint after the installed manifest confirms that version.

## Remaining release validation

These tests validate this feature on the current VMware router and test VPS. They do not certify a final image that has not yet been rebuilt. Build the final v0.64.2-3K image from the updated locked feed, verify the packaged native binary and defaults after first boot, test reboot/WAN failover and the required scheduler scenarios, and package the VPS native binary into a new candidate frozen bundle before any release. Keep the existing published VPS bundle unchanged.

Test-only router SNAT, Windows HTTP canary process, external WireGuard namespace and browser session were removed/closed. No credentials or private WireGuard keys are included in this report.
