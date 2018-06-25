Summary: Openfire XMPP Server
Name: openfire
Version: 4.2.3
Release: 5%{dist}
BuildRoot: %{_builddir}/%{name}-root
Source0: openfire_src_4_2_3.tar.gz
Source1: openfire-start
Source2: openfire.service
Source3: openfire-tmpfiles.conf
Source4: openfire-sysconfig
Source5: openfire.logrotate
Source100: ofmeet.jar
Source101: offocus.jar
Source102: fastpath.jar
Source103: certificateManager.jar
Requires: java-headless >= 1:1.8.0
Requires: systemd
Requires: logrotate
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(pre): /usr/sbin/useradd
Requires(pre): /usr/sbin/groupadd
BuildRequires: ant
BuildRequires: systemd
Group: Applications/Communications
Vendor: Igniterealtime Community
Packager: Igniterealtime Community
License: Apache license v2.0
AutoReqProv: no
URL: http://www.igniterealtime.org/

%define prefix %{_datadir}
%define homedir %{prefix}/openfire
# couldn't find another way to disable the brp-java-repack-jars which was called in __os_install_post
%define __os_install_post %{nil}
%define debug_package %{nil}

%description
Openfire is a leading Open Source, cross-platform IM server based on the
XMPP (Jabber) protocol. It has great performance, is easy to setup and use,
and delivers an innovative feature set.

%prep
%setup -q -n openfire_src

%build
cd build
ant openfire
ant -Dplugin=search plugin
cd ..

%install
# Prep the install location.
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{prefix}
# Copy over the main install tree.
cp -R target/openfire $RPM_BUILD_ROOT%{homedir}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/openfire

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sbindir}/openfire-start

# Set up the init script.
mkdir -p -m 755 $RPM_BUILD_ROOT/var/run/openfire
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/systemd/system/openfire.service
install -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/openfire.conf

# Set up the sysconfig file.
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -D -m 644 %{SOURCE4} $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openfire

# Make the startup script executable.
chmod 755 $RPM_BUILD_ROOT%{homedir}/bin/openfire.sh

# Copy over the documentation
# This is done via the %doc in the file manifest
# Copy over the i18n files
cp -R src/i18n $RPM_BUILD_ROOT%{homedir}/resources/i18n

# Move over the embedded db viewer pieces
mv $RPM_BUILD_ROOT%{homedir}/bin/extra/embedded-db.rc $RPM_BUILD_ROOT%{homedir}/bin
mv $RPM_BUILD_ROOT%{homedir}/bin/extra/embedded-db-viewer.sh $RPM_BUILD_ROOT%{homedir}/bin

# Add symlink for log files
mkdir -p -m 755 $RPM_BUILD_ROOT/var/log/openfire
rmdir $RPM_BUILD_ROOT%{homedir}/logs
ln -sf /var/log/openfire $RPM_BUILD_ROOT%{homedir}/logs

# 3rd party jar files go straight to plugins folder
install -D -m 644 %{SOURCE100} $RPM_BUILD_ROOT%{homedir}/plugins
install -D -m 644 %{SOURCE101} $RPM_BUILD_ROOT%{homedir}/plugins
install -D -m 644 %{SOURCE102} $RPM_BUILD_ROOT%{homedir}/plugins
install -D -m 644 %{SOURCE103} $RPM_BUILD_ROOT%{homedir}/plugins

# Hotdeploy certificate manager plugin
mkdir -p $RPM_BUILD_ROOT%{homedir}/resources/security/hotdeploy

# We don't really need any of these things.
rm -rf $RPM_BUILD_ROOT%{homedir}/bin/extra
rm -f $RPM_BUILD_ROOT%{homedir}/bin/*.bat
rm -rf $RPM_BUILD_ROOT%{homedir}/resources/nativeAuth/osx-ppc
rm -rf $RPM_BUILD_ROOT%{homedir}/resources/nativeAuth/win32-x86
rm -f $RPM_BUILD_ROOT%{homedir}/lib/*.dll

%clean
rm -rf $RPM_BUILD_ROOT

%pre
/usr/sbin/useradd -c "Openfire" -s /sbin/nologin -r -d %{homedir} openfire 2> /dev/null
exit 0

%preun
%systemd_preun openfire.service
exit 0

%postun
%systemd_postun_with_restart openfire.service
exit 0

%systemd_post openfire.service
exit 0

%files
%defattr(-,openfire,openfire)
%attr(755, openfire, openfire) %dir %{homedir}
%dir %{homedir}/bin
%{homedir}/bin/openfire.sh
%{homedir}/bin/openfirectl
%config(noreplace) %{homedir}/bin/embedded-db.rc
%{homedir}/bin/embedded-db-viewer.sh
%dir %{homedir}/conf
%config(noreplace) %{homedir}/conf/openfire.xml
%config(noreplace) %{homedir}/conf/security.xml
%config(noreplace) %{homedir}/conf/crowd.properties
%dir %{homedir}/lib
%{homedir}/lib/*.jar
%config(noreplace) %{homedir}/lib/log4j.xml
# This is symlink to /var/log/openfire
%{homedir}/logs
%dir %{homedir}/plugins
%{homedir}/plugins/search.jar
%{homedir}/plugins/fastpath.jar
%{homedir}/plugins/offocus.jar
%{homedir}/plugins/ofmeet.jar
%{homedir}/plugins/certificateManager.jar
%dir %{homedir}/plugins/admin
%{homedir}/plugins/admin/*
%dir %{homedir}/resources
%dir %{homedir}/resources/database
%{homedir}/resources/database/*.sql
%dir %{homedir}/resources/database/upgrade
%dir %{homedir}/resources/database/upgrade/*
%{homedir}/resources/database/upgrade/*/*
%dir %{homedir}/resources/i18n
%{homedir}/resources/i18n/*
%dir %{homedir}/resources/nativeAuth
%dir %{homedir}/resources/nativeAuth/linux-i386
%{homedir}/resources/nativeAuth/linux-i386/*
%dir %{homedir}/resources/security
%dir %{homedir}/resources/security/hotdeploy
%dir %{homedir}/resources/spank
%{homedir}/resources/spank/index.html
%dir %{homedir}/resources/spank/WEB-INF
%{homedir}/resources/spank/WEB-INF/web.xml
%config(noreplace) %{homedir}/resources/security/keystore
%config(noreplace) %{homedir}/resources/security/truststore
%config(noreplace) %{homedir}/resources/security/client.truststore

%doc %attr(-,root,root) documentation/dist/LICENSE.html
%doc %attr(-,root,root) documentation/dist/README.html
%doc %attr(-,root,root) documentation/dist/changelog.html
# System
%config(noreplace) %{_sysconfdir}/sysconfig/openfire
%dir /var/run/openfire
%dir /var/log/openfire
%attr(-,root,root) /usr/lib/systemd/system/openfire.service
%attr(-,root,root) /usr/lib/tmpfiles.d/openfire.conf
%attr(-,root,root) %{_sbindir}/openfire-start
%attr(-,root,root) %{_sysconfdir}/logrotate.d/openfire

%changelog
* Mon Jun 25 2018 Guus der Kinderen <guus@goodbytes.nl> - 4.2.3-5
Updated ofmeet plugin to 0.9.4
Updated offocus plugin to 0.9.4

* Thu Mar 29 2018 Guus der Kinderen <guus@goodbytes.nl> - 4.2.3-1
Updated to 4.2.3

* Thu Mar 8 2018 Guus der Kinderen <guus@goodbytes.nl> - 4.2.2-3
Updated ofmeet plugin to 0.9.3
Updated offocus plugin to 0.9.3

* Tue Feb 13 2018 eGloo <developer@egloo.ca> - 4.2.2-2
Updated to 4.2.2

* Wed Dec 13 2017 eGloo <developer@egloo.ca> - 4.2.1-1
Updated to 4.2.1

* Fri Dec 8 2017 Guus der Kinderen <guus@goodbytes.nl> - 4.2.0-1
Updated to 4.2.0

* Thu Nov 30 2017 eGloo <developer@egloo.ca> - 4.2.0-1.beta
Updated to 4.2.0 Beta
Added certificate manager plugin

* Thu Oct 19 2017 eGloo <developer@egloo.ca> - 4.1.6-1
Harmonized spec file with upstream
Added logrotate
Updated to 4.1.6

* Thu Aug 31 2017 eGloo <developer@egloo.ca> - 4.1.5-5
Updated spec file manifest

* Tue Aug 22 2017 eGloo <developer@egloo.ca> - 4.1.5-4
Changed plugin handling on upgrades

* Mon Aug 21 2017 eGloo <developer@egloo.ca> - 4.1.5-3
Added offocus plugin
Updated ofmeet plugin to 0.9.2

* Mon Aug 14 2017 eGloo <developer@egloo.ca> - 4.1.5-2
4.1.5 Build

* Fri Dec 23 2016 eGloo <developer@egloo.ca> - 4.1.0-3
Avoided using _tmpfilesdir and _unitdir macros

* Wed Dec 21 2016 eGloo <developer@egloo.ca> - 4.1.0-2
Updated to match upstream distro standards

* Wed Dec 21 2016 eGloo <developer@egloo.ca> - 4.1.0-1
First release
