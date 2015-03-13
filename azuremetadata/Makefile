DESTDIR=
dirs = usr
files = Makefile README.md

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}' *.spec)

tar:
	mkdir "$(nv)"
	cp -r $(dirs) $(files) "$(nv)"
	tar -cjf "$(nv).tar.bz2" "$(nv)"
	rm -rf "$(nv)"

install:
	cp -r $(dirs) "$(DESTDIR)/"

