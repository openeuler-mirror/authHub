Name:		authhub
Version:	v1.0.0
Release:	1
Summary:	Authentication authority based on oauth2
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz
Source1:	node_modules.tar.gz

BuildRequires:  python3-setuptools
Requires:  aops-vulcanus >= v2.1.0 python3-Authlib aops-zeus >= v2.1.0 
Provides:  authhub

%description
authhub is a specialized authentication center built on OAuth2, providing robust authentication and authorization capabilities for secure user access control in your applications..

%package -n authhub-web
Summary: Authentication authority web based on oauth2

BuildRequires: nodejs
Requires:  nginx

%description -n authhub-web
Authentication authority web based on oauth2

%prep
%autosetup -n %{name}-%{version}
%setup -T -D -a 1 -n %{name}-%{version}/oauth2_web
cd %{_builddir}/%{name}-%{version}

# build for authhub
%py3_build

# build for authhub-web
pushd oauth2_web
npm run build
popd

# install for authhub
%py3_install

# install for authhub-web
pushd oauth2_web
mkdir -p %{buildroot}/opt/authhub/web/
cp -r dist %{buildroot}/opt/authhub/web/
cp deploy/authhub.nginx.conf /etc/nginx/conf.d/
popd

%files
%attr(0644,root,root) %{_sysconfdir}/aops/conf.d/authhub.yml
%attr(0755,root,root) %{_unitdir}/authhub.service
%attr(0755, root, root) /opt/aops/database/*
%{python3_sitelib}/authhub*.egg-info
%{python3_sitelib}/oauth2_provider/*

%files -n authhub-web
%attr(0755, root, root) /opt/authhub/web/dist/*
%attr(0755,root,root) %{_unitdir}/authhub-web.service

%changelog
* Mon Aug 19 2024 gongzhengtang<gong_zhengtang@163.com> - v1.0.0-1
- Package init

