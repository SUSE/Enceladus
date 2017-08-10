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
Name:           python3-susepubliccloudinfo
Version:        0.4.0
Release:        1
Summary:        Query SUSE Public Cloud Info Service
License:        GPL-3.0+
Group:          System/Management
Url:            https://github.com/SUSE/Enceladus
Source0:        %{upstream_name}-%{version}.tar.bz2
Requires:       python3
Requires:       python3-docopt
Requires:       python3-lxml
Requires:       python3-requests
BuildRequires:  python3-setuptools
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

Provides:       python-susepubliccloudinfo = %{version}
Obsoletes:      python-susepubliccloudinfo < %{version}

%description
Query the SUSE Public Cloud Information Service REST API

%package amazon
Summary:        Generate Amazon specific information
Group:          System/Management
PreReq:         python3-susepubliccloudinfo = %version
Requires:       python3-boto
Requires:       python3-lxml

%description amazon
Script that generates information for Amazon to automate image inclusion
in the quick launcher and the Support matrix on the AWS web pages.

%prep
%setup -q -n %{upstream_name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/pint.1 %{buildroot}/%{_mandir}/man1
gzip %{buildroot}/%{_mandir}/man1/pint.1

%files
%defattr(-,root,root,-)
%doc LICENSE
%{_mandir}/man1/*
%dir %{python3_sitelib}/susepubliccloudinfoclient
%{python3_sitelib}/*
%{_bindir}/pint

%files amazon
%defattr(-,root,root,-)
%{_bindir}/awscsvgen

%changelog
