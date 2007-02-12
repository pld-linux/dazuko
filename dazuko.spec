#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%if !%{with kernel}
%undefine	with_dist_kernel
%endif
#
%define		_rel	1
Summary:	Linux Dazuko driver
Summary(pl.UTF-8):   Sterownik Dazuko dla Linuksa
Name:		dazuko
Version:	2.3.2
Release:	%{_rel}
Epoch:		0
License:	BSD (library), GPL (Linux kernel module)
Group:		Base/Kernel
Source0:	http://www.dazuko.org/files/%{name}-%{version}.tar.gz
# Source0-md5:	bb32e24ad60a31dbfc419d3341287f68
Patch0:		%{name}-kbuild.patch
Patch1:		%{name}-caps.patch
URL:		http://www.dazuko.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.286
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

To install the dazuko kernel module install kernel-misc-dazuko or
kernel-smp-misc-dazuko.

%description -l pl.UTF-8
Dazuko ma być wieloplatformowym sterownikiem urządzenia pozwalającym
aplikacjom sterować dostępem do plików w systemie. Poprzez
zainstalowanie sterownika system będzie mógł wspierać aplikacje
sterujące dostępem do plików w oparciu o Dazuko. Kiedy ten projekt
stanie się popularny, autorzy mają nadzieję, że sterownik ten będzie
popularnym elementem większości systemów.

Aby zainstalować moduł jądra należy zainstalować pakiet
kernel-misc-dazuko lub kernel-smp-misc-dazuko.

# kernel subpackages.
%package -n kernel%{_alt_kernel}-misc-%{name}
Summary:	Linux driver for dazuko
Summary(pl.UTF-8):   Linuksowy sterownik dazuko
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-misc-%{name}
This is driver for dazuko for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-misc-%{name} -l pl.UTF-8
Ten pakiet zawiera sterownik dazuko dla Linuksa.

%package -n kernel%{_alt_kernel}-smp-misc-%{name}
Summary:	Linux SMP driver for dazuko
Summary(pl.UTF-8):   Sterownik dazuko dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-misc-%{name}
This is driver for dazuko for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-misc-%{name} -l pl.UTF-8
Ten pakiet zawiera sterownik dazuko dla Linuksa SMP.

%package examples
Summary:	Example code for Dazuko
Summary(pl.UTF-8):   Przykładowy kod dla Dazuko
License:	BSD
Group:		Development/Libraries

%description examples
Example code for Dazuko.

%description examples -l pl.UTF-8
Przykładowy kod dla Dazuko.

%package devel
Summary:	Headers for Dazuko
Summary(pl.UTF-8):   Pliki nagłówkowe Dazuko
License:	BSD
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Headers for Dazuko.

%description devel -l pl.UTF-8
Pliki nagłówkowe Dazuko.

%package static
Summary:	Static libraries for Dazuko
Summary(pl.UTF-8):   Statyczne biblioteki Dazuko
License:	BSD
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libraries for Dazuko.

%description static -l pl.UTF-8
Statyczne biblioteki Dazuko.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%if %{with kernel}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
#
#	patching/creating makefile(s) (optional)

	# NOTE: It's not autoconf configure.
	./configure \
		--kernelsrcdir=%{_kernelsrcdir} \
		%{?debug:--enable-debug} \
		--disable-compat1 \
		--without-library

	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv dazuko{,-$cfg}.ko
done
%endif

%if %{with userspace}
# NOTE: It's not autoconf configure.
./configure \
	%{?debug:--enable-debug} \
	--disable-compat1 \
	--without-module

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
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install dazuko-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/dazuko.ko
%if %{with smp} && %{with dist_kernel}
install dazuko-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/dazuko.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel%{_alt_kernel}-misc-dazuko
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-misc-dazuko
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-misc-dazuko
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-misc-dazuko
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-dazuko
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-misc-dazuko
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
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
