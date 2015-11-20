#
# spec file for package docker-img-store-setup
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


Name:           docker-img-store-setup
Version:        1.0.0
Release:        0
Summary:        Setup btrfs image store for docker
License:        GPL-3.0+
Group:          System/Management
Url:            https://github.com/SUSE/Enceladus
Source0:        %{name}-%{version}.tar.bz2
Requires:       btrfsprogs
Requires:       qemu-tools
BuildRequires:  systemd
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
Set up a 100 GB thinly provisioned storage file for docker image storage

%prep
%setup -q

%build

%install
make install DESTDIR=%{buildroot}

%pre
%service_add_pre docker-img-store-setup.service

%post
%service_add_post docker-img-store-setup.service

%preun
%service_del_preun docker-img-store-setup.service

%postun
%service_del_postun docker-img-store-setup.service

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%{_sbindir}/docker-img-store-setup
%{_unitdir}/docker-img-store-setup.service

%changelog

