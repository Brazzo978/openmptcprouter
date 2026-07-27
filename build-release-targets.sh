#!/usr/bin/env bash
set -euo pipefail

RELEASE=${OMR_RELEASE:-v0.62.14-3K}
KERNEL=${OMR_KERNEL:-6.6}
FEED_SRC=${OMR_FEED_SRC:-omr-v0.62.14-3K}
JOBS=${OMR_JOBS:-24}
TARGETS=${OMR_TARGETS:-x86_64 rpi2 rpi3 rpi4 rpi5}
LOG_DIR=${OMR_LOG_DIR:-/root/omr-build-logs}
SERIAL_NET_SNMP=${OMR_SERIAL_NET_SNMP:-no}
SERIAL_TOOLS=${OMR_SERIAL_TOOLS:-yes}

mkdir -p "$LOG_DIR"

for target in $TARGETS; do
	log="$LOG_DIR/omr-${RELEASE}-${KERNEL}-${target}.log"
	echo "=== Building $target / kernel $KERNEL / release $RELEASE ==="
	echo "Log: $log"
	OMR_TARGET="$target" \
	OMR_KERNEL="$KERNEL" \
	OMR_RELEASE="$RELEASE" \
	OMR_FEED_SRC="$FEED_SRC" \
	OMR_JOBS="$JOBS" \
	OMR_SERIAL_NET_SNMP="$SERIAL_NET_SNMP" \
	OMR_SERIAL_TOOLS="$SERIAL_TOOLS" \
	./build.sh 2>&1 | tee "$log"
done
