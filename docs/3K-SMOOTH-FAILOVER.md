# Next candidate: MQVPN session-preserving failover and VPS API paths

Source candidate developed on 2026-10-30. Published client/VPS releases are not
replaced by this branch. The complete previous feature set remains governed by
[3K-MODIFICATIONS.md](3K-MODIFICATIONS.md). The original defect analysis remains
in [3K-WAN-FAILOVER-AUDIT.md](3K-WAN-FAILOVER-AUDIT.md).

## API policy

The new `omr-api-paths` package supplies `/usr/share/omr/api-paths.sh` and is an
explicit dependency of both `openmptcprouter` and `omr-tracker`. It is not a file
that requires users to remember to install a newer tracker package separately.

Each operation first races harmless unauthenticated OMR homepage probes over
ordinary routing and eligible default, backup, subflow and signal interfaces.
All candidates start concurrently; the first HTTP 200 with the expected OMR
homepage wins. Outstanding probe processes and curl children are stopped and
private temporary files are removed. IPv6 URLs use bracketed addresses and the
same explicit interface binding as IPv4. The server tracker uses this helper
too; its ping list also includes backup/subflow/signal paths and refreshes each
cycle rather than waiting for the former 30-second cache.

The actual login/configuration operation runs once through the selected path.
We deliberately do not replicate every GET: the paired VPS `/config` handler
can generate OpenVPN certificates and update stored values. Login fields are
form-encoded; definite credential rejection does not retry every VPS address.
Expired credentials and denied permissions have distinct paths.

Only errors known to precede HTTP delivery may select another path and retry.
A lost response, including timeout after a possible upload, produces an
uncertain-delivery result rather than an automatic replay. The WireGuard caller
retains that result across its VPS-IP loop. Trusted JSON HTTP errors are preserved
for the GUI; HTML/error replies are normalized rather than treated as config.
Normal configuration readers never receive an error object as valid config.
This is not a server-side exactly-once guarantee: reconciliation must read back
state before an intentional retry. See the upstream [curl error definitions](https://curl.se/libcurl/c/libcurl-errors.html).

## MQVPN policy

Client package 0.16.2-r5 layers `030-3k-smooth-failover.patch` after the existing
native-LAN and FEC capability patches. The APK world hold follows the exact r5
package. The same source patch is retained in the VPS repository for subsequent
builds. It changes client/path/socket behavior rather than the wire protocol;
tests use a rebuilt baseline 010+020 server to exercise that compatibility.

The hold tests exercise the new script after r5 is installed. A router still
pinned to `mqvpn=0.16.2-r4` requires an explicit, verified migration of that
constraint before an APK-only upgrade can install r5. Do not present the hold
test as proof of the complete r4-to-r5 package upgrade. Full-image and APK-only
upgrade paths need their own acceptance evidence.

When a usable alternate exists, retiring the initial QUIC path no longer
unconditionally closes the whole connection. The engine retires the failed
path, promptly probes the survivor and aims to preserve the original QUIC
connection, TUN and application TCP/UDP flows. Control-socket removal and
platform/netlink loss share the policy. Whole-connection recovery remains for
an unsafe retirement or no usable alternative.

Backup sockets must be bound to their own interface: otherwise a backup can
appear validated while its packets actually follow the primary. Reconnect
selection must skip detached paths so a restored remaining WAN is usable.
Previously validated does not prove current reachability; the failover guard
must distinguish sustained missing feedback from a short loss episode.

## Evidence and remaining acceptance

The feed retains the API suites under `openmptcprouter/tests`, lab evidence in
`mqvpn/tests/smooth-failover-lab-20261030.json`, and the real-engine namespace
runner is part of patch 030 (`scripts/ci_e2e/run_3k_smooth_failover.py`). Source
and binary hashes identify the actual tested inputs; do not substitute a new
binary while retaining the old result record.

- API: 18 Bash/Dash fixture/source cases plus four real curl/HTTPS localhost
  cases passed. JSONfilter is a Python fixture, not the deployed OpenWrt binary.
- Engine: the original path-0 bug was reproduced with a real tunnel and ongoing
  TCP flow. Candidate scenarios check TCP progress, UDP replies, unchanged TUN
  ifindex and QUIC connection identity, recovery/re-add, physical-link versus
  blackhole events, backup binding and all-paths-unusable fallback. The JSON
  record is authoritative for the final scenario count, hashes and outcomes.
- Host CTest and native-LAN regressions are necessary but do not replace a
  router image test. FEC enabled in a scenario is not proof of repair efficacy.
- Blackhole-plus-control-removal scenarios model the event after a tracker has
  declared a path failed. They do not measure OpenWrt tracker detection latency.
- Linux namespaces and veth paths are controlled synthetic WANs, not physical
  fiber/5G throughput or a byte-identical execution of the published VPS DEB.

Before firmware publication: build the complete pinned candidate, verify package
selection and installed bytes, run BusyBox ash/real JSONfilter, APK index and
partial-upgrade resolution, boot/GUI/native forwarding/WireGuard gates, and
the paired two-WAN T15 matrix. A brief traffic gap is possible; no zero-loss or
zero-delay promise is made. The VPS frozen lock and installer still reference
the published 0.16.2-3k2 payload until a separately built and verified replacement
is deliberately frozen. No new firmware/VPS release is implied by these sources.
