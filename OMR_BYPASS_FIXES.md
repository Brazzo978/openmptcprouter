## OMR-ByPass Fixes

This file tracks the concrete `omr-bypass` fixes applied in the `0.62` client build tree.

### Fixed

1. Broken nft domain bypass activation
- File: `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass-nft`
- `_bypass_domain()` was enabling firewall sections using `${type}`, but `type` is not defined in that function.
- Fixed to use `${intf}`, which is the correct bypass target namespace.
- Impact: domain-based bypass rules in the nft path now enable the correct firewall sets/rules instead of writing to invalid section names.

2. Unsafe reload test in legacy and nft scripts
- Files:
  - `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass`
  - `feeds/openmptcprouter/omr-bypass/files/etc/init.d/omr-bypass-nft`
- The code used `[ -z $RELOAD ]`, which is unsafe when `RELOAD` is empty or unset.
- Fixed to `[ -z "$RELOAD" ]`.
- Impact: avoids shell test misbehavior and makes the "skip DNS resolution during reload" logic deterministic.

3. Broken firewall include guard
- File: `feeds/openmptcprouter/omr-bypass/files/etc/firewall.omr-bypass`
- The previous check used:
  - `$(pgrep -f omr-bypass 2>&1 >/dev/null)`
- Due to the redirection order, the command substitution was effectively unusable and the guard was wrong.
- Fixed to:
  - `! pgrep -f omr-bypass >/dev/null 2>&1`
- Impact: the firewall include now reloads rules only when the bypass service is not already running.

4. Broken dnsmasq migration path
- File: `feeds/openmptcprouter/omr-bypass/files/etc/uci-defaults/41_omr-bypass`
- The defaults script used `dhcp.dnsmasq[0].ipset`, which is not valid UCI list-section syntax.
- Fixed to `dhcp.@dnsmasq[0].ipset`.
- Impact: migration of older dnsmasq ipset-based bypass domains can now actually run.

### Validation

- `sh -n` passed on:
  - `etc/init.d/omr-bypass`
  - `etc/init.d/omr-bypass-nft`
  - `etc/firewall.omr-bypass`
  - `etc/uci-defaults/41_omr-bypass`
