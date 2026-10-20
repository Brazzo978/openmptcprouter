include $(TOPDIR)/rules.mk

PKG_NAME:=speedtest-ookla-3k
PKG_VERSION:=1.2.0.84
PKG_RELEASE:=2

# Keep the vetted x86_64 executable; ARM uses checksum-pinned official binaries.
ifneq ($(filter arm aarch64,$(ARCH)),)
  OOKLA_ARCH:=$(if $(filter aarch64,$(ARCH)),aarch64,armhf)
  PKG_SOURCE:=ookla-speedtest-1.2.0-linux-$(OOKLA_ARCH).tgz
  PKG_SOURCE_URL:=https://install.speedtest.net/app/cli
  PKG_HASH:=$(if $(filter aarch64,$(ARCH)),3953d231da3783e2bf8904b6dd72767c5c6e533e163d3742fd0437affa431bd3,e45fcdebbd8a185553535533dd032d6b10bc8c64eee4139b1147b9c09835d08d)
  PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)-$(ARCH)
  SPEEDTEST_BINARY:=$(PKG_BUILD_DIR)/speedtest
else
  SPEEDTEST_BINARY:=./files/speedtest
endif

include $(INCLUDE_DIR)/package.mk

define Package/speedtest-ookla-3k
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Official speedtest CLI for x86_64 and ARM
  DEPENDS:=@(TARGET_x86_64||aarch64||arm)
endef

define Package/speedtest-ookla-3k/description
  Speedtest CLI with the executable selected for the target architecture.
  ARM downloads use fixed source hashes; the x86_64 executable is carried
  forward from the vetted v0.62 image.
endef

ifneq ($(filter arm aarch64,$(ARCH)),)
define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(TAR) -C $(PKG_BUILD_DIR) -xzf $(DL_DIR)/$(PKG_SOURCE)
endef
endif

define Build/Compile
endef

define Package/speedtest-ookla-3k/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(SPEEDTEST_BINARY) $(1)/usr/bin/speedtest
endef

$(eval $(call BuildPackage,speedtest-ookla-3k))
