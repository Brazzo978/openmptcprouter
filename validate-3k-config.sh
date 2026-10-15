#!/bin/sh
set -eu

config=${1:?usage: validate-3k-config.sh SOURCE-DIR}
conf="$config/.config"
feed="$config/package/system/apk/files/customfeeds.list"
[ -f "$conf" ] || { echo "missing defconfig output: $conf" >&2; exit 1; }
[ -f "$feed" ] || { echo "missing APK feed list: $feed" >&2; exit 1; }

while IFS= read -r setting; do
    grep -Fqx "$setting" "$conf" || { echo "required selection missing: $setting" >&2; exit 1; }
done <<'REQUIRED'
CONFIG_TARGET_x86_64=y
CONFIG_PACKAGE_openmptcprouter-full=y
CONFIG_PACKAGE_btop=y
CONFIG_PACKAGE_openvpn-openssl=y
CONFIG_PACKAGE_kmod-ovpn=y
CONFIG_PACKAGE_luci-proto-openvpn=y
CONFIG_PACKAGE_speedtestcpp=y
CONFIG_PACKAGE_speedtest-ookla-3k=y
CONFIG_PACKAGE_xray-core=y
CONFIG_PACKAGE_xray-config=y
CONFIG_PACKAGE_openssl-util=y
CONFIG_PACKAGE_sqm-scripts=y
CONFIG_PACKAGE_sqm-autorate=y
CONFIG_PACKAGE_luci-app-sqm-autorate=y
CONFIG_PACKAGE_mptcp-bpf-bkup=y
CONFIG_PACKAGE_mptcp-bpf-burst=y
CONFIG_PACKAGE_mptcp-bpf-first=y
CONFIG_PACKAGE_mptcp-bpf-red=y
CONFIG_PACKAGE_mptcp-bpf-rr=y
CONFIG_PACKAGE_mptcp-bpf-weight=y
CONFIG_PACKAGE_mptcp-bpf-weight-rr=y
CONFIG_PACKAGE_mptcp-bpf-dscp=y
CONFIG_PACKAGE_mptcp-weight-manager=y
CONFIG_PACKAGE_mptcp-dscp-manager=y
CONFIG_PACKAGE_bpftool-full=y
CONFIG_HAS_BPF_TOOLCHAIN=y
CONFIG_BPF_TOOLCHAIN_HOST=y
CONFIG_KERNEL_BPF_EVENTS=y
CONFIG_KERNEL_DEBUG_INFO_BTF=y
CONFIG_VERSION_NUMBER="v0.64.2-3K-rc3"
REQUIRED

if grep -Eq '^CONFIG_(ALL_KMODS|ALL|ALL_NONSHARED)=[ym]$' "$conf"; then
    echo "broad package/module selection restored by defconfig" >&2
    grep -E '^CONFIG_(ALL_KMODS|ALL|ALL_NONSHARED)=[ym]$' "$conf" >&2
    exit 1
fi

bad_legacy=$(grep -E '^CONFIG_PACKAGE_(mlvpn|luci-app-mlvpn)=[ym]$' "$conf" || true)
[ -z "$bad_legacy" ] || { echo "unsupported client VPN selected: $bad_legacy" >&2; exit 1; }

bad_modems=$(grep -Ei '^CONFIG_PACKAGE_[A-Za-z0-9_-]*(modem|mbim|qmi|ncm|wwan|sierra|huawei|hso|kalmia|ipheth|comgt|usb-modeswitch|gobinet|pcie_mhi|usb-wdm|usb-acm|gigaset|hfcpci|hfcmulti|solos-pci|chat|luci-proto-3g|usb-serial-ipw)[A-Za-z0-9_-]*=[ym]$' "$conf" || true)
if [ -n "$bad_modems" ]; then
    echo "cellular/legacy modem selections restored by defconfig:" >&2
    printf '%s\n' "$bad_modems" >&2
    exit 1
fi

bad_langs=$(grep -E '^CONFIG_LUCI_LANG_[^=]+=[ym]$' "$conf" | grep -v '^CONFIG_LUCI_LANG_en=' || true)
bad_i18n=$(grep -E '^CONFIG_PACKAGE_luci-i18n-[^=]+=[ym]$' "$conf" || true)
if [ -n "$bad_langs$bad_i18n" ]; then
    echo "non-English LuCI translation selected:" >&2
    printf '%s\n%s\n' "$bad_langs" "$bad_i18n" >&2
    exit 1
fi

if grep -Fv '/v0.64.2-6.18/x86_64/' "$feed" >/dev/null; then
    echo "APK feed list has an unpinned package URL:" >&2
    cat "$feed" >&2
    exit 1
fi
[ "$(grep -c '^https://' "$feed")" -ge 4 ] || {
    echo "APK feed list is incomplete" >&2
    exit 1
}


grep -Fqx 'include $(TOPDIR)/package/base-files/3k-apk-repositories.mk' "$config/package/base-files/Makefile" || { echo "missing 3K APK repository generator override" >&2; exit 1; }

echo "3K defconfig passed: stock schedulers/BPF/BTF and tools selected; no modem or extra LuCI language; upstream APK feed pinned"
