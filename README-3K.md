# OpenMPTCProuter v0.64.2-3K - x86_64 source build

This branch is the router-side 3K release based on Ysurac's v0.64.2 source. The server-side source, patches, package locks and installer live in the matching `Brazzo978/openmptcprouter-vps` 3K branch. The 3K feed is `Brazzo978/openmptcprouter-feeds`, branch `omr-v0.64.2-3K`.

`source-lock-3k.json` pins the upstream root base and all five nested Git checkouts: the 3K feed, OpenWrt, packages, LuCI and routing. `bootstrap-3k.py` fetches each exact commit SHA and checks its origin. It never resets, cleans or updates an existing checkout. The release root commit itself is fixed by the Git commit or tag used to check out this branch; the lock records its upstream ancestor to avoid a self-referential hash.

## Fresh checkout

Use a full clone so the root's upstream ancestor is present locally:

```sh
git clone --branch omr-v0.64.2-3K https://github.com/Brazzo978/openmptcprouter.git
cd openmptcprouter
python3 bootstrap-3k.py materialize
python3 bootstrap-3k.py verify
./run-build-3k.sh prepare
./run-build-3k.sh build
```

`prepare` applies the 3K overlays, generates OpenWrt configuration, and validates the selected packages. `build` repeats that validation and runs one strict OpenWrt make graph; pass extra make arguments after `build` if needed. `OMR_JOBS` sets parallelism from 1 to 20 (default 18). Firmware and the package manifest are written under `x86_64/6.18/source/bin/targets/x86/64/`.

A shallow clone of this 3K branch can omit the upstream base commit required for ancestry verification. Fetch full history before materialization. The source lock protects checkouts at the commit level, while source downloads, host build tools and mirrors still need the normal OpenWrt build environment.

## Existing development checkout

If a checkout already has local 3K work at the official feed base `818fa5116eefc99325e0f231e819dc51b062ef85`, `OMR3K_ALLOW_LOCAL_EDITS=yes python3 bootstrap-3k.py verify` explicitly allows that one dirty feed for development. The same override can be passed to `run-build-3k.sh`. It does not materialize a release and the output says `DEVELOPMENT ONLY`. Release builds use the published feed commit `b5f28146bc807d90c2bda0da8d83111c2bf34f71` without this override.

The client kernel 6.18.39 contains the 3K congestion controls alongside upstream BBRv3 (kernel name `bbr`). BBRv3 is the kernel, new-install UCI and GUI default; an existing explicit choice is preserved. Keep the router image and paired VPS release at their respective pinned commits when deploying them together.

## Frozen candidate and validation

The final four x86_64 images and paired VPS packages are published under https://repoomr.3klab.com/frozen3k/v0.64.2-20261013/. The release manifest records exact source commits, sizes and SHA256. `validation/` in this Git branch contains the image, BIOS/UEFI boot, BTF and HTTPS mirror reports.

The strict final firmware build completed successfully with 641 packages. The final ext4 image booted in isolated BIOS QEMU with BBRv3 selected, passed real loopback TCP transfers with all 18 controls, and registered/selected all eight BPF schedulers. NanBBR VAR applied 75 with matching readback and restored BBRv3 afterward. The final squashfs EFI image booted through OVMF with kernel 6.18.39 and default `bbr`. The GUI displayed BBRv3, the VAR slider, advanced Path diagnostics and the unchanged upstream Bandwidth page. All four published images were downloaded over HTTPS and matched their hashes.

These are functional VM checks. Real multi-WAN load/performance, the complete PC/phone WireGuard to VPS to OMR GUI path, and production VPS installation remain deployment checks. No production system was installed or rebooted.
