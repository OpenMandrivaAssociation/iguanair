
%define name	iguanair
%define Name	iguanaIR
%define version	0.99
%define svnsnap	959
%define rel	1

%define major	0
%define libname	%mklibname iguanair %major
%define devname	%mklibname iguanair -d

# python module
%define _disable_ld_no_undefined 1

Summary:	IguanaWorks USB IR Transceiver driver
Name:		%name
Version:	%version
Release:	%mkrel 1.svn%svnsnap.%rel
License:	GPLv2 and LGPLv2.1
Group:		System/Kernel and hardware
URL:		http://iguanaworks.net/projects/IguanaIR/
# svn co http://iguanaworks.net/repos/iguanair/public/trunk/software/usb_ir iguanair
# REV=$(svn info iguanair | grep "Last Changed Rev" | cut -d" " -f4)
# svn export iguanair iguanair-$REV
# rm -rf iguanair-$REV/win32
# tar -cJf iguanair-$REV.tar.xz iguanair-$REV
Source:		iguanair-%svnsnap.tar.xz
Source1:	iguanair.mdv.init
Source2:	iguanair.sysconfig
Source3:	iguanair.logrotate
BuildRoot:	%{_tmppath}/%{name}-root
BuildRequires:	libusb-devel
BuildRequires:	libpopt-devel
BuildRequires:	swig
Requires(post):	rpm-helper
Requires(preun): rpm-helper

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
%setup -q -n iguanair-%svnsnap
# Project uses autoconf but not automake,
# and configure.ac overwrites CFLAGS.
# -fPIC should always be used for shared libs
sed -i 's|-O2|%{optflags} -fPIC|' autoconf/configure.ac
sed -i 's|-fpic||' Makefile.in

# noarch data wrongly in libdir:
sed -i 's|/lib/|/share/|' reflasher/Makefile

# arch-specific py libs wrongly in noarch dir:
sed -i 's|@PYTHON_SITE_PKG@|%python_sitearch|' Makefile.in

%build
./bootstrap.sh
%configure2_5x
# Parallel build broken as of 2009-07-04; tries to build python module
# before shared library.
# Also, Makefile is modified during build so we re-run make here
# so that files are not rebuilt in install phase.
make
make

%install
rm -rf %{buildroot}
%makeinstall_std
rm %{buildroot}%{_sysconfdir}/init.d/iguanaIR
rm %{buildroot}%{_sysconfdir}/default/iguanaIR
rm %{buildroot}%{_sysconfdir}/udev/rules.d/iguanaIR.rules
# same as upstream with udev 098 change and RUN adapted to our initscript
cat > %{buildroot}%{_sysconfdir}/udev/rules.d/iguanaIR.rules <<EOF
ATTRS{manufacturer}=="IguanaWorks", \
	OWNER="iguanair", GROUP="iguanair", MODE="0660", \
	RUN+="/sbin/service iguanair rescan"
EOF

install -D -m755 %SOURCE1 %{buildroot}%{_initrddir}/%name
install -D -m644 %SOURCE2 %{buildroot}%{_sysconfdir}/sysconfig/%name
install -D -m644 %SOURCE3 %{buildroot}%{_sysconfdir}/logrotate.d/%name

# not executables
chmod 0644 %{buildroot}%{_datadir}/iguanaIR-reflasher/hex/*.hex
chmod 0644 %{buildroot}%{_includedir}/*.h
chmod 0644 %{buildroot}%{python_sitearch}/*.py

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd iguanair / /bin/nologin

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
%defattr(-,root,root)
%doc AUTHORS README.txt
%{_sysconfdir}/udev/rules.d/%{Name}.rules
%{_initrddir}/%name
%config(noreplace) %{_sysconfdir}/sysconfig/%name
%config(noreplace) %{_sysconfdir}/logrotate.d/%name
%{_bindir}/igclient
%{_bindir}/igdaemon

%files -n python-iguanair
%defattr(-,root,root)
%{python_sitearch}/*%{Name}*

%files reflasher
%defattr(-,root,root)
%{_bindir}/iguanaIR-reflasher
%{_datadir}/iguanaIR-reflasher

%files -n %libname
%defattr(-,root,root)
%{_libdir}/libiguanaIR.so.%{major}*

%files -n %devname
%defattr(-,root,root)
%doc README.txt
%{_libdir}/*.so
%{_includedir}/%{Name}.h

