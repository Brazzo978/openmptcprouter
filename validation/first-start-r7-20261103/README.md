# MQVPN r7 first-start correction and acceptance

Factory build root: `b9c7e8cedfd5ad7077c30d9c95766b66a4eb32df`.
Client feed: `c5730aab311781467f19e4898b2ce82b77b08235`.
Version remains the local `v0.64.3-3K` candidate, based on upstream 0.64.2
and the frozen kernel 6.18 series. Documentation commits after that root
do not change the built artifact's provenance.

The clean r6 VMware import is retained as an expected negative result in
`../paired-20261103/first-start-r6-negative.json`. It failed to recover after
the first server-route pin error despite WAN recovery. Do not present its
earlier filesystem, boot or paired-package checks as first-start acceptance.

MQVPN 0.16.2-r7 adds patch 050. See
[the investigation](../../docs/3K-MQVPN-FIRST-START-20261103.md) and the native
fault-injection comparison in `../paired-20261103/initial-tun-native-r7.json`.
The deployed VPS MQVPN server binary is unchanged; the source patch is mirrored
for maintenance and introduces no server protocol or public library ABI change.

| Evidence | Passed | Scope |
| --- | ---: | --- |
| `installed-package.json` | 11 | Signed APK payload equals actual VMware binary, r7 hold, FEC, both WANs, TUN/peer traffic, LAN and profile state |
| `failover.json` | 20 | Separate WAN interruptions, existing TCP and MQVPN UDP progress, API calls, restoration and cleanup |
| `forwarding.json` | 17 | Native MQVPN and independent Xray HTTP forwarding, distinct rules and cleanup |
| `wireguard.json` | 13 | GUI rescue, full IPv4 tunnel with VPS Internet egress, peer lifecycle and cleanup |
| `image-verification.json` | 57 | Exact built filesystem, manifest, patches, preserved features and pinned package versions |
| `rebuilt-boot-verification.json` | 16 | Factory snapshot boot, live LuCI backend, runtime package/binary identity and defaults |
| `cold-pair.json` | 19 | First ordinary wizard pairing on the exact image, TUN, DNS, peer traffic, HTTPS VPS egress and safe actual-router restoration |

The cold-pair run had no startup route errors. It proves a normal first pairing;
the separate native fault-injection test proves recovery from the original
pin-error path. Only one client used VPS user 0 at a time. The isolated guest
was proven stopped before restoring the actual router's executable mode and
service. The router was rechecked through a fresh SSH connection before the
rollback was disarmed. The independent timers are best effort and cannot
guarantee ordering during a host/watchdog failure.

`build-provenance.json` retains the original build source and raw image hashes.
`canonical-verification.json` records identical VMDK disk contents after VMware
conversion. `ova-verification.json` records the local-test artifact identity,
OVF validation and the raw image hash remaining unchanged after cold pairing.
No VPS credentials or QA configuration are embedded in that factory image.

The replacement VMware OVA is 107591680 bytes (102.6 MiB), SHA-256
`60c8fa9f4020064fc852c73385cdaccdf78654a26e9075abd54b36a38ae06e1e`.

The actual VMware router was returned to confirmed Default, with no pending
profile transaction and its saved A/B pair preserved. A signed APK restart
activates r7; this is separate from the same-process recovery demonstrated by
native fault injection. During r7 WAN1 loss the maximum observed TCP reply gap
was 8.68 seconds; MQVPN UDP was 0.21 seconds. During WAN2 loss both were 0.21
seconds. The TCP socket survived. PID/TUN identity alone does not prove an
unchanged QUIC connection. These virtual WANs do not measure physical fiber/5G
aggregate throughput or establish zero-loss failover.

The earlier distinct Windows-host WireGuard LAN global/peer AND gate is
recorded separately in `../paired-20261103/wireguard-real-lan.json` (28 checks).
It was not repeated by these thirteen r7 GUI/full-tunnel checks. Test peers,
namespaces, listeners and temporary forwarding rules were removed.

All previous 3K source modifications are retained. Mobile QR onboarding,
IPv6 and upgrading an arbitrary legacy installation remain outside this
acceptance scope. Public release assets are unchanged.

## Actual clean VMware import after local handoff

The user imported the replacement OVA as a new VMware VM. Thirteen read-only
identity checks passed before trusting its new SSH key. Both factory-empty WANs
obtained DHCP leases with a timed rollback; fresh SSH and both leases were
verified before disarming it. VPS user 0 was free before the ordinary wizard
paired this router. Eighteen traffic/runtime checks passed. MQVPN's observed
PID stayed unchanged throughout that first-pairing observation, with no manual
restart and no logged initial server-route failure.

An unqualified TCP `curl --interface tun0` probe initially timed out: the live
SS NAT OUTPUT chain redirected it to local port 1100. Header-only capture showed
SYNs to `127.0.0.1:1100` on tun0, so it was not testing native Internet TCP over
MQVPN. The dedicated native TCP check used an automatically removed NAT-output
exception for one resolved public test endpoint. Its counter increased and
HTTPS passed with local source `10.255.220.2` and public egress matching the VPS.
This is a QA correction, not a firmware change or a production proxy exception.

| Additional evidence | Passed | Scope |
| --- | ---: | --- |
| `vmware-r7-identity.json` | 13 | Actual clean OVA identity, packages, exact runtime hashes, LuCI backend |
| `vmware-r7-pairing.json` | 18 | Ordinary first pairing, peer/public ICMP, UDP DNS, proxy TCP, FEC, WANs and runtime |
| `vmware-native-mq-tcp.json` | 4 | Native HTTPS with endpoint-only proxy exception, bound MQ source, rule hit and cleanup |
| `vmware-final-state.json` | 4 | Normal Default apply/confirm, ordinary transparent TCP egress, no remaining QA exceptions, redirect-all disabled |

After the first-pairing observation, Default was applied and confirmed through
the normal profile API. This ordinary profile transition may restart services;
it is separate from the first-pairing same-process observation above. Final
state is Default, unmodified, matching the VPS and without a pending transaction.
