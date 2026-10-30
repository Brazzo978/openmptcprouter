# OpenMPTCProuter v0.64.2-3K - x86_64 source build

This `omr-v0.64.2-3K-next` branch is a source candidate for session-preserving
MQVPN failover and resilient VPS API routing. See [candidate behavior and test
limits](docs/3K-SMOOTH-FAILOVER.md). To materialize this candidate, clone this
branch and use its `source-lock-3k.json`; commands and validation sections below
also retain historical stable/RC context. Published release assets are unchanged.

The maintained cross-version acceptance checklist is
[3K-MODIFICATIONS.md](docs/3K-MODIFICATIONS.md). It distinguishes source,
artifact checks, historical runtime evidence and work still to verify. The
[WAN-failover investigation](docs/3K-WAN-FAILOVER-AUDIT.md) records the current
MQVPN path-removal and administration-routing findings with offline reproducers.

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

If a checkout already has local 3K work at the official feed base `818fa5116eefc99325e0f231e819dc51b062ef85`, `OMR3K_ALLOW_LOCAL_EDITS=yes python3 bootstrap-3k.py verify` explicitly allows that one dirty feed for development. The same override can be passed to `run-build-3k.sh`. It does not materialize a release and the output says `DEVELOPMENT ONLY`. Release builds use the published feed commit `3b21452ab4c572adc355ba5e80fe67757e57e07b` without this override.

The client kernel 6.18.39 contains the 3K congestion controls alongside upstream BBRv3 (kernel name `bbr`). BBRv3 is the kernel, new-install UCI and GUI default; an existing explicit choice is preserved. Keep the router image and paired VPS release at their respective pinned commits when deploying them together.

## RC1 frozen candidate and validation

The final four x86_64 images and paired VPS packages are published under https://repoomr.3klab.com/frozen3k/v0.64.2-20261013/. The release manifest records exact source commits, sizes and SHA256. `validation/` in this Git branch contains the image, BIOS/UEFI boot, BTF and HTTPS mirror reports.

The strict final firmware build completed successfully with 641 packages. The final ext4 image booted in isolated BIOS QEMU with BBRv3 selected, passed real loopback TCP transfers with all 18 controls, and registered/selected all eight BPF schedulers. NanBBR VAR applied 75 with matching readback and restored BBRv3 afterward. The final squashfs EFI image booted through OVMF with kernel 6.18.39 and default `bbr`. The GUI displayed BBRv3, the VAR slider, advanced Path diagnostics and the unchanged upstream Bandwidth page. All four published images were downloaded over HTTPS and matched their hashes.

These are functional VM checks. Real multi-WAN load/performance, the complete PC/phone WireGuard to VPS to OMR GUI path, and production VPS installation remain deployment checks. No production system was installed or rebooted.

## RC2 corrections

RC2 restores the .62 calculated path MTU in the Status page, including the link MTU, using DF probes towards the VPS with a bounded status budget and cache. The .62 IPv4/IPv6 omr-test-speed host lists are included again and protected as configuration files.

Runtime APK repositories use the five flat Ysurac v0.64.2-6.18/x86_64 feeds. The 3K base-files override suppresses OpenWrt-generated target/feed paths that do not exist on that server. This does not change the frozen build source checkouts. The actual image APK client successfully updated the five indexes with signature checks enabled and simulated adding tree in an isolated filesystem.

The RC2 release is https://github.com/Brazzo978/openmptcprouter/releases/tag/v0.64.2-3K-rc2. Use the immutable tag for a frozen rebuild:

```sh
git clone --branch v0.64.2-3K-rc2 https://github.com/Brazzo978/openmptcprouter.git
cd openmptcprouter
python3 bootstrap-3k.py materialize
./run-build-3k.sh prepare
./run-build-3k.sh build
```

RC2 firmware, BIOS/EFI, native Status RPC and VMware offline import reports are under `validation/rc2/`. The kernel is byte-identical to RC1.

## RC3 diagnostic logging

RC3 restores the earlier OMR diagnostic logging workflow: a bounded local collector, the read-only diagnostic RPC and a **Diagnostic logs** page in LuCI. The collector writes to RAM or persistent storage according to its configured storage setting; the support report applies the diagnostic module's redaction and output limits. RC3 keeps the RC2 Status PMTU, speedtest host lists and APK repository corrections.

The RC3 image gate checks that the collector, init script, Lua module, RPC endpoint, menu, read ACL and LuCI page are present in the assembled image and match their source files. It also checks executable permissions, the Lua module's 0644 mode and the startup link when the image root contains OpenWrt init links. These are build and packaging checks. Actual ESXi guest boot and live multi-WAN/WireGuard operation remain deployment validation.
