
DESTDIR=
PREFIX=
dirs = etc usr
files = Makefile README LICENSE setup.py

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}|' *.spec | cut -d'|' -f1)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}|' *.spec | cut -d'|' -f1)
verSrc = $(shell cat lib/cloudregister/VERSION)
ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

tar:
	mkdir "$(nv)"
	cp -r $(dirs) lib $(files) "$(nv)"
	tar -cjf "$(nv).tar.bz2" "$(nv)"
	rm -rf "$(nv)"

install:
	cp -r $(dirs) "$(DESTDIR)/"
	python setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
