# Single wizard footer fix, 2026-10-16

The single-page wizard appended a custom Save & Apply bar inside its map. LuCI then appended the standard Save & Apply / Save / Reset bar outside the map. The old delayed cleanup only searched inside the map and could not remove that footer.

The view now overrides the documented addFooter hook with an empty fragment. The custom atomic wizardadd save button and its pending-request disabling behavior remain. Removed the ineffective DOM cleanup and timer.

Applied to the user's router over the private MQVPN path through the VPS; no new public SSH port was opened. Saved original wizard privately on the router before replacing the minified file. No network configuration was submitted during verification.

Browser check before: two cbi-page-actions bars. After clearing the versioned module cache: exactly one bar, text Save & Apply, all Server / Settings / LAN / WAN headings present. Node syntax check passed. Installed minified JS SHA256 e6095a5520020ac6ee7782e4292b00460b3025df66f95f567378184c66ada8cd.

Source saved locally and on the build host for the final rebuild. The delivered 20261016 OVA predates this correction and has not been replaced in this step. No commit, push or release.
