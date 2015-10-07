#
# spec file for package python-susepubcloudinfo
#
# Copyright (c) 2015 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


%define upstream_name susepubliccloudinfo
Name:           python-susepubliccloudinfo
Version:        0.2.0
Release:        1
Summary:        Query SUSE Public Cloud Info Service
License:        GPL-3.0+
Group:          System/Management
Url:            https://github.com/SUSE/Enceladus
Source0:        %{upstream_name}-%{version}.tar.bz2
Requires:       python
Requires:       python-docopt
Requires:       python-requests
BuildRequires:  python-setuptools
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%else
BuildArch:      noarch
%endif

%description
Query the SUSE Public Cloud Information Service REST API

%package amazon
Summary:        Generate Amazon specific information
Group:          System/Management
PreReq:         python-susepubliccloudinfo = %version
Requires:       python-boto
Requires:       python-lxml

%description amazon
Script that generates information for Amazon to automate image inclusion
in the quick launcher and the Support matrix on the AWS web pages.

%prep
%setup -q -n %{upstream_name}-%{version}

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/pint.1 %{buildroot}/%{_mandir}/man1
gzip %{buildroot}/%{_mandir}/man1/pint.1

%files
%defattr(-,root,root,-)
%doc LICENSE
%{_mandir}/man1/*
%dir %{python_sitelib}/susepubliccloudinfoclient
%{python_sitelib}/*
%{_bindir}/pint

%files amazon
%{_bindir}/awscsvgen

%changelog
