include $(TOPDIR)/rules.mk

PKG_NAME:=speedtest-ookla-3k
PKG_VERSION:=1.2.0.84
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

define Package/speedtest-ookla-3k
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Carry-forward x86_64 speedtest CLI
  DEPENDS:=@TARGET_x86_64
endef

define Package/speedtest-ookla-3k/description
  The x86_64 speedtest executable carried forward from the vetted v0.62 image.
endef

define Build/Compile
endef

define Package/speedtest-ookla-3k/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) ./files/speedtest $(1)/usr/bin/speedtest
endef

$(eval $(call BuildPackage,speedtest-ookla-3k))
