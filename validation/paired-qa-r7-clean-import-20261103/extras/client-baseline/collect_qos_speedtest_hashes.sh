#!/bin/sh
# Read-only byte-identity check for directly installed 3K speedtest/SQM files.
# CR bytes are removed before hashing to compare content normalized to LF.
# This script never reads UCI values or executes the speedtest/tracker scripts.
LC_ALL=C
export LC_ALL

emit() {
	_emit_key=$1
	_emit_value=$(printf '%s' "$2" | tr '\t\r\n' '   ' | cut -c1-320)
	printf '%s\t%s\n' "$_emit_key" "$_emit_value"
}

package_version() {
	awk -F: -v wanted="$1" '
		$1 == "P" { p=$2 }
		$1 == "V" && p == wanted { print $2; exit }
	' /lib/apk/db/installed 2>/dev/null
}

check_file() {
	cf_key=$1
	cf_path=$2
	cf_mode=$3
	emit "file.$cf_key.path" "$cf_path"
	if [ ! -f "$cf_path" ]; then
		emit "file.$cf_key.present" false
		emit "file.$cf_key.normalized_lf_sha256" absent
		emit "file.$cf_key.normalized_lf_bytes" absent
		emit "file.$cf_key.executable" not_applicable
		return
	fi
	emit "file.$cf_key.present" true
	cf_hash=$(tr -d '\r' < "$cf_path" | sha256sum | awk '{print $1}')
	cf_bytes=$(tr -d '\r' < "$cf_path" | wc -c | tr -d ' ')
	emit "file.$cf_key.normalized_lf_sha256" "$cf_hash"
	emit "file.$cf_key.normalized_lf_bytes" "$cf_bytes"
	if [ "$cf_mode" = executable ]; then
		if [ -x "$cf_path" ]; then cf_exec_state=true; else cf_exec_state=false; fi
	else
		cf_exec_state=not_applicable
	fi
	emit "file.$cf_key.executable" "$cf_exec_state"
}

check_package_file() {
	cpf_package=$1
	cpf_path=$2
	cpf_list="/lib/apk/packages/$cpf_package.list"
	if [ ! -r "$cpf_list" ]; then
		cpf_result=package_file_list_unavailable
	elif grep -Fxq "$cpf_path" "$cpf_list" || grep -Fxq "${cpf_path#/}" "$cpf_list"; then
		cpf_result=listed_in_installed_package_manifest
	else
		cpf_result=not_listed_in_installed_package_manifest
	fi
	emit "package_file.$cpf_package.$(basename "$cpf_path")" "$cpf_result"
}

emit audit_utc "$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)"
emit kernel_release "$(uname -r 2>/dev/null || printf unknown)"
emit package.openmptcprouter "$(package_version openmptcprouter)"
emit package.omr-tracker "$(package_version omr-tracker)"

check_file omr_test_speed /bin/omr-test-speed executable
check_file ipv4_host_list /etc/omr-test-speed-hosts.list data
check_file ipv6_host_list /etc/omr-test-speed-hosts6.list data
check_file sqm_firstboot_defaults /etc/uci-defaults/2040-omr-sqm executable
check_file sqm_tracker_hook /usr/share/omr/post-tracking.d/022-speedtest executable
check_package_file openmptcprouter /bin/omr-test-speed
check_package_file openmptcprouter /etc/omr-test-speed-hosts.list
check_package_file openmptcprouter /etc/omr-test-speed-hosts6.list
check_package_file openmptcprouter /etc/uci-defaults/2040-omr-sqm
check_package_file omr-tracker /usr/share/omr/post-tracking.d/022-speedtest
