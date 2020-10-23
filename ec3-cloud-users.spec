%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define underscore() %(echo %1 | sed 's/-/_/g')
%define stripc() %(echo %1 | sed 's/el7.centos/el7/')

%if 0%{?el7:1}
%define mydist %{stripc %{dist}}
%else
%define mydist %{dist}
%endif

Name:           ec3-cloud-users
Version:        0.1.0
Release:        1%{?mydist}.srce
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
%dir %{_sharedstatedir}/%{name}/
%attr(0755,root,root) %dir %{_libexecdir}/%{name}
%attr(0755,root,root) %{_libexecdir}/%{name}/*.py*

%changelog
* Fri Oct 23 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.1.0-1%{?dist}
- first release
