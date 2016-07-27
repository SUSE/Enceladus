#
# spec file for package supportutils-plugin-suse-public-cloud
#
# Copyright (c) 2016 SUSE LINUX Products GmbH, Nuernberg, Germany.
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

Name:           supportutils-plugin-suse-public-cloud
Version:        1.0.1
Release:        0
Summary:        Public Cloud plugin for supportconfig
License:        GPL-2.0+
Group:          System/Monitoring
Url:            https://github.com/SUSE/Enceladus
Source0:        %{name}-%{version}.tar.bz2
Requires:       supportutils
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
A plugin for the supportutils utility to collect system information from
running instances in a Public Cloud Framework that originated from SUSE
published and maintained images.

%prep
%setup -q -n %{name}-%{version}

%build


%install
make install DESTDIR=%{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE README.md 
%{_mandir}/man*/*
/usr/lib/supportconfig/
