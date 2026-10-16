# 3K uses the versioned Ysurac APK feeds from customfeeds.list.
# Override only base-files' repository generator, not feed/package selection.
define FeedSourcesAppendAPK
	printf '%s\n' '# 3K package repositories are pinned in customfeeds.list.' > $(1)
endef
