#
# spec file for package azure-bond-autoconf
#
# Copyright (c) 2017 SUSE Linux GmbH, Nuernberg, Germany.
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

%define base_name azure-bond-autoconf

Name:           %{base_name}
Version:        0.2
Release:        0
License:        GPL-3.0+
Summary:        Network bonding configuration scripts for Microsoft Azure
Url:            https://github.com/SUSE/Enceladus
Group:          System/Management
Source0:        %{base_name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
BuildRequires:  udev
Requires:       udev
%if 0%{?suse_version} >= 1210
BuildRequires: systemd-rpm-macros
%endif
%{?systemd_requires}

%define udevdir %{_usr}/lib/udev

%description
This package contains scripts for automatically configuring Hyper-V single
root I/O network interfaces (Accelerated Networking) for bonding with their
standard virtual interface peers.

%prep
%setup -q -n %{base_name}-%{version}

%build

%install
make install \
  DESTDIR=%{buildroot} \
  PREFIX=%{_usr} \
  SYSCONFDIR=%{_sysconfdir} \
  UDEVDIR=%{udevdir} \
  UDEVRULESDIR=%{_udevrulesdir} \
  UNITDIR=%{_unitdir}

%pre
%service_add_pre azure-bond-cleanup.service

%post
%service_add_post azure-bond-cleanup.service

%preun
%service_del_preun azure-bond-cleanup.service

%postun
%service_del_postun azure-bond-cleanup.service

%files
%defattr(-,root,root)
%{_sysconfdir}/sysconfig/network/scripts/*
%{_udevrulesdir}/60-azure-bond-autoconf.rules
%{udevdir}/hv_vf_name
%{_unitdir}/azure-bond-cleanup.service
%doc README.md LICENSE

%changelog
