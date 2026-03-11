## Master Selection

The legacy `Master interface selection` control has been re-enabled in the settings page.

### Runtime Behavior

- `balancing`
  - Default behavior for this build.
  - Uses all healthy WANs and rebuilds balanced routes when links fail or recover.

- `change`
  - The tracker can promote another WAN to `master` when its latency is clearly better than the current master.
  - This is the old "wizard change" behavior.

- `dynamic`
  - Similar to `change`, but more conservative.
  - It requires a larger and stable latency improvement before switching.

- `static`
  - Keeps the current master fixed.
  - Only a hard failure triggers fallback routing.

### Backend Note

- `luci-app-openmptcprouter/luasrc/controller/openmptcprouter.lua`
  - Saving the settings page now keeps the existing value if the form field is absent.
  - Fallback default is `balancing`, not `static`.
  - Server form tables are also guarded with `or {}` to avoid nil iteration on incomplete submits.

The master selection block is now uncommented in `settings.htm` and rendered again in the GUI, with an inline description of the behavior of `balancing`, `change`, `dynamic`, and `static`.
