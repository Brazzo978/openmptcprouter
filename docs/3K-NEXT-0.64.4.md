# Planned v0.64.4-3K client corrections

This is a future-build checklist, not a published v0.64.4 image.

- Include feed commit `0d63c4711f155f1ce1ffbb0710f166b1946095d8`:
  preserve an existing IPv4 CIDR suffix when collecting LAN addresses instead
  of appending a retained UCI netmask. Keep multi-address collection, exact
  LAN-zone membership and the associated regression tests. The source package
  revision is `openmptcprouter 0.95-r5`.
- Preserve every previous 3K change and pair the build with the current VPS.
- Verify a LAN subnet change with a retained separate netmask, including
  removal of obsolete main/WireGuard policy routes and MQVPN LAN grants.
- Verify normal RTH GUI rescue with LAN denied and explicit per-peer/global
  LAN access with suitable client routes.

The v0.1164-3K VPS API 3k9 supplies backward compatibility for the specific
legacy `IPv4/prefix/retained-mask` payload. Existing v0.64.3 clients therefore
need no rebuild for that reported case. This does not put the definitive
collector correction into old images or repair malformed JSON/omitted client
addresses. The client-side correction remains required in the next build.
