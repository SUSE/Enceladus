DESTDIR=
dirs = usr
files = Makefile README.md LICENSE

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec)

tar:
	mkdir -p "$(nv)"
	cp -r $(dirs) $(files) "$(nv)"
	tar -cjf "$(nv).tar.bz2" "$(nv)"
	rm -rf "$(nv)"

install:
	install -d -m 755 "$(DESTDIR)"
	cp -r $(dirs) "$(DESTDIR)"
