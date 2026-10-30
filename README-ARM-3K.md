# OpenMPTCProuter 0.64.2-3K ARM builds

This branch inventories all 44 ARM board configurations from upstream v0.64.2 (33 ARM64 and 11 ARM32 across 15 OpenWrt target/subtarget groups). The future-maintenance policy selects 25 build candidates with at least 1024 MiB RAM, excludes 15, and holds four ZBT profiles pending exact RAM verification. All historical IDs and source pins remain in the catalog and source lock. Previously published ARM assets are unaffected by this policy change.

Build status is separate from runtime validation. A compiled image is not a hardware boot test. Incompatible configurations, missing features and failed images are recorded explicitly. Partial prereleases may contain only individually verified builds and must identify the published subset and validation scope.

## Build one board

Use a full clone, a Linux OpenWrt build environment and the exact source lock. Rockchip U-Boot requires the host Python `elftools` module (Debian package `python3-pyelftools`), Python development headers, setuptools and SWIG. Install the standard OpenWrt prerequisites before starting the queue.

The generic ARM64 image uses a 512 MiB root partition: the full 3K filesystem does not fit in the upstream 104 MiB default.

Build a selected board with:

```sh
git clone --branch omr-v0.64.2-3K-arm https://github.com/Brazzo978/openmptcprouter.git
cd openmptcprouter
OMR_TARGET=rpi4 python3 bootstrap-3k.py materialize
OMR_TARGET=rpi4 OMR_JOBS=18 ./run-build-3k.sh build
```

Replace `rpi4` with an active `keep` target in `arm-targets-3k.json`. The default remains `x86_64`. `prepare` stops after defconfig and policy validation. Runtime APK URLs are derived from the resolved package architecture and retain the real upstream v0.64.2-6.18 repositories. The generic `armsr64` image requires a deployment with at least 1024 MiB RAM; `rpi3` maintenance applies to the Pi 3B+ hardware variant only.

## ARM target matrix

| OpenWrt target/subtarget | OMR configurations |
| --- | --- |
| armsr/armv8 | `armsr64` |
| bcm27xx/bcm2709 | `rpi2` |
| bcm27xx/bcm2710 | `rpi3` |
| bcm27xx/bcm2711 | `rpi4` |
| bcm27xx/bcm2712 | `rpi5` |
| ipq40xx/generic | `p2w_r619ac`, `rutx`, `rutx12`, `rutx50` |
| ipq806x/generic | `r7800` |
| mediatek/filogic | `bpi-r3`, `bpi-r3-mini`, `bpi-r4`, `bpi-r4-poe`, `cudy_tr3000-256mb-v1`, `gl-mt2500`, `gl-mt2500-airoha`, `gl-mt3000`, `gl-mt3600be`, `gl-mt5000`, `gl-mt6000`, `gl-x3000`, `gl-xe3000`, `z8102ax-emmc`, `z8102ax_128m`, `z8102ax_64m`, `z8109ax_128m`, `z8109ax_512m`, `z8802be_128m`, `z8803be` |
| mediatek/mt7622 | `bpi-r64` |
| mediatek/mt7623 | `bpi-r2` |
| mvebu/cortexa53 | `espressobin` |
| mvebu/cortexa9 | `cznic_turris-omnia`, `wrt3200acm`, `wrt32x` |
| qualcommax/ipq807x | `qnap-301w` |
| rockchip/armv8 | `r2s`, `r3s`, `r4s`, `r5c`, `r5s`, `r6s` |
| sunxi/cortexa7 | `bpi-r1` |

## Release queue

`run-arm-release-3k.py` is the release builder's persistent queue. It records all 44 historical IDs, builds only the 25 active `keep` candidates by default, and reuses the source/download/toolchain cache sequentially. Each built board gets its own binary output directory, log, configuration and manifest, preserving device-specific partition sizes. The shared source layout must be prepared before starting this internal release queue. Hardware exclusions and pending verification are explicit statuses (`excluded_by_hardware_policy` and `pending_hardware_verification`), applied before older board-port deferrals.

To build selected recovery boards in a **new job directory** after committing the policy change, run:

```sh
python3 run-arm-release-3k.py --root /path/to/build-repo --job /path/to/new-job \
  --targets bpi-r1 qnap-301w
```

`--targets` accepts unique active `keep` IDs only. The job records the exact `requested_targets`; every other kept board is `not_requested`, not a success. A job cannot resume with a different selection or build-root commit. Existing completed artifacts from earlier jobs are not imported or changed automatically; use a new job for this policy version and retain old manifests as separate provenance evidence. The queue uses the existing source and caches but does not treat earlier jobs' board states as proof for cache cleanup.

The queue records strict make exit status, exact source pins, image/profile hashes, executable architecture, compiled BPF scheduler count, kernel congestion controls, factory diagnostics/UI files, public signing keys and package outputs. New artifact manifests include the maintenance decision and any CPU advisory. It refuses changed provenance or target selection on resume and supports `--retry-failed` for an intentional retry. Disk space is checked before each board. A platform kernel cache is archived and verified before its uncompressed copy is removed only when every board in that platform has a verified built result or a catalog-authorized exclusion/pending/deferred status, and at least one board was built. `not_requested` never authorizes cleanup, so selecting only R6S does not retire the shared Rockchip cache using unverified results from another job. Firmware and APK output duplicates are removed only after their retained artifact copies match by size and SHA-256. Completed records are checked against their artifact manifests before cache retirement. Build manifests also inventory untracked OpenWrt overlay inputs. No images are automatically published by the queue: failures, installed UI/source parity and available ARM64 boot tests are reviewed first.

ARM Speedtest binaries come from the official Ookla 1.2.0 ARM64/ARM hard-float downloads with SHA-256 pinned in the package recipe. The vetted x86_64 binary remains available for x86 builds. Scheduler CO-RE types are generated from the actual target kernel; OpenWrt's synthetic MIPS UAPI header environment is retained, while tracing helpers select the actual kernel architecture.

The custom BBR2 and NanBBR implementations use kernel math64 helpers for runtime 64-bit divisions on ARM32. The Cudy TR3000 256 MB v1 build enables its exact upstream device definition and DTS.

## Hardware policy and recovery

The canonical hardware inventory is `hardware-inventory-3k.json`; the executable future-maintenance decisions are in `arm-targets-3k.json`. NAND/eMMC suffixes describe storage and are never used as RAM evidence. Variants with multiple documented RAM sizes are kept only where every listed variant has at least 1024 MiB. The `z8102ax_128m` decision applies specifically to the documented Z8102AX v1 with 128 MB NAND and 1 GiB RAM. The `z8102ax-emmc` profile remains pending because vendor RAM information conflicts with the local DTS. Four ZBT IDs remain pending until the exact RAM configuration is verified. R1 remains selected despite its older ARMv7 CPU; encrypted bonding/SQM headroom is limited and no 3K throughput measurement is available. This is an advisory, not a measured speed claim.

The 15 excluded IDs are `bpi-r2`, `cudy_tr3000-256mb-v1`, `gl-mt3000`, `gl-mt3600be`, `gl-x3000`, `gl-xe3000`, `p2w_r619ac`, `r7800`, `rpi2`, `rutx`, `rutx12`, `rutx50`, `wrt3200acm`, `wrt32x`, and `z8802be_128m`. The four pending IDs are `z8102ax_64m`, `z8102ax-emmc`, `z8109ax_128m`, and `z8109ax_512m`. The other 25 IDs in the matrix are active `keep` candidates.

The NanoPi R6S, Banana Pi R1 and Banana Pi R2 SD-root partitions are fixed at 512 MiB. The full 3K filesystem exceeds the upstream 104 MiB default. Banana Pi R2/R64 configurations use the exact current device IDs. The exact kernel package kmod-qcom-qmi-helpers is permitted because Qualcomm ath11k/ath12k Wi-Fi depends on it; modem-management packages remain excluded.

The following historical board-port limitations remain documented, but their targets are now excluded by the hardware policy before the deferred-port check:

- r7800: ipq806x still has 6.12 target configuration/patches in the frozen source; a 6.18 backport requires separate review and board validation.
- rutx: the old generic profile has no match; RUTX10 is disabled upstream for missing DSA setup.
- rutx12: no corresponding device definition/DTS exists in the frozen source.

Their configuration files are retained for future porting. No board is substituted for a different model, and no 3K feature or source pin is removed to make a build pass.

Banana Pi R2 is now excluded after the full recovery image exceeded its fixed 40 MiB SD recovery partition (49,597,996 bytes). The size guard remains enabled and the recovery/layout remain intact. No image is published for this board. R1 and QNAP are allowed one final build attempt after verified cache offload; a further failure ends their recovery work.
