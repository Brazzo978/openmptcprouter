#!/bin/sh
# Build the minimal x86_64 v0.64.2-3K image from the pinned local checkouts.
set -eu

cd "$(dirname "$0")"
mode=${1:-build}
case "$mode" in
    prepare|build) ;;
    *) echo "usage: $0 [prepare|build] [make arguments...]" >&2; exit 2 ;;
esac
[ "$#" -eq 0 ] || shift

# Fail before build.sh can rewrite feed indexes unless every local checkout is
# based on the reviewed immutable source lock. Dirty authorized edits remain.
python3 ./bootstrap-3k.py verify

# Avoid the upstream OMR_HOST fallback querying ifconfig.co during preparation.
# OMR_REPO below is explicit; this placeholder is not published in an image.
export OMR_HOST=127.0.0.1
export OMR_TARGET=x86_64
export OMR_KERNEL=6.18
export OMR_DIST=openmptcprouter
export OMR_PACKAGES=full
export OMR_RELEASE=v0.64.2-3K-rc2
export OMR_VERSION_NUMBER=v0.64.2-3K-rc2
export OMR_PACKAGE_RELEASE=v0.64.2-6.18
export OMR_REPO=https://packages.openmptcprouter.com/v0.64.2-6.18/x86_64
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
source_dir="$PWD/x86_64/6.18/source"
(
    cd "$source_dir"
    make defconfig
)
./validate-3k-config.sh "$source_dir"

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
