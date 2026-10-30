# Offline WAN-failover audit reproductions

See [the investigation](../../docs/3K-WAN-FAILOVER-AUDIT.md) and inventory checks
T09/T15 in [3K-MODIFICATIONS.md](../../docs/3K-MODIFICATIONS.md).

These cases reproduce the **reviewed current behavior, including defects**.
All passing means the source-level observations were reproduced; it does not
mean seamless failover works. After a fix, replace the relevant known-behavior
assertions with acceptance expectations and retain before/after evidence.

Requirements: Linux/WSL, Python 3, Bash, a C11 compiler, the reviewed 3K feed and
MQVPN native source. There are no downloads or network calls. Shell operations
and xquic are mocked; real source functions are extracted without running init
scripts or starting the engine. Real UCI, services and WAN state are untouched.

```sh
OMR3K_AUDIT_FEED=/path/to/openmptcprouter-feeds \
OMR3K_AUDIT_MQVPN=/path/to/reviewed-mqvpn-source \
OMR3K_AUDIT_OUTPUT=/tmp/omr3k-offline-audit \
python3 validation/failover/reproduce.py
```

The script writes `offline-results.json` with source hashes and scope, plus
`c-reproducer-output.txt`. Default locations match the review workspace layout;
set the paths above in a different checkout. Generated evidence stays outside
the repository. Exit zero requires all nine cases to reproduce their expected
behavior. The C fixture includes five removal/error branches in one test case.

The inspected 2026-10-30 snapshot reproduced 9/9 cases. This was neither a full
QUIC-engine test nor a router/VPS traffic simulation; no packet-loss, recovery
time or application-session continuity was measured.
