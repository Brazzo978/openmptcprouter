# Backport of the LuCI RPC fix to an installed Flint 2

An installed GL-MT6000 running 0.64.2-3K uses kernel 6.18.39, ARM64 Cortex-A53,
and the same LuCI a3cc0e1 base as the 0.64.3-3K release. Its original MQVPN
package is r4. The GUI fix can be applied independently of MQVPN, the tracker,
new connection profiles, kernel modules and firmware flashing.

## Installed hotfix scope

- The compiled `luci.js` from the verified GL-MT6000 0.64.3 build. Its bytes
  outside `probeSystemFeatures()` match the installed original exactly.
- The OMR Lua footer now loads its authenticated menu only with an auth session.
- LuCI version metadata and the ucode header's literal `luci.js` resource
  revision are updated to avoid reusing a cached original script. Copying
  version.lua/version.uc alone does not update that compiled header literal.

Firmware identity remains 0.64.2-3K. No APK installation, global package upgrade,
MQVPN restart, kernel replacement or WAN/LAN configuration change was performed.
The preceding CIDR LAN hotfix was preserved. Original GUI files are backed up
on the router. This is an installed-file hotfix, not a claim that package
metadata or the complete firmware was upgraded to 0.64.3.

## Newline regression and recovery

The first manual deployment serialized the Lua footer using Windows CRLF line
endings. LuCI's installed template parser rejected that copy with an unfinished
string error at line 8 and the GUI returned a dispatch error. The four original
files were immediately restored byte-for-byte and HTTP login/authentication
were checked successfully.

The same failure was then reproduced on a temporary copy using the actual
`luci.template.parser` on the router: CRLF returned nil and the original error;
LF returned a compiled function. The corrected deployment stages all files,
requires LF, and compiles the staged Lua footer with the installed parser before
promotion. A timed rollback was armed and disarmed only after authenticated
HTTP acceptance. The resource-header change is a literal asset-version edit.

## Verification

- Twelve source-derived feature discovery tests passed using the real method
  extracted from the compiled ARM JavaScript and the original LuCI.raise code.
- Before the fix, one injected missing-object response reproduced the visible
  RPC notification in the real browser.
- After the fix, two injected missing-object replies recovered on the third
  real-backend request, with no feature RPC notification and an active login form.
  Requests unrelated to the fault target were passed to the real backend.
- Real-browser authentication loaded the authenticated menu; logout returned to
  the login page without loading that menu. HTTP authentication also returned
  200 without a template error. Tests used an isolated browser and loopback SSH
  proxy; no password was written into test scripts or reports.
- Fresh SSH and file hashes confirmed the GUI files, unchanged MQVPN process,
  preserved LAN hotfix and original firmware identity.

These tests exercise the bounded missing-object recovery and actual installed
GUI. They do not identify every possible underlying rpcd outage or claim that
permanent authorization/backend failures are hidden.

## Future manual backports

Keep Linux LF bytes during cross-platform transfers (`write_bytes` or an
explicit newline policy), compile Lua templates on the target before activation,
verify anonymous and authenticated rendering, and verify the actual served
asset URL rather than assuming package version metadata changes it. Prefer
signed target-matched APK updates when the installed package world resolves;
never mix the x86 package set into an ARM router or use a global upgrade as a
substitute for this isolated fix.
