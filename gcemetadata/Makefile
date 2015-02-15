DESTDIR=
PREFIX=
NAME=gcemetadata
dirs = lib
files = Makefile README.md LICENSE gcemetadata setup.py

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' *.spec)
verSrc = $(shell cat lib/gcemetadata/VERSION)
ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

tar:
	mkdir "$(NAME)-$(verSrc)"
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -cjf "$(NAME)-$(verSrc).tar.bz2" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"

install:
	python setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
