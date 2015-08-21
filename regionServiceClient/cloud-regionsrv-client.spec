#
# spec file for package cloud-regionsrv-client
# this code base is under development
#
# Copyright (c) 2015 SUSE LLC
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

%define base_version 6.4.0
Name:           cloud-regionsrv-client
Version:        %{base_version}
Release:        0
License:        LGPL-3.0
Summary:        Cloud Environment Guest Registration
URL:            http://www.github.com:SUSE/Enceladus
Group:          Productivity/Networking/Web/Servers
Source0:        %{name}-%{version}.tar.bz2
Requires:       cloud-regionsrv-client-config
Requires:       python
Requires:       python-lxml
Requires:       python-requests
Requires:       regionsrv-certs
%if 0%{?suse_version} > 1140
Requires:       SUSEConnect
Requires:       python-M2Crypto
BuildRequires:  systemd
%endif
%{?systemd_requires}
%if 0%{?suse_version} < 1140
Requires:       insserv
Requires:       python-m2crypto
Requires:       sysvinit
Requires:       suseRegister
%endif
BuildRequires:  python
BuildRequires:  python-setuptools
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root


%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%else
BuildArch:      noarch
%endif

%description
Obtain cloud SMT server information from the region server configured in
/etc/regionserverclnt.cfg

%package generic-config
Version:      1.0.0
License:      LGPL-3.0
Summary:      Cloud Environment Guest Registration Configuration
Group:        Productivity/Networking/Web/Servers
Provides:     cloud-regionsrv-client-config
Conflicts:    otherproviders(cloud-regionsrv-client-config)

%description generic-config
Generic configuration for the registration client

%package plugin-gce
Version:      1.0.0
License:      LGPL-3.0
Summary:      Cloud Environment Guest Registration Plugin for GCE
Group:        Productivity/Networking/Web/Servers
Requires:     cloud-regionsrv-client >= 6.0.0

%description plugin-gce
Guest registration plugin for Google Compute Engine

%prep
%setup -q

%build
python setup.py build

%install
cp -r etc %{buildroot}
cp -r usr %{buildroot}
python setup.py install --prefix=%{_prefix}  --root=%{buildroot}
%if 0%{?suse_version} < 1140
    rm -rf %{buildroot}/usr/lib/systemd
    pushd %{buildroot}
    ln -s %{_initddir}/guestregister %{buildroot}/%{_sbindir}/rcguestregister 
    popd
%else
%if 0%{?suse_version} < 1230
    mkdir -p %{buildroot}/%{_unitdir}
    mv %{buildroot}/usr/lib/systemd/system/* %{buildroot}/%{_unitdir}
    rm -rf %{buildroot}/usr/lib/systemd
%endif
    rm -rf %{buildroot}/etc/init.d
%endif

%pre
%if 0%{?suse_version} > 1140
    %service_add_pre guestregister.service
%endif

%post
%if 0%{?suse_version} > 1140
    %service_add_post guestregister.service
%endif

%preun
%if 0%{?suse_version} > 1140
    %service_del_preun guestregister.service
%else
    %stop_on_removal
%endif

%postun
%if 0%{?suse_version} > 1140
    %service_del_postun guestregister.service
%else
    %insserv_cleanup
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README LICENSE
%{_sbindir}/registercloudguest
%if 0%{?suse_version} > 1140
%{_unitdir}/guestregister.service
%else
%attr(0755,root,root) %{_initddir}/guestregister
%{_sbindir}/rcguestregister
%endif

%files generic-config
%defattr(-,root,root,-)
%config %{_sysconfdir}/regionserverclnt.cfg

%files plugin-gce
%defattr(-,root,root,-)
%dir %{python_sitelib}/cloudregister-%{base_version}-py%{py_ver}.egg-info
%dir %{python_sitelib}/cloudregister/
%{python_sitelib}/cloudregister-%{base_version}-py%{py_ver}.egg-info/*
%{python_sitelib}/cloudregister/*

%changelog


