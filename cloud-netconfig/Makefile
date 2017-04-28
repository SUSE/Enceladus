.PHONY: common help install-azure install-ec2
PREFIX?=/usr
SYSCONFDIR?=/etc
UDEVRULESDIR?=$(PREFIX)/lib/udev/rules.d
NETCONFDIR?=$(SYSCONFDIR)/netconfig.d
SCRIPTDIR?=$(SYSCONFDIR)/sysconfig/network/scripts
DESTDIR?=
DNETCONFDIR=$(DESTDIR)$(NETCONFDIR)
DUDEVRULESDIR=$(DESTDIR)$(UDEVRULESDIR)
DSCRIPTDIR=$(DESTDIR)$(SCRIPTDIR)


verSrc = $(shell cat VERSION)
verSpecEC2 = $(shell rpm -q --specfile --qf '%{VERSION}' cloud-netconfig-ec2.spec)
verSpecAz = $(shell rpm -q --specfile --qf '%{VERSION}' cloud-netconfig-azure.spec)

ifneq "$(verSrc)" "$(verSpecEC2)"
$(error "Version mismatch source and EC2 spec, aborting")
endif
ifneq "$(verSrc)" "$(verSpecAz)"
$(error "Version mismatch source and Azure spec, aborting")
endif

help:
	@echo "Type 'make install-ec2' for installation on EC2"
	@echo "Type 'make install-azure' for installation on Azure"
	@echo "Use var DESTDIR for installing into a different root."

common:
	mkdir -p $(DNETCONFDIR)
	mkdir -p $(DUDEVRULESDIR)
	mkdir -p $(DSCRIPTDIR)
	install -m 644 common/75-cloud-persistent-net-generator.rules $(DUDEVRULESDIR)
	install -m 755 common/cloud-netconfig $(DNETCONFDIR)
	install -m 755 common/cloud-netconfig-cleanup $(DSCRIPTDIR)
	install -m 755 common/cloud-netconfig-hotplug $(DSCRIPTDIR)

install-azure: common
	install -m 644 azure/51-cloud-netconfig-hotplug.rules $(DUDEVRULESDIR)
	install -m 755 azure/functions.cloud-netconfig $(DSCRIPTDIR)

install-ec2: common
	install -m 644 ec2/51-cloud-netconfig-hotplug.rules $(DUDEVRULESDIR)
	install -m 755 ec2/functions.cloud-netconfig $(DSCRIPTDIR)

tarball:
	@test -n "$(verSrc)"
	@ln -s . cloud-netconfig-$(verSrc)
	@tar chjf cloud-netconfig-$(verSrc).tar.bz2 \
		--warning=no-file-changed \
		--exclude cloud-netconfig-$(verSrc)/cloud-netconfig-$(verSrc) \
		--exclude cloud-netconfig-$(verSrc)/cloud-netconfig-$(verSrc).tar.bz2 \
		cloud-netconfig-$(verSrc)
	@rm -f cloud-netconfig-$(verSrc)
	@ls -l cloud-netconfig-$(verSrc).tar.bz2
