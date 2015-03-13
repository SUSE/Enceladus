#
# spec file for package azureMetaData
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

Name:           azuremetadata
# For compatibility, remove provides 11/11/2015
Provides:       azureMetaData
Obsoletes:      azureMetaData <= 2.0.1
Version:        3.0.0
Release:        0
License:        GPL-3.0+
Summary:        Collect instance metadata in Azure
URL:            http://www.github.com:SUSE/Enceladus/azuremetadata
Group:          System/Management
Source0:        %{name}-%{version}.tar.bz2
Requires:       perl
Requires:       perl-JSON
Requires:       perl-XML-LibXML
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch:      noarch

%description
Collect instance metadada for the running instance in Azure

%prep
%setup -q

%build

%install
%make_install
pushd %{buildroot}/%{_sbindir}
# link retained for backward compatibility remove on or after 11/11/15
ln -s azuremetadata azureMetaData
popd

%files
%defattr(-,root,root,-)
%doc README.md
%{_sbindir}/azureMetaData
%{_sbindir}/azuremetadata
%{_sbindir}/AzureNetwork.pm
%{_sbindir}/AzureDisk.pm

%changelog


