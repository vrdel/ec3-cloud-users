%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define underscore() %(echo %1 | sed 's/-/_/g')
%define stripc() %(echo %1 | sed 's/el7.centos/el7/')

%if 0%{?el7:1}
%define mydist %{stripc %{dist}}
%else
%define mydist %{dist}
%endif

Name:           ec3-cloud-users
Version:        0.1.2
Release:        2%{?mydist}.srce
Summary:        Scripts for opening user accounts on EC3 spawned clusters on SRCE HTC IaaS Cloud
Group:          Applications/System
License:        GPL
URL:            https://github.com/vrdel/isabella-users
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel
Requires:       python-unidecode
Requires:       libuser-python
Requires:       python-argparse
Requires:       python-requests
Requires:       python-dns

%description
Scripts for opening user accounts on EC3 spawned clusters on SRCE HTC IaaS Cloud

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT --record=INSTALLED_FILES
install --directory --mode 755 $RPM_BUILD_ROOT/%{_localstatedir}/log/%{name}/
install --directory --mode 755 $RPM_BUILD_ROOT/%{_sharedstatedir}/%{name}/
install --directory %{buildroot}/%{_libexecdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/%{name}/config.conf
%dir %{python_sitelib}/%{underscore %{name}}/
%{python_sitelib}/%{underscore %{name}}/*.py[co]
%dir %{_localstatedir}/log/%{name}/
%attr(0755,root,root) %dir %{_libexecdir}/%{name}
%attr(0755,root,root) %{_libexecdir}/%{name}/*.py*
%attr(0644,root,root) %{_sysconfdir}/cron.d/*
%attr(0700,root,root) %dir %{_sharedstatedir}/%{name}/

%changelog
* Sun Sep 19 2021 Daniel Vrcic <dvrcic@srce.hr> - 0.1.2-2%{?dist}
- load users from csv
- fix homedir reference
* Fri Oct 23 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.1.1-3%{?dist}
- refined mail template
* Fri Oct 23 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.1.1-2%{?dist}
- do not Cc to same From address
* Fri Oct 23 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.1.1-1%{?dist}
- DNS resolve to manually set local_hostname for SMTP
* Fri Oct 23 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.1.0-1%{?dist}
- first release
