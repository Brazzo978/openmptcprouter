#!/bin/sh
# Build a selected v0.64.2-3K image from the pinned local checkouts.
set -eu

cd "$(dirname "$0")"
mode=${1:-build}
case "$mode" in
    prepare|build) ;;
    *) echo "usage: $0 [prepare|build] [make arguments...]" >&2; exit 2 ;;
esac
[ "$#" -eq 0 ] || shift
target=${OMR_TARGET:-x86_64}

# Fail before build.sh can rewrite feed indexes unless every local checkout is
# based on the reviewed immutable source lock. Dirty authorized edits remain.
python3 ./bootstrap-3k.py verify --target "$target"
source_dir="$PWD/$target/6.18/source"
target_board=$(sed -n 's/^CONFIG_TARGET_\([A-Za-z0-9]*\)=y$/\1/p' "config-$target" | head -n 1)
[ -n "$target_board" ] && [ -d "$source_dir/target/linux/$target_board" ] || {
    echo "target $target is absent from pinned OpenWrt 6.18; refusing to build with a different kernel target" >&2
    exit 1
}

# Avoid the upstream OMR_HOST fallback querying ifconfig.co during preparation.
# OMR_REPO below is explicit; this placeholder is not published in an image.
export OMR_HOST=127.0.0.1
export OMR_TARGET="$target"
export OMR_KERNEL=6.18
export OMR_DIST=openmptcprouter
export OMR_PACKAGES=full
export OMR_RELEASE=v0.64.2-3K
export OMR_VERSION_NUMBER=v0.64.2-3K
export OMR_PACKAGE_RELEASE=v0.64.2-6.18
export OMR_REPO="https://packages.openmptcprouter.com/v0.64.2-6.18/$target"
export OMR_FEED=feeds/openmptcprouter
export OMR_FEED_SRC=omr-v0.64.2-3K
export OMR_3K=yes
export OMR_OPENWRT=default
export OMR_OPENWRT_GIT=https://github.com
export CUSTOM_FEED_URL=
export ONLY_PREPARE=yes
export OMR_KEEPBIN=yes
export OMR_ALL_PACKAGES=no
export FORCE_UNSAFE_CONFIGURE=1

# ONLY_PREPARE keeps build.sh from fetching/checking out over local feed edits
# and stops before its IGNORE_ERRORS=m compilation. We drive defconfig here.
./build.sh
(
    cd "$source_dir"
    make defconfig
)
# build.sh has a partial board-to-package-architecture map. Use the architecture
# resolved by OpenWrt for both installed APK feeds and the image's runtime URL.
arch=$(sed -n 's/^CONFIG_TARGET_ARCH_PACKAGES="\([A-Za-z0-9_-]*\)"$/\1/p' "$source_dir/.config" | head -n 1)
case "$arch" in
    arm_*|aarch64_*|x86_64) ;;
    *) echo "unsupported or unresolved package architecture for $target: $arch" >&2; exit 1 ;;
esac
repo="https://packages.openmptcprouter.com/v0.64.2-6.18/$arch"
feed="$source_dir/package/system/apk/files/customfeeds.list"
for component in luci packages base routing telephony; do
    printf '%s/%s/packages.adb\n' "$repo" "$component"
done > "$feed"
sed -i "s|^CONFIG_VERSION_REPO=.*|CONFIG_VERSION_REPO=\"$repo\"|" "$source_dir/.config"
(
    cd "$source_dir"
    make defconfig
)
./validate-3k-config.sh "$source_dir" "$target"

if [ "$mode" = prepare ]; then
    echo "3K source prepared and validated; compilation not started."
    exit 0
fi

jobs=${OMR_JOBS:-18}
case "$jobs" in
    ''|*[!0-9]*) echo "OMR_JOBS must be an integer from 1 to 20" >&2; exit 2 ;;
esac
[ "$jobs" -ge 1 ] && [ "$jobs" -le 20 ] || {
    echo "OMR_JOBS must be from 1 to 20" >&2
    exit 2
}
cd "$source_dir"
make -j"$jobs" "$@"
