.PHONY: common help install
PREFIX?=/usr
SYSCONFDIR?=/etc
UDEVDIR?=$(PREFIX)/lib/udev
UDEVRULESDIR?=$(PREFIX)/lib/udev/rules.d
SCRIPTDIR?=$(SYSCONFDIR)/sysconfig/network/scripts
UNITDIR?=$(PREFIX)/lib/systemd/system
DESTDIR?=
DEST_UDEVDIR=$(DESTDIR)$(UDEVDIR)
DEST_UDEVRULESDIR=$(DESTDIR)$(UDEVRULESDIR)
DEST_SCRIPTDIR=$(DESTDIR)$(SCRIPTDIR)
DEST_UNITDIR=$(DESTDIR)$(UNITDIR)

verSrc = $(shell cat VERSION)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' azure-bond-autoconf.spec)

ifneq "$(verSrc)" "$(verSpec)"
$(error "Version mismatch source and spec, aborting")
endif

help:
	@echo "Type 'make install' to install azure-bond-autoconf"
	@echo "Use var DESTDIR for installing into a different root."

install:
	mkdir -p $(DEST_UDEVDIR)
	mkdir -p $(DEST_UDEVRULESDIR)
	mkdir -p $(DEST_SCRIPTDIR)
	mkdir -p $(DEST_UNITDIR)
	install -m 644 60-azure-bond-autoconf.rules $(DEST_UDEVRULESDIR)
	install -m 755 azure-hv-bond-create-cfg $(DEST_SCRIPTDIR)
	install -m 755 azure-hv-bond-cleanup $(DEST_SCRIPTDIR)
	install -m 644 azure-bond-cleanup.service $(DEST_UNITDIR)
	install -m 755 hv_vf_name $(DEST_UDEVDIR)

tarball:
	@test -n "$(verSrc)"
	@ln -s . azure-bond-autoconf-$(verSrc)
	@tar chjf azure-bond-autoconf-$(verSrc).tar.bz2 \
		--warning=no-file-changed \
		--exclude azure-bond-autoconf-$(verSrc)/azure-bond-autoconf-$(verSrc) \
		--exclude azure-bond-autoconf-$(verSrc)/azure-bond-autoconf-$(verSrc).tar.bz2 \
		azure-bond-autoconf-$(verSrc)
	@rm -f azure-bond-autoconf-$(verSrc)
	@ls -l azure-bond-autoconf-$(verSrc).tar.bz2

