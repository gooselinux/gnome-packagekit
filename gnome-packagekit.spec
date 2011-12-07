%define packagekit_version		0.5.0
%define dbus_version			1.1.2
%define dbus_glib_version		0.73
%define glib2_version			2.18.0
%define gtk2_version			2.16.0
%define libnotify_version		0.4.3
%define unique_version			1.0.0
%define devicekit_power_version		007
%define libcanberra_version		0.10

%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary:   Session applications to manage packages
Name:      gnome-packagekit
Version:   2.28.3
Release:   3%{?dist}
License:   GPLv2+
Group:     Applications/System
URL:       http://www.packagekit.org
Source0:   http://download.gnome.org/sources/gnome-packagekit/2.28/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# RHEL specific
Patch0:    gnome-packagekit-2.28.3-change-default-to-category-groups.patch

# Update to Red Hat Supported Languages
Patch1:    gnome-packagekit-2.28.3-rhlinguas.patch

Requires:  glib2 >= %{glib2_version}
Requires:  gtk2 >= %{gtk2_version}
Requires:  gnome-icon-theme
Requires:  libnotify >= %{libnotify_version}
Requires:  unique >= %{unique_version}
Requires:  dbus-glib >= %{dbus_glib_version}
Requires:  dbus-x11 >= %{dbus_version}
Requires:  PackageKit >= %{packagekit_version}
Requires:  PackageKit-glib >= %{packagekit_version}
Requires:  PackageKit-gtk-module >= %{packagekit_version}
Requires:  PackageKit-device-rebind >= %{packagekit_version}
Requires:  shared-mime-info
Requires:  iso-codes
Requires:  libcanberra >= %{libcanberra_version}
Requires:  DeviceKit-power >= %{devicekit_power_version}
Requires(post):   scrollkeeper
Requires(pre):    GConf2
Requires(post):   GConf2
Requires(preun):  GConf2
Requires(postun): scrollkeeper
Obsoletes: pirut < 1.3.31-2
Provides:  pirut = 1.3.31-2

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: libwnck-devel
BuildRequires: dbus-devel >= %{dbus_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: libnotify-devel >= %{libnotify_version}
BuildRequires: gnome-panel-devel
BuildRequires: scrollkeeper
BuildRequires: gnome-doc-utils >= 0.3.2
BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: libtool
BuildRequires: cairo-devel
BuildRequires: startup-notification-devel
BuildRequires: perl(XML::Parser)
BuildRequires: gnome-doc-utils
BuildRequires: gnome-menus-devel >= 2.24.1
BuildRequires: PackageKit-glib-devel >= %{packagekit_version}
BuildRequires: unique-devel >= %{unique_version}
BuildRequires: intltool
BuildRequires: xorg-x11-proto-devel
BuildRequires: fontconfig-devel
BuildRequires: libcanberra-devel >= %{libcanberra_version}
BuildRequires: libgudev1-devel
BuildRequires: DeviceKit-power-devel >= %{devicekit_power_version}

%description
gnome-packagekit provides session applications for the PackageKit API.
There are several utilities designed for installing, updating and
removing packages on your system.

%package extra
Summary: Session applications to manage packages (extra bits)
Group: Applications/System
Requires: %{name} = %{version}-%{release}

%description extra
Extra GNOME applications for using PackageKit that are not normally needed.

%prep
%setup -q
%patch0 -p1 -b .change-default-to-category-groups
%patch1 -p2 -b .rhlinguas

%build
%configure --disable-scrollkeeper --disable-schemas-install
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

# nuke the ChangeLog file, it's huge
rm -f $RPM_BUILD_ROOT%{_datadir}/doc/gnome-packagekit-*/ChangeLog

desktop-file-install --delete-original                   \
  --dir=$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/                    \
  $RPM_BUILD_ROOT%{_datadir}/gnome/autostart/gpk-update-icon.desktop

for i in gpk-application gpk-update-viewer gpk-install-file gpk-log gpk-prefs gpk-repo ; do
  desktop-file-install --delete-original                                \
    --dir=$RPM_BUILD_ROOT%{_datadir}/applications/                      \
    $RPM_BUILD_ROOT%{_datadir}/applications/$i.desktop
done


# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi
      fi
    fi
  done
done

%find_lang %name --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
        %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas >/dev/null || :
scrollkeeper-update -q &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q %{_datadir}/icons/hicolor &> /dev/null || :
fi
update-desktop-database %{_datadir}/applications &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas &> /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas &> /dev/null || :
fi

%postun
scrollkeeper-update -q &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q %{_datadir}/icons/hicolor &> /dev/null || :
fi
update-desktop-database %{_datadir}/applications &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README
%{_bindir}/gpk-application
%{_bindir}/gpk-install-*
%{_bindir}/gpk-log
%{_bindir}/gpk-prefs
%{_bindir}/gpk-repo
%{_bindir}/gpk-update-icon
%{_bindir}/gpk-update-viewer
%dir %{_datadir}/gnome-packagekit
%{_datadir}/gnome-packagekit/gpk-application.ui
%{_datadir}/gnome-packagekit/gpk-client.ui
%{_datadir}/gnome-packagekit/gpk-eula.ui
%{_datadir}/gnome-packagekit/gpk-prefs.ui
%{_datadir}/gnome-packagekit/gpk-update-viewer.ui
%{_datadir}/gnome-packagekit/gpk-error.ui
%{_datadir}/gnome-packagekit/gpk-log.ui
%{_datadir}/gnome-packagekit/gpk-repo.ui
%{_datadir}/gnome-packagekit/gpk-signature.ui
%dir %{_datadir}/gnome-packagekit/icons
%dir %{_datadir}/gnome-packagekit/icons/hicolor
%dir %{_datadir}/gnome-packagekit/icons/hicolor/*
%dir %{_datadir}/gnome-packagekit/icons/hicolor/*/*
%{_datadir}/gnome-packagekit/icons/hicolor/*/*/*.png
%{_datadir}/gnome-packagekit/icons/hicolor/scalable/*/*.svg*
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/icons/hicolor/scalable/*/*.svg*
%config(noreplace) %{_sysconfdir}/gconf/schemas/*.schemas
%{_datadir}/man/man1/*.1.gz
%{_datadir}/gnome/help/gnome-packagekit
%{python_sitelib}/packagekit/*py*
%{_datadir}/omf/gnome-packagekit
%{_sysconfdir}/xdg/autostart/gpk-update-icon.desktop
%{_datadir}/applications/gpk-application.desktop
%{_datadir}/applications/gpk-install-file.desktop
%{_datadir}/applications/gpk-prefs.desktop
%{_datadir}/applications/gpk-install-catalog.desktop
%{_datadir}/applications/gpk-update-viewer.desktop

%files extra
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README
%{_bindir}/gpk-backend-status
%{_bindir}/gpk-service-pack
%{_datadir}/gnome-packagekit/gpk-service-pack.ui
%{_datadir}/gnome-packagekit/gpk-backend-status.ui
%{_datadir}/applications/gpk-service-pack.desktop
%{_datadir}/applications/gpk-repo.desktop
%{_datadir}/applications/gpk-log.desktop

%changelog
* Tue Aug 10 2010 Richard Hughes <rhughes@redhat.com> - 2.28.3-3
- Translation patch for Red Hat supported languages.
- Resolves: #574661

* Wed Jun 09 2010 Richard Hughes  <rhughes@redhat.com> - 2.28.3-2
- Backport a patch from upstream that adds support for support media repos
  such as those found on additional CDs or DVDs.
- This patch just calls GetUpdates after a detected media repo is inserted,
  which is enough for PackageKit to add the repo to the default set, and for
  the repo to be used in all the GNOME and KDE tools.
- This patch will not add explicit support for media repos in client programs,
  so the media is not requested if it is not inserted when the package tools
  are open. This functionality can be backported at a later time if required.
- Resolves: #591534

* Tue Jun 08 2010 Richard Hughes  <rhughes@redhat.com> - 2.28.3-1
- Update to 2.28.3
- When we ask to logout, actually logout, rather than shutdown
- Don't hide the restart status icon just because the daemon exited
- Don't check for updates every day when the user had specified 'Never'
- Allow the user to select the GPG key information to be able to verify it
- Fix the error when the user clicks the about menu item
- Fix a crash where the desktop file that was installed has no root directory
- Fix a crash when the process-working icon has zero height
- Resolves: #585086

* Thu May 27 2010 Richard Hughes  <rhughes@redhat.com> - 2.28.3-0.5.20091211git
- Translation patch for gnome-packagekit for Red Hat Supported Languages.
- Resolves: #575716

* Fri Jan 08 2010 Richard Hughes  <rhughes@redhat.com> - 2.28.3-0.4.20091211git
- Don't rely on an obsolete package name (in another place).
- Resolves: #553687

* Fri Jan 08 2010 Richard Hughes  <rhughes@redhat.com> - 2.28.3-0.3.20091211git
- Don't rely on an obsolete package name.
- Resolves: #553687

* Fri Jan 08 2010 Richard Hughes  <rhughes@redhat.com> - 2.28.3-0.2.20091211git
- Change the default in add/remove programs to show the category group menu.
- Resolves: #553687

* Mon Dec 11 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.3-0.1.20091211git
- New snapshot from the gnome-2-28 branch
- Don't show the selected packages as deps of the to be updated packages.
  Note, this only affects PackageKit >= 0.5.5. Fixes rh#546247
- Check the GpkDbusTask object only replies once to each session request

* Mon Dec 07 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.2-1
- Update to 2.28.2
- Remove the original package from the dep-confirmation screen
- Ignore generic errors such as 'Failed' and do not show UI in this case
- Use the desktop icon when we unselect the installed application in gpk-application. Fixes fd#25098

* Mon Nov 16 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.2-0.2.20091116git
- New snapshot from the gnome-2-28 branch
- Use the desktop icon when we unselect the installed application in gpk-application.
- Added and Updated translations.
- Fix crash when removing certain packages with gpk-application.
- Only wait 3 seconds (not 60) when we get the updates changed signal

* Fri Oct 30 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.2-0.1.20091030git
- New snapshot from the gnome-2-28 branch
- Have a better stab at #530264

* Thu Oct 29 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.2-0.1.20091029git
- New snapshot from the gnome-2-28 branch
- Many updated translations.
- Fixes #529960 and #530595

* Mon Oct 19 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.1-1
- Update to 2.28.1
- Translation updates
- Simulate removal correctly to fix removing packages
- Ignore cleanup and finished packages when we a simulating remove or install
- If command line contains (deleted) the original binary is invalid. Fixes #524873
- Never show the role text in the GpkWatch tooltip
- Run the helpers with interaction 'hide-finished,hide-warnings' as we are handling failure

* Mon Sep 28 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.0-0.1.20090928git
- New snapshot from the gnome-2-28 branch
- Many updated translations.
- Fixes #525810 and #524873

* Mon Sep 21 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.0-1
- New upstream version.

* Mon Sep 07 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.92-1
- New upstream version.
- Many updated translations.
- Add simulation of installed files.
- Don't show duplicate package names in the reboot tooltip.

* Mon Aug 24 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.91-2
- Actually upload the correct tarball.

* Mon Aug 24 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.91-1
- New upstream version

* Tue Aug 11 2009 Ville Skyttä <ville.skytta@iki.fi> - 2.27.5-3
- Use bzipped upstream tarball.

* Mon Aug 03 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.5-2
- Move the gpk-log and gpk-repo menu shortcuts to the gnome-packagekit-extra
  subpackage to reduce menu polution on the live cd.

* Mon Aug 03 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.5-1
- New upstream version
- Port all the code to using PolicyKit1 rather than PolicyKit
- Reduce the size displayed as the package is downloaded
- Scroll to the package being processed in the update list
- Fixes #510730, #510984, #510730, #497737 and #514879

* Mon Jul 27 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.4-0.1.20090727git
- Update to latest git master snapshot

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 06 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.3-1
- New upstream version
 - Lots of updated translations
 - Check for dependancies before downloading updates in the update viewer
 - Connect to gnome-session to get the idle status, not gnome-screensaver
 - Don't show a generic icon when we have messages
 - Use the newest filter by default in the update viewer
 - Run all the packages after install, not just the selected package
- Fixes #506010, #507062, #508505, #509067, #509104 and #509636

* Thu Jun 25 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.3-0.4.20090625git
- Don't build with GDK_MULTIHEAD_SAFE as it breaks ca_gtk_context_get with a
  new libcanberra-gtk. Ifdefs probably required as ca_gtk_context_get_for_screen
  is fairly new.

* Thu Jun 25 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.3-0.3.20090625git
- Update to latest git master snapshot

* Tue Jun 16 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.3-0.2.20090616git
- Apply a patch to convert to the PolKit1 API.
- Do autoreconf as the polkit patch is pretty invasive

* Tue Jun 16 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.3-0.1.20090616git
- Update to todays git snapshot
- Connect to gnome-session to get the idle status, not gnome-screensaver
- Lots of translation updates

* Tue Jun 02 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.2-2
- Rebuild as waitrepo timed out on me during a chainbuild. Oddball.

* Mon Jun 01 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.2-1
- New upstream version
- Lots of translation updates
- Add UI helpers for media changing
- Lots of fixes to the update viewer and update icon
- Fixes #493934, #492160, #496024, #496870, #497162, #500237, #502562,
  #502589 and #492005

* Tue Apr 14 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.2-0.2.20090414git
- Reroll the tarball without the new PkMediaTypeEnum functionality which
  is present in git master PackageKit.

* Tue Apr 14 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.2-0.1.20090414git
- New git snapshot fixing several bugs

* Mon Mar 30 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.1-1
- New upstream version

* Tue Mar 24 2009 Richard Hughes  <rhughes@redhat.com> - 2.27.1-0.1.20090324git
- New snapshot fixing several bugs with the new update viewer.

* Thu Mar 19 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.6-0.2.20090319git
- Don't break the package download size label.

* Thu Mar 19 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.6-0.1.20090319git
- Update to todays git snapshot so we can test the latest version of the
  update viewer.
- Remove the fedora system-install-packages compatibility script as we've had
  it for over two releases.

* Tue Mar 17 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.6-0.1.20090317git
- Update to a git snapshot so we can test the latest version of the
  update viewer.

* Wed Mar 11 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.5-3
- Put gpk-update-viewer2 into the main package, not extras
- Fixes #489677

* Mon Mar 09 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.5-2
- Require PackageKit 0.4.5 otherwise the new update viewer breaks

* Mon Mar 09 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.5-1
- New upstream version
- Merge in a new update viewer with a very different UI which I've patched
  Fedora to use by default as requested by Matthias.
- Lots of translation updates

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 23 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.4-2
- Bump for rebuild.

* Mon Feb 23 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.4-1
- New upstream version
- Lots of bug fixes

* Mon Jan 19 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.2-1
- New upstream version
- Lots of bug fixes

* Thu Jan 08 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.1-1
- New upstream version
- Add an option to the prefs dialog to prevent checking for updates when
  using mobile broadband connections
- Allow the admin to restrict getting updates when on WiFi connections
- Set the default search mode to details (not name) and preserve the search
  type in GConf if changed in the UI
- Add a simple markdown parser and use it in all applications.
- Send different errors when we fail a method on the session DBus interface
- Support setting timeouts via the interaction mode from the DBus interface
- Lots of bugfixes

* Fri Dec 12 2008 Richard Hughes  <rhughes@redhat.com> - 0.4.0-2
- Depend on PackageKit-gtk-module so the auto-font installation can be
  turned on in F11.
- Turn off the loading of libpk-gtk-module.so until we have a new
  fontconfig using a spec file patch that we can nuke soon.
- Fixes rh#476066

* Tue Dec 09 2008 Richard Hughes  <rhughes@redhat.com> - 0.4.0-1
- New upstream version

* Thu Dec  4 2008 Matthias Clasen <mclasen@redhat.com> 0.3.11-3
- Rebuild for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.3.11-2
- Rebuild for Python 2.6

* Mon Nov 24 2008 Richard Hughes <rhughes@redhat.com> - 0.3.11-1
- New upstream version

* Tue Nov 11 2008 Richard Hughes <rhughes@redhat.com> - 0.3.10-1
- New upstream version
- Drop all upstreamed patches

* Fri Nov 07 2008 Warren Togami <wtogami@redhat.com> - 0.3.9-7
- Bug #470617 Just exit instead of complaining about a non-local session

* Wed Nov 05 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-6
- Fix up the fedora system-install-packages compatibility script.
- Fixes #468568

* Sat Nov 01 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-5
- Fix up the pirut obsoletes to fix upgrades from F8. Fixes #469481

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-4
- Barr. Actually apply the patch. Sleep time.

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-3
- Fix the size request of gpk-application to fix rh#467987

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-2
- Split out the service pack creator and the backend status programs
  into a gnome-packagekit-extra package as it's not suitable for the
  default desktop.

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-1
- New upstream version
- Many new and updated translations.
- Lots of bugfixes (#467746, #467582)

* Fri Oct 24 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.8-2
- Fix the untitled window in gpk-update-viewer. Fixes #468200
- Fix the resize problem on small form factor devices. Fixes #467987

* Mon Oct 20 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.8-1
- New upstream version

* Mon Oct 13 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.7-1
- New upstream version
- Much better log viewer functionality
- New service pack creator tool

* Fri Oct 10 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-5
- Bump

* Fri Oct 10 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-4
- Add a bugfix from upstream so we don't try to check for updates
  when we've set to never. Fixes RH#461825.

* Wed Oct  8 2008 Matthias Clasen  <mclasen@redhat.com> - 0.3.6-3
- Another space-saving hack

* Mon Oct 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-2
- Upload new sources. Ooops.

* Mon Oct 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-1
- New upstream version
- Show vendor specific messages when we fail to find packages
- Turn off hardware HAL integration

* Mon Sep 22 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.5-1
- New upstream version

* Mon Sep 22 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.4-1
- New upstream version

* Wed Sep 17 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.3-2
- Fix the interaction when the update check and the upgrade check are
  scheduled at the same time.

* Tue Sep 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.3-1
- Update to newest upstream version.
- Supports collection install and remove in the UI
- Add InstallGStreamerCodecs to the session interface

* Mon Sep 08 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.2-1
- Update to newest upstream version.

* Thu Aug 28 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.1-3
- Bump because the PackageKit-devel rpm was empty.

* Thu Aug 28 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.1-2
- Bump as make chainbuild is broken, so we'll have to do this in two steps.

* Mon Aug 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.1-1
- Update to newest upstream version.

* Mon Aug 22 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.0-1
- Update to newest upstream version.

* Mon Aug 04 2008 Robin Norwood <rnorwood@redhat.com> - 0.2.4-3
- Fix Source0 URL.

* Tue Jul 31 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.4-2
- Rebuild for libunique ABI break.

* Tue Jul 30 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.4-1
- New upstream version, only bugfixes.

* Wed Jun 18 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-4.20080618
- Pull in a new snapshot from the unstable branch.
- Fixes a problem when installing with the DBUS session interface

* Mon Jun 11 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-3.20080611
- Pull in a new snapshot from the unstable branch.
- New interface for gpk-application - one that doesn't suck
- UI fixes for gpk-repo and gpk-update-viewer

* Mon Jun 09 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-2.20080609
- Add intltool to the BR.

* Mon Jun 09 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-1.20080609
- Pull in a new snapshot from the unstable branch.

* Thu May 29 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.2-2.20080529
- Pull in a new snapshot from the unstable branch.

* Mon May 19 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.2-1.20080519
- Pull in a new snapshot from the unstable branch.

* Fri May 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.1-3.20080508
- Add a BR on unique to make the client tools single instance

* Thu May 08 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.1-2.20080508
- Pull in a new snapshot from the unstable branch.

* Tue May 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.1-1.20080506
- Pull in a new snapshot from the unstable branch.

* Tue May 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.0-1
- Update to the latest _UNSTABLE_ upstream source

* Sat Apr 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-5.20080416git
- Build against the right version of PackageKit to make koji DTRT.

* Sat Apr 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-4.20080416git
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes rh#442398.

* Sat Apr 15 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-3.20080415git
- Add a man page for system-install-packages. Fixes rh#441673

* Sat Apr 15 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-2.20080415git
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes include rh#442150, rh#442543, rh#442230, rh#441062 and more from upstream.

* Sat Apr 12 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-1.20080412git
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes that were cherry picked into this branch since 0.1.11 was released can be viewed at:
  http://gitweb.freedesktop.org/?p=users/hughsient/gnome-packagekit.git;a=log;h=GNOME_PACKAGEKIT_0_1_X

* Fri Apr 11 2008 Jesse Keating <jkeating@redhat.com> - 0.1.11-5
- Obsolete / Provide pirut.

* Thu Apr 10 2008 Owen Taylor <otaylor@redhat.com> - 0.1.11-4
- Make system-install-packages a wrapper script not a symlink
  so both files and package names work (#441674)

* Sat Apr  9 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.11-3
- Pull in the new icons from upsteam from Mike Langlie.

* Sat Apr  9 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.11-2
- Fix a plethora of GUI bugs by pulling some fixes from upstream

* Sat Apr  5 2008 Matthias Clasen  <mclasen@redhat.com> - 0.1.11-1
- Update to 0.1.11

* Fri Mar 28 2008 Bill Nottingham <notting@redhat.com> - 0.1.10-1
- update to 0.1.10
- add PK-gnome-devel build requirement

* Tue Mar 18 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-4
- move pk-update-icon.desktop to /etc/xdg/autostart/

* Thu Mar 13 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-3
- symlink pk-install-file to system-install-packages

* Tue Mar 11 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-2
- Apply patch to enable gnome-packagekit in KDE

* Wed Mar  5 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-1
- Update to latest upstream version: 0.1.8

* Thu Feb 21 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.8-1
- Update to latest upstream version: 0.1.8

* Fri Feb 15 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.7-1
- Update to latest upstream version: 0.1.7

* Sat Jan 19 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.6-1
- Update to latest upstream version: 0.1.6

* Sun Dec 30 2007 Christopher Aillon <caillon@redhat.com> - 0.1.5-2
- Fix the build

* Fri Dec 21 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.5-1
- Update to latest upstream version: 0.1.5
 
* Tue Nov 27 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.4-1
- Update to latest upstream version: 0.1.4

* Mon Nov 12 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.3-1
- Update to latest upstream version: 0.1.3

* Sun Nov 11 2007 Ray Strode <rstrode@redhat.com> - 0.1.2-2
- remove --vendor "gnome" from desktop-file-install calls. It's
  deprecated and changes the latest of .desktop files.

* Thu Nov 01 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.2-1
- Update to latest upstream version: 0.1.2

* Tue Oct 23 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.1-1
- Update to latest upstream version

* Tue Oct 16 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.0-2
- Apply recommended fixes from package review
 
* Mon Oct 15 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.0-1
- Initial build (based upon spec file from Richard Hughes)
