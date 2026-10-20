# OpenMPTCProuter 0.64.2-3K ARM builds

This branch extends the frozen x86_64 0.64.2-3K source to every ARM board configuration in upstream v0.64.2: 44 configurations, 33 ARM64 and 11 ARM32, across 15 OpenWrt target/subtarget groups. Source commits, client/VPS protocol and the 3K feature policy remain pinned.

Build status is separate from runtime validation. A compiled image is not a hardware boot test. Incompatible configurations, missing features and failed images are recorded explicitly; they must be resolved before release publication.

## Build one board

Use a full clone, a Linux OpenWrt build environment and the exact source lock:

```sh
git clone --branch omr-v0.64.2-3K-arm https://github.com/Brazzo978/openmptcprouter.git
cd openmptcprouter
OMR_TARGET=rpi4 python3 bootstrap-3k.py materialize
OMR_TARGET=rpi4 OMR_JOBS=18 ./run-build-3k.sh build
```

Replace `rpi4` with a target from the table below. The default remains `x86_64`. `prepare` stops after defconfig and policy validation. Runtime APK URLs are derived from the resolved package architecture and retain the real upstream v0.64.2-6.18 repositories.

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

`run-arm-release-3k.py` is the release builder's persistent queue. It uses 44 separate board configurations and reuses the source/download/toolchain cache sequentially. Each board gets its own binary output directory, log, configuration and manifest, preserving device-specific partition sizes. The shared source layout must be prepared before starting this internal release queue.

The queue records strict make exit status, exact source pins, image/profile hashes, executable architecture, compiled BPF scheduler count, kernel congestion controls, factory diagnostics/UI files, public signing keys and package outputs. It refuses changed provenance on resume and supports `--retry-failed` for an intentional retry. Disk space is checked before each board. No images are automatically published by the queue: failures, installed UI/source parity and available ARM64 boot tests are reviewed first.

ARM Speedtest binaries come from the official Ookla 1.2.0 ARM64/ARM hard-float downloads with SHA-256 pinned in the package recipe. The vetted x86_64 binary remains available for x86 builds. Scheduler CO-RE types are generated from the actual target kernel; OpenWrt's synthetic MIPS UAPI header environment is retained, while tracing helpers select the actual kernel architecture.
