DESTDIR=
MANPATH=/usr/share/man
PREFIX=/usr
NAME=susepubliccloudinfo
dirs = bin lib man
files = Makefile README.md LICENSE setup.py

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' *.spec)
verSrc = $(shell cat lib/susepubliccloudinfoclient/version.py | \
	grep VERSION | awk -F\' '{ print $$2 }' | tr -d '\n')

ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

tar:
	mkdir -p "$(NAME)-$(verSrc)"/man/man1
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -cjf "$(NAME)-$(verSrc).tar.bz2" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"

install:
	python setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
	install -d -m 755 "$(DESTDIR)"/"$(MANDIR)"/man1
	install -m 644 man/man1/pint.1 "$(DESTDIR)"/"$(MANDIR)"/man1
	gzip "$(DESTDIR)"/"$(MANDIR)"/man1/pint.1

pep8:
	tools/run-pep8

.PHONY: test
test:
	nosetests --with-coverage --cover-erase --cover-package=lib.susepubliccloudinfoclient --cover-xml
	tools/coverage-check

coverage:
	nosetests --with-coverage --cover-erase --cover-package=lib.susepubliccloudinfoclient --cover-xml
	mv test/unit/coverage.xml test/unit/coverage.reference.xml

list_tests:
	@for i in test/unit/*_test.py; do basename $$i;done | sort

%.py:
	nosetests $@

