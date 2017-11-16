DESTDIR=
MANPATH=/usr/share/man
PREFIX=/usr
NAME=ec2uploadimg
dirs = lib man
files = Makefile README.md LICENSE ec2uploadimg setup.py

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' *.spec)
verSrc = $(shell cat lib/ec2utils/upload_VERSION)
ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

clean:
	@find . -name "*.pyc" | xargs rm -f 
	@find . -name "__pycache__" | xargs rm -rf
	@find . -name "*.cache" | xargs rm -rf
	@find . -name "*.egg-info" | xargs rm -rf

pep8: clean
	@pep8 -v --statistics lib/ec2utils/*

tar:
	mkdir -p "$(NAME)-$(verSrc)"/man/man1
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -cjf "$(NAME)-$(verSrc).tar.bz2" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"

install:
	python setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
	install -d -m 755 "$(DESTDIR)"/"$(MANDIR)"/man1
	install -m 644 man/man1/ec2uploadimg.1 "$(DESTDIR)"/"$(MANDIR)"/man1
	gzip "$(DESTDIR)"/"$(MANDIR)"/man1/ec2uploadimg.1

pypi:
	mkdir -p "$(NAME)-$(verSrc)"/man/man1
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -czf "$(NAME)-$(verSrc).tar.gz" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"
	mkdir dist
	mv "$(NAME)-$(verSrc).tar.gz" dist
