# TODO: fix Name vs filename
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
# main package.
#
Summary:	Linux Dazuko driver
Summary(pl):	Sterownik Dazuko dla Linuksa
Name:		dazuko
Version:	2.0.6
%define		_rel	1
Release:	%{_rel}
Epoch:		0
License:	BSD/GPL
Group:		Base/Kernel
Source0:	http://www.dazuko.org/files/dazuko-%{version}.tar.gz
# Source0-md5:	844498651d22ddd76bea4104bf7c3e43
URL:		http://www.dazuko.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
BuildRequires:	bash
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Dazuko aims to be a cross-platform device driver that allows
applications to control file access on a system. By installing the
driver, your system will be able to support file access control
applications that are based on Dazuko. As this project becomes more
popular and more applications choose Dazuko for their file access
needs, it is hoped that this driver will become a common component
of most systems. 

To install the dazuko kernel module install kernel-misc-dazuko or
kernel-smp-misc-dazuko.

%description -l pl
Dazuko ma byæ wieloplatformowym sterownikiem urz±dzenia pozwalaj±cym
aplikacjom sterowaæ dostêpem do plików w systemie. Poprzez
zainstalowanie sterownika system bêdzie móg³ wspieraæ aplikacje
steruj±ce dostêpem do plików w oparciu o Dazuko. Kiedy ten projekt
stanie siê popularny, autorzy maj± nadziejê, ¿e sterownik ten bêdzie
popularnym elementem wiêkszo¶ci systemów.

Aby zainstalowaæ modu³ j±dra nale¿y zainstalowaæ pakiet
kernel-misc-dazuko lub kernel-smp-misc-dazuko.

# kernel subpackages.
%package -n kernel-misc-%{name}
Summary:	Linux driver for dazuko
Summary(pl):	Linuksowy sterownik dazuko
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-misc-%{name}
This is driver for dazuko for Linux.

This package contains Linux module.

%description -n kernel-misc-%{name} -l pl
Ten pakiet zawiera sterownik dazuko dla Linuksa.

%package -n kernel-smp-misc-%{name}
Summary:	Linux SMP driver for dazuko
Summary(pl):	Sterownik dazuko dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-misc-%{name}
This is driver for dazuko for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-misc-%{name} -l pl
Ten pakiet zawiera sterownik dazuko dla Linuksa SMP.

%package examples
Summary:	Example code for Dazuko
Summary(pl):	Przyk³adowy kod dla Dazuko
Group:		Development/Libraries

%description examples
Example code for Dazuko.

%description examples -l pl
Przyk³adowy kod dla Dazuko.

%package devel
Summary:	Headers for Dazuko
Summary(pl):	Pliki nag³ówkowe Dazuko
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Headers for Dazuko.

%description devel -l pl
Pliki nag³ówkowe Dazuko.

%package static
Summary:	Static libraries for Dazuko
Summary(pl):	Statyczne biblioteki Dazuko
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libraries for Dazuko.

%description static -l pl
Statyczne biblioteki Dazuko.

%prep
%setup -q

%build

%if %{with kernel}
# NOTE: It's not autoconf configure.
bash ./configure \
	--kernelsrcdir=%{_kernelsrcdir}

# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	touch include/config/MARKER
#
#	patching/creating makefile(s) (optional)
#
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}

	mv dazuko{,-$cfg}.ko
done
%endif

%if %{with userspace}
cd library
%{__make} \
	CFLAGS="-fPIC"
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

cp -af library/libdazuko.* $RPM_BUILD_ROOT/%{_libdir}
install dazukoio.h $RPM_BUILD_ROOT/%{_includedir}
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

%post	-n kernel-misc-dazuko
%depmod %{_kernel_ver}

%postun	-n kernel-misc-dazuko
%depmod %{_kernel_ver}

%post	-n kernel-smp-misc-dazuko
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-misc-dazuko
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files -n kernel-misc-dazuko
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-dazuko
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
