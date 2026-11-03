#!/bin/sh
# Read-only client inventory/runtime baseline. Executed through the pinned,
# local SSH helper. It prints only selected package/service facts, never UCI,
# credentials, network configuration, or process command lines.
LC_ALL=C
export LC_ALL

emit() {
	key=$1
	value=$(printf '%s' "$2" | tr '\t\r\n' '   ' | cut -c1-320)
	printf '%s\t%s\n' "$key" "$value"
}

join_lines() {
	awk 'NF { if (n++) printf ","; printf "%s", $0 } END { if (!n) printf "none" }'
}

emit audit_utc "$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)"
release=$(sed -n 's/^DISTRIB_RELEASE="\([^"]*\)"$/\1/p' /etc/openwrt_release 2>/dev/null | head -n 1)
emit router_release "${release:-unknown}"
emit kernel_release "$(uname -r 2>/dev/null || printf unknown)"

manifest=/lib/apk/db/installed
installed=
if [ -r "$manifest" ]; then
	installed=$(awk -F: '$1 == "P" { p=$2 } $1 == "V" && p != "" { print p "=" $2 }' "$manifest" | sort)
	emit manifest_read yes
	emit manifest_package_count "$(printf '%s\n' "$installed" | awk 'NF {n++} END {print n+0}')"
else
	emit manifest_read missing
	installed=
fi

for name in \
	btop speedtest-ookla-3k speedtestcpp speedtest \
	openvpn-openssl openvpn-mbedtls openvpn-wolfssl kmod-ovpn luci-proto-openvpn \
	mlvpn luci-app-mlvpn \
	mptcp-bpf-bkup mptcp-bpf-burst mptcp-bpf-first mptcp-bpf-red \
	mptcp-bpf-rr mptcp-bpf-weight mptcp-bpf-weight-rr mptcp-bpf-dscp \
	bpftool-full kmod-sched-bpf kmod-sched-core kmod-sched-flower \
	kmod-qcom-qmi-helpers
do
	version=$(printf '%s\n' "$installed" | awk -F= -v n="$name" '$1 == n { sub(/^[^=]*=/, ""); print; exit }')
	emit "package.$name" "${version:-absent}"
done

printf '%s\n' "$installed" | awk -F= '
{
 n=tolower($1)
 if (n == "kmod-qcom-qmi-helpers") next
 if (n ~ /(modemmanager|modem-manager|umbim|uqmi|mbim|qmi|ncm|wwan|sierra|huawei|hso|kalmia|ipheth|comgt|usb-modeswitch|gobinet|pcie_mhi|usb-wdm|usb-acm|gigaset|hfcpci|hfcmulti|solos-pci|chat|luci-proto-3g|usb-serial-ipw)/) {
   if (n ~ /^lib/) libs[++nl]=$0
   else if (n ~ /^kmod-/) drivers[++nd]=$0
   else controls[++nc]=$0
 }
 if (n ~ /(mlvpn|openvpn.*bond|bond.*openvpn)/) bonds[++nb]=$0
 if (n ~ /^luci-i18n-/) i18n[++ni]=$0
 if (n ~ /^luci-i18n-/ && n !~ /-(en|english)$/) nonen[++nx]=$0
 if (n ~ /^openvpn/) ovpn[++no]=$0
}
END {
 printf "package.modem_control_candidates\t"
 for(i=1;i<=nc;i++) printf "%s%s", i==1?"":",", controls[i]
 if(!nc) printf "none"
 printf "\npackage.modem_kernel_driver_candidates\t"
 for(i=1;i<=nd;i++) printf "%s%s", i==1?"":",", drivers[i]
 if(!nd) printf "none"
 printf "\npackage.modem_library_candidates\t"
 for(i=1;i<=nl;i++) printf "%s%s", i==1?"":",", libs[i]
 if(!nl) printf "none"
 printf "\npackage.openvpn_bonding_or_mlvpn\t"
 for(i=1;i<=nb;i++) printf "%s%s", i==1?"":",", bonds[i]
 if(!nb) printf "none"
 printf "\npackage.ordinary_openvpn_related\t"
 for(i=1;i<=no;i++) printf "%s%s", i==1?"":",", ovpn[i]
 if(!no) printf "none"
 printf "\npackage.luci_i18n\t"
 for(i=1;i<=ni;i++) printf "%s%s", i==1?"":",", i18n[i]
 if(!ni) printf "none"
 printf "\npackage.luci_i18n_non_english\t"
 for(i=1;i<=nx;i++) printf "%s%s", i==1?"":",", nonen[i]
 if(!nx) printf "none"
 printf "\n"
}'

# Compiled LuCI message catalogs: report only locale suffixes and counts.
 lmo_files=
for dir in /usr/lib/lua/luci/i18n /usr/share/luci/i18n; do
	[ -d "$dir" ] || continue
	lmo_files="${lmo_files}${lmo_files:+
}$(find "$dir" -type f -name '*.lmo' 2>/dev/null)"
done
if [ -n "$lmo_files" ]; then
	lmo_count=$(printf '%s\n' "$lmo_files" | awk 'NF {n++} END {print n+0}')
	lmo_locales=$(printf '%s\n' "$lmo_files" | while IFS= read -r path; do
		base=${path##*/}
		locale=$(printf '%s\n' "$base" | sed -n 's/.*\.\([^.]*\)\.lmo$/\1/p')
		[ -n "$locale" ] && printf '%s\n' "$locale"
	done | sort -fu | join_lines)
	lmo_nonenglish=$(printf '%s\n' "$lmo_files" | while IFS= read -r path; do
		base=${path##*/}
		locale=$(printf '%s\n' "$base" | sed -n 's/.*\.\([^.]*\)\.lmo$/\1/p')
		case "$(printf '%s' "$locale" | tr '[:upper:]' '[:lower:]')" in
			en|en_us|en_gb|english|'') ;;
			*) printf '%s\n' "$locale" ;;
		esac
	done | sort -fu | join_lines)
else
	lmo_count=0
	lmo_locales=none
	lmo_nonenglish=none
fi
emit luci_lmo_file_count "$lmo_count"
emit luci_lmo_locales "$lmo_locales"
emit luci_lmo_non_english_locales "$lmo_nonenglish"

# Version/help-only probes; these flags do not start throughput tests.
probe() {
	name=$1
	flag=$2
	bin=$(command -v "$name" 2>/dev/null || true)
	if [ -z "$bin" ] || [ ! -x "$bin" ]; then
		emit "executable.$name" absent
		emit "probe.$name" not_run
		return
	fi
	emit "executable.$name" "$bin"
	output=$("$bin" "$flag" 2>&1)
	rc=$?
	first=$(printf '%s\n' "$output" | head -n 1)
	first=$(printf '%s' "$first" | tr -d '\033' | sed 's/\[[0-9;]*[[:alpha:]]//g')
	emit "probe.$name.flag" "$flag"
	emit "probe.$name.exit" "$rc"
	emit "probe.$name.first_line" "$first"
}
probe_path() {
	name=$1
	bin=$2
	flag=$3
	if [ ! -x "$bin" ]; then
		emit "executable.$name" absent
		emit "probe.$name" not_run
		return
	fi
	emit "executable.$name" "$bin"
	output=$("$bin" "$flag" 2>&1)
	rc=$?
	first=$(printf '%s\n' "$output" | head -n 1)
	first=$(printf '%s' "$first" | tr -d '\033' | sed 's/\[[0-9;]*[[:alpha:]]//g')
	emit "probe.$name.flag" "$flag"
	emit "probe.$name.exit" "$rc"
	emit "probe.$name.first_line" "$first"
}
probe btop --version
probe speedtest --version
probe_path speedtestcpp /usr/bin/SpeedTest --help

speedtestcpp_paths=$(apk info -L speedtestcpp 2>/dev/null | awk '/^\/(usr\/)?(s?bin)\// {print}' | sort -u | join_lines)
emit speedtestcpp.package_bin_paths "${speedtestcpp_paths:-none}"
speedtestcpp_manifest_files=$(awk -F: '
 $1 == "P" { in_pkg=($2 == "speedtestcpp"); current_dir="" }
 in_pkg && $1 == "F" { current_dir=$2 }
 in_pkg && $1 == "R" {
   if (current_dir == "") print "/" $2
   else print "/" current_dir "/" $2
 }' /lib/apk/db/installed | grep '^/usr/bin/' | sort -u | join_lines)
emit speedtestcpp.manifest_files "${speedtestcpp_manifest_files:-none}"
printf '%s\n' "$installed" | awk -F= 'tolower($1) ~ /libbpf/ {print}' | sort | join_lines | {
	read -r libbpf_packages
	emit package.libbpf_related "${libbpf_packages:-none}"
}
if [ -s /sys/kernel/btf/vmlinux ]; then
	emit kernel.btf_vmlinux present
else
	emit kernel.btf_vmlinux absent
fi

# Read only fixed, known services. Procd response is filtered to running
# booleans before output; commands, arguments, environment and config are not
# collected. Tracker/MQVPN observations may be transient during profile QA.
for service in rpcd uhttpd dnsmasq omr-tracker omr-profiles mqvpn; do
	init="/etc/init.d/$service"
	if [ -x "$init" ]; then
		emit "service.$service.init_present" true
		"$init" enabled >/dev/null 2>&1
		enabled_rc=$?
		case "$enabled_rc" in
			0) init_enabled=true ;;
			1) init_enabled=false ;;
			*) init_enabled=unknown ;;
		esac
	else
		emit "service.$service.init_present" false
		init_enabled=unknown
	fi
	emit "service.$service.init_enabled" "$init_enabled"
	boot_enabled=false
	for link in /etc/rc.d/S??"$service"; do
		[ -e "$link" ] || [ -L "$link" ] || continue
		boot_enabled=true
		break
	done
	emit "service.$service.boot_enabled" "$boot_enabled"
	if command -v ubus >/dev/null 2>&1 && command -v jsonfilter >/dev/null 2>&1; then
		running_values=$(ubus call service list "{\"name\":\"$service\"}" 2>/dev/null | jsonfilter -e "@[\"$service\"].instances.*.running" 2>/dev/null | awk '$0 == "true" || $0 == "false" { if (n++) printf ","; printf "%s", $0 }')
		[ -n "$running_values" ] || running_values=unreported
	else
		running_values=unavailable
	fi
	emit "service.$service.procd_instance_running" "$running_values"
done

# Read only the registered/available CC list; intentionally omit active CC.
cc_list=$(cat /proc/sys/net/ipv4/tcp_available_congestion_control 2>/dev/null || printf unavailable)
emit tcp_available_congestion_control "$cc_list"

# Check all eight packaged BPF schedulers and their expected object files.
for scheduler in bkup burst first red rr weight weight_rr dscp; do
	package="mptcp-bpf-$scheduler"
	[ "$scheduler" != weight_rr ] || package=mptcp-bpf-weight-rr
	version=$(printf '%s\n' "$installed" | awk -F= -v n="$package" '$1 == n { sub(/^[^=]*=/, ""); print; exit }')
	emit "scheduler.package.$scheduler" "${version:-absent}"
	object="/usr/share/bpf/scheduler/mptcp_bpf_${scheduler}.o"
	if [ -f "$object" ]; then
		size=$(wc -c < "$object" | tr -d ' ')
		emit "scheduler.object.$scheduler" "present:$size"
	else
		emit "scheduler.object.$scheduler" absent
	fi
done
emit bpftool.executable "$(command -v bpftool 2>/dev/null || printf absent)"
