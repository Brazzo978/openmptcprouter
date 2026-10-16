# Live fiber + 5G audit, 2026-10-16

Read-only networking checks and bounded UI/RPC fixes were performed through the private VPS-to-router MQVPN path. No WAN/network/MQVPN restart was performed. rpcd was restarted once after installing its corrected modules; MQVPN PID remained 6189.

Both WANs are up, both MPTCP endpoints are usable, and a sample of 32 MPTCP sessions had 64 subflows. Payload counters were nonzero on both fiber and 5G. This demonstrates concurrent use of both paths; a controlled throughput aggregation benchmark has not been performed.

DNS resolves through loopback and the LAN address, VPS ping passed 3/3, and HTTPS exits via the VPS. The kernel log scan found no panic, Oops, OOM or segfault. Explicit user congestion selection nanbbr3_var was retained; fresh-image default remains bbr (BBRv3).

## Corrections validated live

- Single-page Wizard now has exactly one action bar via the view addFooter override.
- Monitoring distinguishes configured, up and usable paths; per-session checks avoid falsely reporting two single-path sessions as multipath healthy.
- Active theme references the shipped loading.svg, removing a 404.
- Stopping an absent OpenVPN omr instance is guarded by the running check.
- Router and VPS upgrade prompts compare numeric versions within the same channel, avoiding stock downgrade/cross-channel proposals to 3K.

Seven browser pages (Wizard, Status, Bandwidth, Monitoring, Diagnostic logs, MQVPN Metrics, Advanced Settings) returned HTTP 200 without JavaScript exceptions or HTTP errors. Stock upgrade banner and invalid VPS update button are absent. WireGuard LAN access is available and unchecked; redirect-all-ports is unchecked.

Fixture checks: MPTCP RPC Lua 4/4, monitoring JS 6/6, OpenVPN stop mock 2/2, update comparison JS 9/9 and Lua 9/9. Source syntax/diff checks passed.

## Limits and release follow-through

XQUIC BBR2 emitted nonfatal RTT compensation warnings; the inspected branch returns without adding optional compensation and no engine patch was made. Current router has no reverse-forward rules, so earlier bounded forwarding tests are separate evidence. No permanent Xray stability claim is made.

The earlier local-test OVA predates these last fixes. The user subsequently authorized rebuilding and publishing the final 0.64.2-3K; final release artifacts must include these sources and pass image/boot/OVA verification before publication.
