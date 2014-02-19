# python module
%define _disable_ld_no_undefined 1
%define debug_package %{nil}

%define Name	iguanaIR
%define major	0
%define libname	%mklibname iguanair %{major}
%define devname	%mklibname iguanair -d

Summary:	IguanaWorks USB IR Transceiver driver
Name:		iguanair
Version:	1.0.5
Release:	2
License:	GPLv2 and LGPLv2.1
Group:		System/Kernel and hardware
Url:		http://iguanaworks.net/projects/IguanaIR/
# svn co http://iguanaworks.net/repos/iguanair/public/trunk/software/usb_ir iguanair
# REV=$(svn info iguanair | grep "Last Changed Rev" | cut -d" " -f4)
# svn export iguanair iguanair-$REV
# rm -rf iguanair-$REV/win32
# tar -cjf iguanair-$REV.tar.bz2 iguanair-$REV
Source0:	http://iguanaworks.net/downloads/%{Name}-%{version}.tar.bz2
Source1:        iguanaIR.service
Source2:        iguanaIR-rescan
Source3:	README.omv
# https://iguanaworks.net/projects/IguanaIR/ticket/205 for patch 5, 3, 2.
Patch3:         0003-Use-platform-specific-python-extension-dir.patch
# Fedora only
Patch6:         0006-udev-invoke-systemd-support-not-sysV-init-file.patch

BuildRequires:	swig
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(popt)
Requires(post,preun):	rpm-helper

%description
This package contains the driver daemon required for the operation
of the IguanaWorks USB IR Transceiver and the igclient test tool.

The IguanaWorks USB IR Transceiver is a simple USB device that can
communicate with most home electronics and remote controls via
infrared (IR). The transceiver can both send and receive IR codes,
and is fully compatible with LIRC under Linux. Unlike serial
devices, the USB transceiver does not require a kernel module, and
multiple transceivers can be in use at the same time. Each
transceiver can transmit on up to 4 independent channels.

%package -n python-iguanair
Summary:	Python bindings for iguanaIR
Group:		Development/Python
BuildRequires:	python-devel

%description -n python-iguanair
Python bindings for IguanaWorks USB IR Transceiver.

%package reflasher
Summary:	Reflasher for iguanaIR devices
Group:		System/Kernel and hardware
Requires:	python-iguanair

%description reflasher
Firmware reflasher for IguanaWorks USB IR Transceiver.

%package -n %{libname}
Summary:	Shared library for iguanaIR devices
Group:		System/Libraries

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with libiguanair.

%package -n %{devname}
Summary:	Headers for iguanaIR development
Group:		Development/C
Requires:	%{libname} = %version
Provides:	%{name}-devel = %version-%release

%description -n %{devname}
This package contains the headers that programmers will need to develop
applications which will use libiguanair.

%prep
%setup -qn %{Name}-%{version}
%apply_patches
cp %{SOURCE3} README.omv

%build
%configure2_5x
%make

# Fix incorrect permissions
chmod -x iguanaIR_wrap.c

%install
%makeinstall_std

install -m755 -d %{buildroot}%{_localstatedir}/run/%{name}

# Use /etc/sysconfig instead of /etc/default
mkdir %{buildroot}%{_sysconfdir}/sysconfig || :
mv  %{buildroot}/etc/default/iguanaIR \
    %{buildroot}%{_sysconfdir}/sysconfig

# Fix up some stray file permissions issues
chmod -x %{buildroot}%{python_sitearch}/*.py \
         %{buildroot}%{_includedir}/%{Name}.h \
         %{buildroot}%{_datadir}/%{Name}-reflasher/hex/*

# Remove the installed initfile and install the systemd support instead.
rm -rf %{buildroot}%{_sysconfdir}/init.d/
install -m644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{Name}.service
install -m755 -D %{SOURCE2} %{buildroot}%{_libexecdir}/iguanaIR/rescan

# Install private log dir, tmpfiles.d setup.
install -m755 -d %{buildroot}%{_localstatedir}/log/iguanaIR
install -m755 -d %{buildroot}/etc/tmpfiles.d

cat > %{buildroot}/etc/tmpfiles.d/%{name}.conf <<EOF
d   /run/%{name}    0755    iguanair   iguanair
EOF
install -m755 -d %{buildroot}/run/%{name}

%pre
%_pre_useradd iguanair / /sbin/nologin

%post
%_post_service %{name}
if [ "$1" = "1" ]; then
	 # apply new permissions from the added udev file
	/sbin/udevadm trigger --attr-match=manufacturer=IguanaWorks
fi

%preun
%_preun_service %{name}

%postun
%_postun_userdel iguanair

%files
%doc AUTHORS LICENSE LICENSE-LGPL WHY protocols.txt
%doc README.txt notes.txt ChangeLog
%doc README.omv
%{_bindir}/igdaemon
%{_bindir}/igclient
%{_libexecdir}/%{Name}/
%{_unitdir}/%{Name}.service
/lib/udev/rules.d/80-%{Name}.rules
%config(noreplace) %{_sysconfdir}/sysconfig/%{Name}
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%attr(755, iguanair, iguanair) /run/%{name}
%attr(775, iguanair, iguanair) %{_localstatedir}/log/%{Name}

%files -n python-iguanair
%{python_sitearch}/*

%files reflasher
%{_datadir}/%{Name}-reflasher/
%{_bindir}/%{Name}-reflasher

%files -n %{libname}
%{_libdir}/iguanaIR.so.%{major}*

%files -n %{devname}
%doc README.txt
%{_libdir}/*.so
%{_includedir}/%{Name}.h
