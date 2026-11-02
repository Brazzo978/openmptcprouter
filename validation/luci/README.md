# LuCI feature discovery and login regression

After `bootstrap-3k.py materialize` and `apply-luci-startup-fix.py`, run with Node
18 or later:

```sh
node validation/luci/test_luci_features.js
python3 validation/luci/test_patch_application.py
```

`--source FILE` and `--footer FILE` select explicit reviewed sources when the
materialized checkouts are elsewhere. The twelve cases extract the actual
`probeSystemFeatures()` and `raise()` implementations. RPC/cache are fixtures
and timers are virtual. LuCI appends stack frames to `Error.message`; the
classifier must handle that real shape, not just a synthetic plain Error.

The original pinned source is a negative control with
`--baseline --source ORIGINAL-LUCI-JS --without-theme`: failures are expected.
No backend permissions, services or real credentials are changed by this suite.
The Python case exercises the real helper and GNU patch on a sparse temporary
clone: pristine source must actually change, repeat application must preserve
bytes, and drift/partial application must fail. This prevents GNU patch's
automatic reverse guessing from incorrectly reporting a patch as present.

The 2026-11-02 browser checks additionally used the built x86 candidate in a
disposable QEMU snapshot: baseline produced the reported red RPC notification
after one injected missing-object reply; patched source recovered after two
such replies and a successful third response from the real guest backend.
Wrong password was denied; authenticated menu rendered; logout returned to an
anonymous login page without a menu. These checks used live guest services with
the reviewed sources installed into that disposable snapshot. They are not a
claim that the rebuilt release image or affected testers' routers were tested.
