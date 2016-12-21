%define OPENFIRE_VERSION 4.0.3
%define OPENFIRE_SOURCE v4.0.3.tar.gz
%define OPENFIRE_RELEASE 1
%define OPENFIRE_BUILDDATE Wed Nov 23 2016
%define OPENFIRE_REPOVERSION FIXME

Summary: Openfire XMPP Server
Name: openfire
Version: %{OPENFIRE_VERSION}
Release: %{OPENFIRE_RELEASE}
BuildRoot: %{_builddir}/%{name}-root
Source0: %{OPENFIRE_SOURCE}
Source10: openfire.service  
Source11: openfire-tmpfiles.conf
Source12: openfire-systemd-start
%ifnarch noarch
Source1: %{JRE_BUNDLE}
%endif
%ifarch noarch
# Note that epoch is set here to 1, this appears to be consistent with non-Redhat
# jres as well due to an ancient problem with java-1.5.0-ibm jpackage RPM
Requires: java-headless >= 1:1.7.0
%endif
Requires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Group: Applications/Communications
Vendor: Igniterealtime Community
Packager: Igniterealtime Community
License: Apache license v2.0
AutoReqProv: no
URL: http://www.igniterealtime.org/

%define prefix /usr/share
%define homedir %{prefix}/openfire
# couldn't find another way to disable the brp-java-repack-jars which was called in __os_install_post
%define __os_install_post %{nil}
%define debug_package %{nil}

%description
Openfire is a leading Open Source, cross-platform IM server based on the
XMPP (Jabber) protocol. It has great performance, is easy to setup and use,
and delivers an innovative feature set.

%prep
%setup -q -n Openfire-4.0.3

%build
cd build
ant openfire
ant -Dplugin=search plugin
cd ..

%install
# Prep the install location.
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{prefix}
mkdir -p -m 755 $RPM_BUILD_ROOT/var/run/openfire
# Copy over the main install tree.
cp -R target/openfire $RPM_BUILD_ROOT%{homedir}
%ifnarch noarch
# Set up distributed JRE
pushd $RPM_BUILD_ROOT%{homedir}
gzip -cd %{SOURCE1} | tar xvf -
popd
%endif
# Set up the init script.
install -D -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}/openfire.service
install -D -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_tmpfilesdir}/openfire.conf
install -m 755 %{SOURCE12} $RPM_BUILD_ROOT%{homedir}/bin/systemd-start
# Make the startup script executable.
chmod 755 $RPM_BUILD_ROOT%{homedir}/bin/openfire.sh
# Set up the sysconfig file.
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
cp $RPM_BUILD_ROOT%{homedir}/bin/extra/redhat/openfire-sysconfig $RPM_BUILD_ROOT/etc/sysconfig/openfire
# Copy over the documentation
cp -R documentation/docs $RPM_BUILD_ROOT%{homedir}/documentation
cp documentation/dist/changelog.html $RPM_BUILD_ROOT%{homedir}/
cp documentation/dist/LICENSE.html $RPM_BUILD_ROOT%{homedir}/
cp documentation/dist/README.html $RPM_BUILD_ROOT%{homedir}/
# Copy over the i18n files
cp -R src/i18n $RPM_BUILD_ROOT%{homedir}/resources/i18n
# Make sure scripts are executable
# Note: these files are deleted below
# chmod 755 $RPM_BUILD_ROOT%{homedir}/bin/extra/openfired
# chmod 755 $RPM_BUILD_ROOT%{homedir}/bin/extra/redhat-postinstall.sh
# Move over the embedded db viewer pieces
mv $RPM_BUILD_ROOT%{homedir}/bin/extra/embedded-db.rc $RPM_BUILD_ROOT%{homedir}/bin
mv $RPM_BUILD_ROOT%{homedir}/bin/extra/embedded-db-viewer.sh $RPM_BUILD_ROOT%{homedir}/bin
# We don't really need any of these things.
rm -rf $RPM_BUILD_ROOT%{homedir}/bin/extra
rm -f $RPM_BUILD_ROOT%{homedir}/bin/*.bat
rm -rf $RPM_BUILD_ROOT%{homedir}/resources/nativeAuth/osx-ppc
rm -rf $RPM_BUILD_ROOT%{homedir}/resources/nativeAuth/win32-x86
rm -f $RPM_BUILD_ROOT%{homedir}/lib/*.dll

%clean
rm -rf $RPM_BUILD_ROOT

%preun
%systemd_preun openfire.service

# Force a happy exit even if openfire shutdown script didn't exit cleanly.
exit 0

%postun
%systemd_postun_with_restart openfire.service

# Force a happy exit even if openfire shutdown script didn't exit cleanly.
exit 0

%post
%systemd_post openfire.service

# Force a happy exit even if openfire condrestart script didn't exit cleanly.
exit 0

%files
%defattr(-,daemon,daemon)
%attr(750, daemon, daemon) %dir %{homedir}
%dir %{homedir}/bin
%{homedir}/bin/openfire.sh
%{homedir}/bin/openfirectl
%{homedir}/bin/systemd-start
%config(noreplace) %{homedir}/bin/embedded-db.rc
%{homedir}/bin/embedded-db-viewer.sh
%dir %{homedir}/conf
%config(noreplace) %{homedir}/conf/openfire.xml
%config(noreplace) %{homedir}/conf/security.xml
%config(noreplace) %{homedir}/conf/crowd.properties
%dir %{homedir}/lib
%{homedir}/lib/*.jar
%config(noreplace) %{homedir}/lib/log4j.xml
%dir %{homedir}/logs
%dir %{homedir}/plugins
%{homedir}/plugins/search.jar
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
%dir %{homedir}/resources/spank
%{homedir}/resources/spank/index.html
%dir %{homedir}/resources/spank/WEB-INF
%{homedir}/resources/spank/WEB-INF/web.xml
%config(noreplace) %{homedir}/resources/security/keystore
%config(noreplace) %{homedir}/resources/security/truststore
%config(noreplace) %{homedir}/resources/security/client.truststore
%doc %{homedir}/documentation
%doc %{homedir}/LICENSE.html 
%doc %{homedir}/README.html 
%doc %{homedir}/changelog.html
%config(noreplace) %{_sysconfdir}/sysconfig/openfire
%attr(0644,root,root) %{_unitdir}/openfire.service
%attr(0644,root,root) %{_tmpfilesdir}/openfire.conf
%ghost %dir /var/run/openfire
%ifnarch noarch
%{homedir}/jre
%endif

%changelog
* %{OPENFIRE_BUILDDATE} Igniterealtime Community <webmaster@igniterealtime.org> %{OPENFIRE_VERSION}-%{OPENFIRE_RELEASE}
- Automated RPM build with git rev-parse --short HEAD of %{OPENFIRE_REPOVERSION}
