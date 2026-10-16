# Native OpenVPN data-channel offload in Linux 6.18.
# The OpenWrt base at c0e9507 does not yet declare a package for CONFIG_OVPN.
define KernelPackage/ovpn
  SUBMENU:=$(NETWORK_SUPPORT_MENU)
  TITLE:=OpenVPN data channel offload (in-tree)
  DEPENDS:=@LINUX_6_18 +kmod-udptunnel4 +IPV6:kmod-udptunnel6 \
	+kmod-crypto-aead +kmod-crypto-gcm +kmod-crypto-chacha20poly1305
  KCONFIG:=CONFIG_OVPN=m
  FILES:=$(LINUX_DIR)/drivers/net/ovpn/ovpn.ko
  AUTOLOAD:=$(call AutoLoad,30,ovpn)
endef

define KernelPackage/ovpn/description
  Native Linux 6.18 OpenVPN data channel offload module.
endef

$(eval $(call KernelPackage,ovpn))
