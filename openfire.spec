Summary: Openfire XMPP Server
Name: openfire
Version: 4.1.0
Release: 3
BuildRoot: %{_builddir}/%{name}-root
Source0: openfire_src_4_1_0.tar.gz
Source1: openfire-start
Source2: openfire.service
Source3: openfire-tmpfiles.conf
Source4: openfire-sysconfig
Requires: java-headless >= 1:1.7.0
Requires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(pre): /usr/sbin/useradd
Requires(pre): /usr/sbin/groupadd
BuildRequires: ant
Group: Applications/Communications
Vendor: Igniterealtime Community
Packager: Igniterealtime Community
License: Apache license v2.0
AutoReqProv: no
URL: http://www.igniterealtime.org/

%define homedir %{_datadir}/openfire
# couldn't find another way to disable the brp-java-repack-jars which was called in __os_install_post
%define __os_install_post %{nil}

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
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_datadir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p -m 755 $RPM_BUILD_ROOT/var/run/openfire
mkdir -p -m 755 $RPM_BUILD_ROOT/var/log/openfire

# Copy over the main install tree.
cp -R target/openfire $RPM_BUILD_ROOT%{homedir}

# Startup script, systemd, and tmpfiles.
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sbindir}/openfire-start
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/systemd/system/openfire.service
install -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/openfire.conf
install -D -m 644 %{SOURCE4} $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openfire

# Make the startup script executable.
chmod 755 $RPM_BUILD_ROOT%{homedir}/bin/openfire.sh

# Copy over the i18n files
cp -R src/i18n $RPM_BUILD_ROOT%{homedir}/resources/i18n

# Move over the embedded db viewer pieces
mv $RPM_BUILD_ROOT%{homedir}/bin/extra/embedded-db.rc $RPM_BUILD_ROOT%{homedir}/bin
mv $RPM_BUILD_ROOT%{homedir}/bin/extra/embedded-db-viewer.sh $RPM_BUILD_ROOT%{homedir}/bin

# Add symlink for log files
rmdir $RPM_BUILD_ROOT%{homedir}/logs
ln -sf /var/log/openfire $RPM_BUILD_ROOT%{homedir}/logs

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

%post
%systemd_post openfire.service
exit 0

%files
%defattr(-,root,root)
# Docs
%doc documentation/dist/README.html documentation/dist/LICENSE.html documentation/dist/changelog.html
# Home directory must be writeable by openfire
%{homedir}
%attr(-,openfire,openfire) %dir %{homedir}
# Openfire writeable directories
%attr(-,openfire,openfire) %{homedir}/conf
%attr(-,openfire,openfire) %{homedir}/plugins
%attr(-,openfire,openfire) %{homedir}/resources/security
# Openfire writeable files
%attr(-,openfire,openfire) %config(noreplace) %{homedir}/bin/embedded-db.rc
%attr(-,openfire,openfire) %config(noreplace) %{homedir}/lib/log4j.xml
# System files
%config(noreplace) %{_sysconfdir}/sysconfig/openfire
%attr(0755,openfire,openfire) %dir /var/run/openfire
%attr(0755,openfire,openfire) %dir /var/log/openfire
/usr/lib/systemd/system/openfire.service
/usr/lib/tmpfiles.d/openfire.conf
%{_sbindir}/openfire-start

%changelog
* Fri Dec 23 2016 eGloo <developer@egloo.ca> - 4.1.0-3
Avoided using _tmpfilesdir and _unitdir macros

* Wed Dec 21 2016 eGloo <developer@egloo.ca> - 4.1.0-2
Updated to match upstream distro standards

* Wed Dec 21 2016 eGloo <developer@egloo.ca> - 4.1.0-1
First release
