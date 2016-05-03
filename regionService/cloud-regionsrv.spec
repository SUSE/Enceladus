#
# spec file for package cloud-regionsrv
# this code base is under development
#
# Copyright (c) 2016 SUSE LLC
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

Name:           cloud-regionsrv
Version:        7.0.0
Release:        0
License:        GPL-3.0+
Summary:        Cloud Environment Region Service
URL:            https://github.com/SUSE/Enceladus
Group:          Productivity/Networking/Web/Servers
Source0:        %{name}-%{version}.tar.bz2
Requires:       apache2
Requires:       apache2-mod_wsgi     >= 4.2.8
Requires:       openssl
Requires:       python
Requires:       python-Flask
Requires:       python-netaddr
Requires:       python-pyOpenSSL
Requires:       cloud-region-config
Requires(pre):  pwdutils
Recommends:     cspApacheAccessConfig
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch:      noarch

%description
Cloud region resolver service, returns SMT server information
for the region based on the client IP address.

%package generic-config
Version:      1.0.0
License:      GPL-3.0+
Summary:      Cloud Environment Region Service Configuration
Group:        Productivity/Networking/Web/Servers
Provides:     cloud-region-config
Conflicts:    otherproviders(cloud-region-config)

%description generic-config
Generic configuration for the region service

%prep
%setup -q

%build

%install
%make_install

%pre
if [ ! `grep regionsrv /etc/group 2>&1 /dev/null` ]; then
    /usr/sbin/groupadd --system regionsrv  2> /dev/null
fi
if [ ! `grep regionsrv /etc/passwd 2>&1 /dev/null` ]; then
    /usr/sbin/useradd -r -g regionsrv -s /bin/false -c "Cloud Region Service" \
        -d /var/lib/regionsrv regionsrv 2> /dev/null || :
else
    /usr/sbin/usermod -g regionsrv -G regionsrv -s /bin/false regionsrv \
      2> /dev/null
fi

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%config(noreplace) %{_sysconfdir}/apache2/vhosts.d/regionsrv_vhost.conf
%config %{_sysconfdir}/logrotate.d/regionInfo.lr
%attr(755,regionsrv,regionsrv) %dir /srv/www/regionService
/srv/www/regionService/regionInfo.wsgi
/srv/www/regionService/regionInfo.py
%attr(755,regionsrv,regionsrv) %dir /var/log/regionService
%attr(644,regionsrv,regionsrv) %ghost /var/log/regionService/regionInfo.log
%dir %{_sysconfdir}/apache2
%dir %{_sysconfdir}/apache2/vhosts.d
%dir %{_sysconfdir}/regionService
/usr/sbin/genRegionServerCert

%files generic-config
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/regionService/regionData.cfg
%config(noreplace) %{_sysconfdir}/regionService/regionInfo.cfg


%changelog


