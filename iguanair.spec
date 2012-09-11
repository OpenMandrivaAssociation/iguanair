
%define name	iguanair
%define Name	iguanaIR
%define version	1.0.3
%define rel	1

%define major	0
%define libname	%mklibname iguanair %major
%define devname	%mklibname iguanair -d

# python module
%define _disable_ld_no_undefined 1

Summary:	IguanaWorks USB IR Transceiver driver
Name:		%name
Version:	%version
Release:	%mkrel 1
License:	GPLv2 and LGPLv2.1
Group:		System/Kernel and hardware
URL:		http://iguanaworks.net/projects/IguanaIR/
# svn co http://iguanaworks.net/repos/iguanair/public/trunk/software/usb_ir iguanair
# REV=$(svn info iguanair | grep "Last Changed Rev" | cut -d" " -f4)
# svn export iguanair iguanair-$REV
# rm -rf iguanair-$REV/win32
# tar -cjf iguanair-$REV.tar.bz2 iguanair-$REV
Source0:	http://iguanaworks.net/downloads/%{Name}-%{version}.tar.bz2
Source1:	iguanair.mdv.init
Source2:	iguanair.sysconfig
Source3:	iguanair.logrotate
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	swig
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Patch0:		RPM_OS_iguana.patch

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
%py_requires -d

%description -n python-iguanair
Python bindings for IguanaWorks USB IR Transceiver.

%package reflasher
Summary:	Reflasher for iguanaIR devices
Group:		System/Kernel and hardware
Requires:	python-iguanair

%description reflasher
Firmware reflasher for IguanaWorks USB IR Transceiver.

%package -n %libname
Summary:	Shared library for iguanaIR devices
Group:		System/Libraries

%description -n %libname
This package contains the library needed to run programs dynamically
linked with libiguanair.

%package -n %devname
Summary:	Headers for iguanaIR development
Group:		Development/C
Requires:	%libname = %version
Provides:	iguanair-devel = %version-%release

%description -n %devname
This package contains the headers that programmers will need to develop
applications which will use libiguanair.

%prep
%setup -q -n %{Name}-%{version}
%patch0 -p1

%build
%configure2_5x
%make

# Fix incorrect permissions
chmod -x iguanaIR_wrap.c

%install
%makeinstall_std

rm -f %{buildroot}%{_sysconfdir}/init.d/iguanaIR
rm -f %{buildroot}%{_sysconfdir}/default/iguanaIR
rm -f %{buildroot}%{_sysconfdir}/udev/rules.d/iguanaIR.rules


#cat > %{buildroot}%{_sysconfdir}/udev/rules.d/iguanaIR.rules <<EOF
# do not edit this file, it will be overwritten on update
#ATTRS{manufacturer}=="IguanaWorks", \
#	GROUP = "iguanair", MODE = "0660", \
#	RUN+="/sbin/service iguanair rescan"
#EOF



install -D -m755 %SOURCE1 %{buildroot}%{_initrddir}/%name
install -D -m644 %SOURCE2 %{buildroot}%{_sysconfdir}/sysconfig/%name
install -D -m644 %SOURCE3 %{buildroot}%{_sysconfdir}/logrotate.d/%name

# not executables
chmod 0644 %{buildroot}%{_libexecdir}/iguanaIR-reflasher/hex/*.hex
chmod 0644 %{buildroot}%{_includedir}/*.h

%pre
%_pre_useradd iguanair / /sbin/nologin

%post
%_post_service %name
if [ "$1" = "1" ]; then
	 # apply new permissions from the added udev file
	/sbin/udevadm trigger --attr-match=manufacturer=IguanaWorks
fi

%preun
%_preun_service %name

%postun
%_postun_userdel iguanair

%files
%doc AUTHORS README.txt
#% {_sysconfdir}/udev/rules.d/%{Name}.rules
%{_initrddir}/%name
%config(noreplace) %{_sysconfdir}/sysconfig/%name
%config(noreplace) %{_sysconfdir}/logrotate.d/%name
/lib/udev/rules.d/80-iguanaIR.rules
%{_bindir}/igclient
%{_bindir}/igdaemon
%{_libdir}/iguanaIR/*.so

%files -n python-iguanair
%{python_sitelib}/*

%files reflasher
%{_bindir}/iguanaIR-reflasher
%{_libexecdir}/iguanaIR-reflasher

%files -n %libname
%{_libdir}/libiguanaIR.so.%{major}*

%files -n %devname
%doc README.txt
%{_libdir}/*.so
%{_includedir}/%{Name}.h
