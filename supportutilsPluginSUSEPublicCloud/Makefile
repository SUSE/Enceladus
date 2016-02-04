DESTDIR=
PREFIX=/usr
MANPATH=$(PREFIX)/share/man
SUPPORTCONFPATH=$(PREFIX)/lib/supportconfig
PLUGINPATH=$(SUPPORTCONFPATH)/plugins
RESOURCEPATH=$(SUPPORTCONFPATH)/resources
NAME=supportutils-plugin-suse-public-cloud
dirs = man supportconfig
files = Makefile README.md LICENSE

verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' *.spec)

tar:
	mkdir -p "$(NAME)-$(verSpec)"
	cp -r $(dirs) $(files) "$(NAME)-$(verSpec)"
	tar -cjf "$(NAME)-$(verSpec).tar.bz2" "$(NAME)-$(verSpec)"
	rm -rf "$(NAME)-$(verSpec)"

install:
	install -d -m 755 $(DESTDIR)/$(MANPATH)/man8
	install -d -m 755 $(DESTDIR)/$(PLUGINPATH)
	install -d -m 755 $(DESTDIR)/$(RESOURCEPATH)
	install -m 644 man/man8/suse-public-cloud.8 $(DESTDIR)/$(MANPATH)/man8
	install supportconfig/plugins/* $(DESTDIR)/$(PLUGINPATH)
	install -m 644 supportconfig/resources/* $(DESTDIR)/$(RESOURCEPATH)
	gzip $(DESTDIR)/$(MANPATH)/man8/suse-public-cloud.8

