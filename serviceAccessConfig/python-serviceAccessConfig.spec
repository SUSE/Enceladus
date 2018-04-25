#
# spec file for package python-serviceAccessConfig.spec
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


Name:           python-serviceAccessConfig
Version:        0.5.2
Release:        0
Summary:        Generate access controll
License:        GPL-3.0+
Group:          System/Management
Url:            https://github.com/SUSE/Enceladus
Source0:        serviceAccessConfig-%{version}.tar.bz2
# Conflict although the package was never released in OBS, or through SLES
# it was distributed to CSPs and deployed to SUSE operated infrastructure
# servers
Conflicts:      cspInfraServerAccessConfig
%if 0%{?suse_version} > 1140
BuildRequires: systemd
%endif
%{?systemd_requires}
%if 0%{?suse_version} < 1140
Requires:      insserv
Requires:      sysvinit
%endif
Requires:       python-base
Requires:       python-docopt
Requires:       python-requests
BuildRequires:  python-mock
BuildRequires:  python-pytest
BuildRequires:  python-requests
BuildRequires:  python-setuptools
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%else
BuildArch:      noarch
%endif

%description
Automatically generate access control configuration for configured services.
Supported services are Apache and HAProxy.

%package test
Summary:        Tests for python-serviceAccessConfig
Group:          Development/Libraries/Python
PreReq:         python-serviceAccessConfig = %version
Requires:       python-mock
Requires:       python-pytest

%description test
Package provides the unit tests for python-serviceAccessConfig

%prep
%setup -q -n serviceAccessConfig-%{version}

%build
python setup.py build

%install
# Code
python setup.py install --prefix=%{_prefix} --root=%{buildroot}
mkdir -p %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/* %{buildroot}%{_sbindir}
# Man page
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/serviceAccessConfig.1 %{buildroot}/%{_mandir}/man1
gzip %{buildroot}/%{_mandir}/man1/serviceAccessConfig.1
# Tests
mkdir -p %{buildroot}%{python_sitelib}/tests/serviceAccessConfig
cp -r tests/* %{buildroot}%{python_sitelib}/tests/serviceAccessConfig
# Init system
%if 0%{?suse_version} < 1140
mkdir -p %{buildroot}%{_sysconfdir}
cp -r etc/init.d %{buildroot}%{_sysconfdir}
%else
mkdir -p %{buildroot}/%{_unitdir}
cp -r usr/lib/systemd/system/* %{buildroot}/%{_unitdir}
%endif

%check
py.test tests/unit/test_*.py

%pre
%if 0%{?suse_version} > 1140
    %service_add_pre serviceAccessConfig.service
%endif

%post
%if 0%{?suse_version} > 1140
    %service_add_post serviceAccessConfig.service
%endif

%preun
%if 0%{?suse_version} > 1140
    %service_del_preun serviceAccessConfig.service
%else
    %stop_on_removal
%endif

%postun
%if 0%{?suse_version} > 1140
    %service_del_postun serviceAccessConfig.service
%else
    %insserv_cleanup
%endif


%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%exclude %{python_sitelib}/tests/*
%{_mandir}/man*/*
%{python_sitelib}/*
%{_sbindir}/*
%if 0%{?suse_version} > 1140
%{_unitdir}/serviceAccessConfig.service
%else
%attr(0755,root,root) %{_initddir}/serviceAccessConfig
%endif

%files test
%defattr(-,root,root,-)
%{python_sitelib}/tests/*

%changelog
