# RC2 validation

Strict firmware build and final image verification passed (641 packages).
The final ext4 image boots in isolated BIOS QEMU; the squashfs EFI image boots through OVMF.
Both report v0.64.2-3K-rc2, Linux6.18.39 and default bbr (BBRv3).

Both native Status RPCs were exercised in the BIOS guest with an isolated synthetic WAN.
They return mtu=1500 and link_mtu=1500 and create a PMTU cache entry. The tracker was stopped only in that disposable snapshot to keep the synthetic WAN marked up without a real VPS.
Separate tests cover PMTU1420/link1500, cache, missing data, blocked probes, deadline and LuCI rendering.

The built APK3 client reproduced the old repository errors (exit5), then updated the five corrected signed Ysurac indexes (exit0, 10420 packages) and simulated adding tree (exit0). This checks index update and dependency resolution; a blanket package upgrade was not tested. Kernel/kmods remain tied to the custom3K ABI.

Speedtest host lists match the .62 custom originals byte for byte. The 3K speedtest endpoint returned HTTP200 to HEAD.
VMware OVF Tool4.6.2 full offline import validated schema, manifest and VMDK transfer. The canonical VMware VMDK has virtual contents identical to the original raw disk. Actual ESXi/Workstation guest boot remains a user deployment check.

The RC2 vmlinux SHA256 is identical to RC1:
8531a95bc856105424b0a089e9744f640c626a2beeace6f5989acf077f530bf1
The prior 18TCP transfers and 8BPF scheduler tests are therefore retained as kernel validation; they were not repeated as RC2 WAN performance tests.

No production system was installed, rebooted or reconfigured. Real multi-WAN, WAN PMTU and full remote WireGuard path remain deployment checks.
