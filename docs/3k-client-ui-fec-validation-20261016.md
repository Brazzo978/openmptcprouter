# Client UI and MQVPN validation, 2026-10-16

These changes are implemented in the working trees and applied to the VMware client at 192.168.100.1 and test VPS 45.146.5.32. They have not been committed, pushed or published. The previously delivered OVA does not yet contain this new change set. Its successful historical image checks remain historical results; a replacement image must be built and checked after the new source commits are pinned.

## Implemented and checked

- Settings Wizard: Server, Settings, LAN and WAN are continuously visible on one page. Browser DOM confirmed four visible sections, zero step navigation elements and one Save & Apply. The original complete wizardadd payload remains in use. A successful request interception captured 32 fields, three interfaces and one server without applying that intercepted request. An earlier interception missed the query string and may have submitted unchanged settings; tunnel health was checked afterward.
- VPS backup: removed menu, view, ACL, client upload/restore/list functions and automatic list fetching; removed VPS Backupfile model and three API endpoints. Authenticated API tests expect 404. Local OpenWrt backup, VPS failover flag and pre-existing stored archives remain. LuCI may resolve an obsolete child URL to the first valid sibling instead of emitting HTTP 404; the deleted view and menu no longer exist.
- Bandwidth: restored refresh/window controls, WAN/total selection, separate inbound/outbound graphs, tabs, tooltips and current/average/peak values using the modern SVG renderer. Browser checked default 3/300 seconds, changed 5/120 and restored defaults; series toggle worked.
- Monitoring: restored readable health cards, WAN/kernel endpoint comparison, connection/subflow tables, changing counters and raw diagnostics. Actual UBus response and existing paths_data API were verified after fixing collector scope. Browser displays In-kernel path-manager label. Zero MPTCP sessions while the selected tunnel is MQVPN/QUIC is expected.
- FEC: client and server are compiled with XQC_ENABLE_FEC/XOR/RSC/PKM. Patch 020 includes the generated XQUIC header in the control API and tests both feature states. The live Metrics page shows FEC support ENABLED; both control APIs report fec_enabled=1. This confirms compiled capability, not an injected-loss recovery test or automatic runtime redundancy.
- Clock recovery: guarded MQVPN NTP hotplug hook restarts an enabled, running daemon only for ACTION=step. Six guard tests passed. Live step-event replay caused reconnect; periodic/stratum events did not restart it. The actual system clock was not changed during the replay test.

## Validation evidence

- VPS API, WireGuard remote access and LAN helper tests: 386 passed, 3 pre-existing deprecation warnings.
- Native Linux MQVPN CTest suite: 46 passed, zero failed.
- Official OpenWrt MQVPN APK build with both patches: exit 0.
- Client package installed as mqvpn=0.16.2-r4, world constraint updated to the same exact version, NTP hook executable. Router configuration preserved by APK conffile handling.
- VPS candidate DEB installed as 0.16.2-3k2; unchanged libmqvpn0 dependency 0.16.2-1. mqvpn and omr-admin services active.
- After the package installs and both service restarts: tunnel peer ping 3/3 replies (about 7.5 ms average), HTTPS request exits via 45.146.5.32. Earlier client-only install check passed 4/4 replies.
- Browser screenshots saved locally for Bandwidth, Monitoring and MQVPN FEC. No JavaScript execution exception observed; console contains existing password/form verbosity and a missing loading.gif resource.
- git diff --check passed in all three repositories.

## Candidate identities

Client APK SHA-256: b31ff2c3a7bf77734b995591d2e5b22fad0475430213cfc6435e3a9e1d0e0e9b
Installed official client ELF SHA-256: 66641f1ed80f1796f73d0fa87458224b7d8954c90d4bee2fb42b4de050068eb2
VPS DEB SHA-256: 6195f80b4ef2406c4df94ce7fb72ab4ae7b11206f0f6af631086d30f9a20f017
VPS ELF SHA-256: 4e9eb2d799b19f8ca27e8e675f101cc16d8e5ac3b8b291ba9e8e58222135cf6e
Patch 010 SHA-256: 416aa9768b6a774b3edb7ab7e03043fdf0fb79118d3a1bcbe1510ce7a1feae50
Patch 020 SHA-256: 530d2112b87845f624f9db79d670e84315f7634b6ba81bbbd524d97d547ce268

The VPS repacker validates both patches, generated XQUIC feature defines, source archive identity, input ELF hash, stock DEB hash, package identity and unchanged dependencies. Candidate provenance is saved beside the DEB. Existing published frozen lock/bundle is unchanged; it must not be described as containing this new candidate.

## Remaining release gates

User GUI testing, final source commits and updated feed pin, new complete image/OVA build and image checks, and a new frozen VPS bundle with the updated admin package and MQVPN candidate are pending. Revalidate the final artifact set before publication.

The previously observed intermittent Xray reverse port forwarding stall remains an independent unresolved issue; these UI/FEC tests do not establish Xray stability. An old orphan VPS listener is not an active forwarding rule on this freshly imported VM.
