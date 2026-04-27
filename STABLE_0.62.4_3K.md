# Stable reference: v0.62.4-3K

This branch is the local stable baseline for the known-good v0.62.4-3K x86_64 / kernel 6.6 image.

## Source baseline

- Main branch: `omr-v0.62.4-3K-stable-local`
- Release string: `v0.62.4-3K`
- Default kernel used for stable image: `6.6`
- OpenWrt source commit: `92e020b50f04535009c91aa708bdb7598f1d9d4a`
- Feed branch expected by `build.sh`: `omr-v0.62.4-3K-stable-local`

## Stable image profile

The stable x86_64 profile keeps the v0.62.4-3K release name and includes the actual tested image choices:

- LuCI English-only profile
- `htop` included
- `btop` included
- `open-vm-tools` disabled
- kernel 6.6 MPTCP/BPF scheduler stack enabled

## Feed additions required for reproducibility

The feed branch includes the v0.62.4-3K additions used by the stable image:

- `openmptcprouter/files/usr/bin/speedtest`
- `openmptcprouter/files/usr/bin/gtun-swap`
- `openmptcprouter/files/usr/lib/gtun-swap/glorytun.omrdev5`
- `btop` dependency in `openmptcprouter-full`

## Verified artifacts

Canonical artifact directory:

- `/root/releases/v0.62.4-3K-upload`

Verification run:

```sh
cd /root/releases/v0.62.4-3K-upload
sha256sum -c sha256sums.txt
```

Result: all listed files verified `OK` on 2026-04-27.

## Do not use as stable baseline

The v0.62.5 and v0.62.6 test branches/artifacts are intentionally not part of this stable baseline.
