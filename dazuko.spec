#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%if !%{with kernel}
%undefine	with_dist_kernel
%endif
#
%define		_rel	0.7
Summary:	Linux Dazuko driver
Summary(pl.UTF-8):	Sterownik Dazuko dla Linuksa
Name:		dazuko
Version:	2.3.4
Release:	%{_rel}
Epoch:		0
License:	BSD (library), GPL (Linux kernel module)
Group:		Base/Kernel
Source0:	http://www.dazuko.org/files/%{name}-%{version}.tar.gz
# Source0-md5:	14ae194714584944b983845793daf2a4
Patch0:		%{name}-caps.patch
URL:		http://www.dazuko.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Dazuko aims to be a cross-platform device driver that allows
applications to control file access on a system. By installing the
driver, your system will be able to support file access control
applications that are based on Dazuko. As this project becomes more
popular and more applications choose Dazuko for their file access
needs, it is hoped that this driver will become a common component of
most systems.

To install the dazuko kernel module install kernel-misc-dazuko.

%description -l pl.UTF-8
Dazuko ma być wieloplatformowym sterownikiem urządzenia pozwalającym
aplikacjom sterować dostępem do plików w systemie. Poprzez
zainstalowanie sterownika system będzie mógł wspierać aplikacje
sterujące dostępem do plików w oparciu o Dazuko. Kiedy ten projekt
stanie się popularny, autorzy mają nadzieję, że sterownik ten będzie
popularnym elementem większości systemów.

Aby zainstalować moduł jądra należy zainstalować pakiet
kernel-misc-dazuko.

%package -n kernel%{_alt_kernel}-misc-%{name}
Summary:	Linux driver for dazuko
Summary(pl.UTF-8):	Linuksowy sterownik dazuko
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-misc-%{name}
This is driver for dazuko for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-misc-%{name} -l pl.UTF-8
Ten pakiet zawiera sterownik dazuko dla Linuksa.

%package examples
Summary:	Example code for Dazuko
Summary(pl.UTF-8):	Przykładowy kod dla Dazuko
License:	BSD
Group:		Development/Libraries

%description examples
Example code for Dazuko.

%description examples -l pl.UTF-8
Przykładowy kod dla Dazuko.

%package devel
Summary:	Headers for Dazuko
Summary(pl.UTF-8):	Pliki nagłówkowe Dazuko
License:	BSD
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Headers for Dazuko.

%description devel -l pl.UTF-8
Pliki nagłówkowe Dazuko.

%package static
Summary:	Static libraries for Dazuko
Summary(pl.UTF-8):	Statyczne biblioteki Dazuko
License:	BSD
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libraries for Dazuko.

%description static -l pl.UTF-8
Statyczne biblioteki Dazuko.

%prep
%setup -q
%patch -P0 -p1

cat > Makefile << EOF
obj-m += dazuko.o

dazuko-objs := dazuko_core.o dazuko_transport.o dazuko_linux26_lsm.o dazuko_linux26.o

CFLAGS += -DLINUX26_SUPPORT -DTRUSTED_APPLICATION_SUPPORT
CFLAGS += -DUSE_CLASS -DUSE_TRYTOFREEZEVOID -DLINUX_USE_FREEZER_H
CFLAGS += -DTASKSTRUCT_USES_PARENT -DUSE_CONFIG_H -DON_OPEN_SUPPORT -DON_EXEC_SUPPORT
EOF

%build
./linux_dev_conf %{_kernelsrcdir}/include/linux/device.h
./linux_lsm_conf %{_kernelsrcdir}/include/linux/security.h
%if %{with kernel}
%build_kernel_modules -m dazuko
%endif

%if %{with userspace}
# NOTE: It's not autoconf configure.
./configure \
	%{?debug:--enable-debug} \
	--disable-compat1 \
	--without-module \
	--disable-rsbac

cd library
%{__make} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -fPIC"
%{__cc} -shared -Wl,-soname,libdazuko.so.0 -o libdazuko.so.0.0.0 *.o
ln -s libdazuko.so.0.0.0 libdazuko.so.0
ln -s libdazuko.so.0.0.0 libdazuko.so
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_examplesdir}/%{name}-%{version},%{_libdir},%{_includedir}}

cp -a example* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

cp -af library/libdazuko.* $RPM_BUILD_ROOT%{_libdir}
install dazukoio.h $RPM_BUILD_ROOT%{_includedir}
%endif

%if %{with kernel}
%install_kernel_modules -m dazuko -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel%{_alt_kernel}-misc-dazuko
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-misc-dazuko
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-dazuko
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdazuko.so.*.*.*

%files examples
%defattr(644,root,root,755)
%doc README
%{_examplesdir}/%{name}-%{version}

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdazuko.so
%{_includedir}/dazukoio.h

%files static
%defattr(644,root,root,755)
%{_libdir}/lib*.a
%endif
