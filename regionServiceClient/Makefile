
DESTDIR=
PREFIX=
dirs = etc usr
files = Makefile README LICENSE setup.py

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec | grep -v config | grep -v plugin)

tar:
	mkdir "$(nv)"
	cp -r $(dirs) lib $(files) "$(nv)"
	tar -cjf "$(nv).tar.bz2" "$(nv)"
	rm -rf "$(nv)"

install:
	cp -r $(dirs) "$(DESTDIR)/"
	python setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
