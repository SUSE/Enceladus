
DESTDIR=
dirs = etc srv usr
files = Makefile LICENSE README.md

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec | grep -v config)

tar:
	mkdir "$(nv)"
	cp -r $(dirs) $(files) "$(nv)"
	tar -cjf "$(nv).tar.bz2" "$(nv)"
	rm -rf "$(nv)"

install:
	cp -r $(dirs) "$(DESTDIR)/"
	mkdir -p "$(DESTDIR)/var/log/regionService"
	touch "$(DESTDIR)/var/log/regionService/regionInfo.log"
