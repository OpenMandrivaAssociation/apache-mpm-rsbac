%define version 2.2.17
%define release %mkrel 3
 
%define defaultmaxmodules 128
%define defaultserverlimit 1024

%define build_test 0

# commandline overrides:
# rpm -ba|--rebuild --with 'xxx'
%{?_with_test: %{expand: %%global build_test 1}}
%{?_without_test: %{expand: %%global build_test 0}}

%define TAG Mandriva Linux
%define BASEPRODUCT Apache

Summary:	Implements a non-threaded, pre-forking web server with RSABC patch (stable)
Name:		apache-mpm-rsbac
Version:	%{version}
Release:	%{release}
Group:		System/Servers
License:	Apache License
URL:		http://www.apache.org
# http://svn.rsbac.org/?do=browse&project=rsbac-apache&path=%2Fmod_rsbac%2Fapache%2Brsbac%2F
Patch1:		httpd-2.2.9-rsbac.patch
BuildRequires:	apache-source = %{version}-%{release}
BuildRequires:	apache-devel = %{version}-%{release}
BuildRequires:	apr-devel >= 1:1.3.0
BuildRequires:	apr-util-devel >= 1.3.0
BuildRequires:	distcache-devel
BuildRequires:	byacc
BuildRequires:	db4-devel
BuildRequires:	expat-devel
BuildRequires:	gdbm-devel
BuildRequires:	libsasl-devel
BuildRequires:	libtool >= 1.4.2
BuildRequires:	openldap-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel >= 5.0
BuildRequires:	perl >= 0:5.600
BuildRequires:	pkgconfig
BuildRequires:	rsbac-devel
BuildRequires:	zlib-devel
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	lynx
BuildRequires:	libcap-devel
%if %{build_test}
BuildRequires:	perl-Apache-Test
BuildRequires:	perl-CGI >= 1:3.11
BuildRequires:	perl-HTML-Parser
BuildRequires:	perl-libwww-perl
BuildRequires:	perl-Tie-IxHash
BuildRequires:	perl-URI
BuildRequires:	perl-BSD-Resource
BuildRequires:	subversion
BuildRequires:	perl-HTTP-DAV
BuildRequires:	perl-doc
BuildRequires:	perl-Crypt-SSLeay
BuildRequires:	perl-XML-DOM
BuildRequires:	perl-XML-Parser
BuildRequires:	openssl
%endif
%if %mdkversion >= 1020
BuildRequires:	multiarch-utils >= 1.0.3
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= %{version}
Requires(pre):	apache-base = %{version}-%{release}
Requires(pre):	apache-modules = %{version}-%{release}
Requires:	apache-conf >= %{version}
Requires:	apache-base = %{version}-%{release}
Requires:	apache-modules = %{version}-%{release}
Requires:	apache-mod_rsbac
Provides:	webserver
Provides:	apache = %{version}-%{release}
Provides:	apache-mpm = %{version}-%{release}

%description
This Multi-Processing Module (MPM) implements a non-threaded, pre-forking web
server that handles requests in a manner similar to Apache 1.3. It is
appropriate for sites that need to avoid threading for compatibility with
non-thread-safe libraries. It is also the best MPM for isolating each request,
so that a problem with a single request will not affect any other.
This MPM contain the RSBAC support but the extra features is 
the mod_rsbac packages. You see a more information is mod_rsbac package.

mpm-rsbac is based on the traditional prefork MPM, which means it's non-threaded;
in short, this means you can run non-thread-aware code (like many PHP
extensions) without problems. (On the other hand, you lose out to any
performance benefit you'd get with threads, of course; you'd have to decide for
yourself if that's worth it or not.)

This MPM is very self-regulating, so it is rarely necessary to adjust its
configuration directives. Most important is that MaxClients be big enough to
handle as many simultaneous requests as you expect to receive, but small enough
to assure that there is enough physical RAM for all processes.

Check for available Apache modules here: http://nux.se/apache/

This package defaults to a maximum of %{defaultmaxmodules} dynamically loadable modules.
This package defaults to a ServerLimit of %{defaultserverlimit}.

You can change these values at RPM build time by using for example:

--define 'maxmodules 512' --define 'serverlimit 2048' 

The package was built to support a maximum of %{?!maxmodules:%{defaultmaxmodules}}%{?maxmodules:%{maxmodules}} dynamically loadable modules.
The package was built with a ServerLimit of %{?!serverlimit:%{defaultserverlimit}}%{?serverlimit:%{serverlimit}}.

I M P O R T A N T
-----------------
This package is only to the RSBAC enabled kernels and may not be stable 
or suitable at any time, in any way, or for any kind production usage. 
Be warned. You must manually add HTTPD="/usr/sbin/httpd-rsbac" in the 
/etc/sysconfig/httpd configuration file to be able to use this MPM.

%prep
%setup -T -c -n apache-%{version}
cp -r /usr/src/apache-%{version}/* .
%patch1 -p1 -b .mpm_rsbac.droplet
cp %{PATCH1} httpd-%{version}-rsbac.patch

%build

#########################################################################################
# configure and build phase
#
export WANT_AUTOCONF_2_5="1"

CFLAGS="`echo $RPM_OPT_FLAGS |sed -e 's/-fomit-frame-pointer//'`"
CPPFLAGS="-DSSL_EXPERIMENTAL_ENGINE -DLDAP_DEPRECATED -DHAVE_APR_MEMCACHE"
if pkg-config openssl; then
    # configure -C barfs with trailing spaces in CFLAGS
    CFLAGS="$RPM_OPT_FLAGS $CPPFLAGS"
    CPPFLAGS="$CPPFLAGS `pkg-config --cflags openssl | sed 's/ *$//'`"
    AP_LIBS="$AP_LIBS `pkg-config --libs openssl`"
else
    CFLAGS="$RPM_OPT_FLAGS"
    CPPFLAGS="$CPPFLAGS"
    AP_LIBS="$AP_LIBS -lssl -lcrypto"
fi
export CFLAGS CPPFLAGS AP_LIBS

export SH_LDFLAGS="%{ldflags}"

APVARS="--enable-layout=NUX \
    --prefix=%{_sysconfdir}/httpd \
    --exec-prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --sbindir=%{_sbindir} \
    --libexecdir=%{_libdir}/apache \
    --sysconfdir=%{_sysconfdir}/httpd/conf \
    --localstatedir=/var \
    --includedir=%{_includedir}/apache \
    --infodir=%{_infodir} \
    --mandir=%{_mandir} \
    --datadir=/var/www \
    --with-port=80 \
    --with-perl=%{_bindir}/perl \
    --with-apr=%{_bindir}/apr-1-config \
    --with-apr-util=%{_bindir}/apu-1-config \
    --with-pcre=%{_prefix} \
    --with-z=%{_prefix} \
    --enable-layout=NUX \
    --with-devrandom \
    --enable-exception-hook \
    --enable-forward \
    --with-program-name=httpd"

for mpm in rsbac; do
    mkdir build-${mpm}; pushd build-${mpm}
    ln -s ../configure .
    
    if [ ${mpm} = rsbac ]; then
	%configure2_5x $APVARS \
    	    --with-rsbac \
    	    --with-mpm=prefork \
	    --enable-modules=none
    # don't build support tools
    perl -pi -e "s|^SUBDIRS = .*|SUBDIRS = os server modules|g" Makefile
    fi

    #Copy configure flags to a file in the apache-source rpm.
    #cp config.nice $RPM_BUILD_DIR/tmp-httpd-%{version}%{_usrsrc}/apache-%{version}/config.nice.${mpm}

    # tag it with the mpm name too so that we can track this somehow at for example netcraft...
    MPM_NAME=`echo ${mpm}|tr "[a-z]" "[A-Z]"`
    #cp ../server/core.c.untagged ../server/core.c
    perl -pi -e "s|\" PLATFORM \"|%{TAG}/${MPM_NAME}-%{release}|g" ../server/core.c

    # if libexpat0-devel is installed on x86_64 somehow the EXTRA_LDLAGS is set 
    # to -L/usr/lib, fix that with a conditional hack...
    %ifarch x86_64
	find -type f | xargs perl -pi -e "s|/usr/lib\b|%{_libdir}|g"
    %endif

    # there is no autofoo stuff the memcache addon yet
    perl -pi -e "s|-ldistcache -lnal|-ldistcache -lnal|g" build/config_vars.mk

    # finally doing the build stage
    %make
    popd
done

%if %{build_test}
# run the test suite, quite a hack, but works, sometimes...
TEST_DIR="`pwd`/TEST"
make -C build-rsbac DESTDIR=${TEST_DIR} \
	manualdir=${TEST_DIR}/var/www/html/manual \
	install

perl -pi -e "s|%{_libdir}/apache/|${TEST_DIR}%{_libdir}/apache/|g" ${TEST_DIR}%{_sysconfdir}/httpd/conf/*
perl -pi -e "s|^#Include|Include|g" ${TEST_DIR}%{_sysconfdir}/httpd/conf/httpd.conf
perl -pi -e "s|/etc|${TEST_DIR}/etc|g" ${TEST_DIR}%{_sysconfdir}/httpd/conf/httpd.conf ${TEST_DIR}%{_sysconfdir}/httpd/conf/extra/*.conf
perl -pi -e  "s|%{_libdir}/apache/build|${TEST_DIR}%{_libdir}/apache/build|g" ${TEST_DIR}%{_sbindir}/apxs

# fool apxs
cat >> ${TEST_DIR}%{_libdir}/apache/build/config_vars.mk << EOF
bindir = ${TEST_DIR}/usr/bin
sbindir = ${TEST_DIR}/usr/sbin
exec_prefix = ${TEST_DIR}/usr
datadir = ${TEST_DIR}/var/www
localstatedir = ${TEST_DIR}/var
libdir = ${TEST_DIR}%{_libdir}
libexecdir = ${TEST_DIR}%{_libdir}/apache
includedir = ${TEST_DIR}/usr/include/apache
sysconfdir = ${TEST_DIR}/etc/httpd/conf
installbuilddir = ${TEST_DIR}%{_libdir}/apache/build
runtimedir = ${TEST_DIR}/var/run
proxycachedir = ${TEST_DIR}/var/cache/httpd/mod_proxy
prefix = ${TEST_DIR}/usr
EOF

svn checkout --ignore-externals http://svn.apache.org/repos/asf/httpd/test/framework/trunk/ perl-framework
#svn checkout http://svn.apache.org/repos/asf/httpd/test/framework/trunk/ perl-framework
#svn up
pushd perl-framework

# disable test cases for bugs that has not been fixed yet,are too old, or
# it is unclear who to blaim, either the php or ASF folks...
rm -f t/php/arg.t
rm -f t/php/func5.t

# this test works with php-5.0 but not with php-5.1, yuck!
rm -f t/php/virtual.t

# if not using LC_ALL=C t/php/getlastmod.t can fail at
# testing : getlastmod()
# expected: november
# received: November
export LC_ALL=C

mkdir -p ${TEST_DIR}%{_sbindir}
cp %{_sbindir}/apxs ${TEST_DIR}%{_sbindir}

perl Makefile.PL -apxs ${TEST_DIR}%{_sbindir}/apxs \
    -httpd_conf ${TEST_DIR}%{_sysconfdir}/httpd/conf/httpd.conf \
    -httpd ${TEST_DIR}%{_sbindir}/httpd
make test
popd
%endif

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 
#########################################################################################
# install phase
make -C build-rsbac DESTDIR=`pwd` install-conf

# install the mpm stuff
install -d %{buildroot}%{_sbindir}
install -m0755 build-rsbac/httpd %{buildroot}%{_sbindir}/httpd-rsbac

#########################################################################################
# install phase done
#

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%files
%defattr(-,root,root)
%doc etc/httpd/conf/httpd.conf etc/httpd/conf/extra/*.conf httpd-%{version}-rsbac.patch
%attr(0755,root,root) %{_sbindir}/httpd-rsbac

