# Wazuh dashboard SPEC
# Copyright (C) 2021, Wazuh Inc.
#
# This program is a free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.
Summary:     Wazuh dashboard is a user interface and visualization tool for security-related data. Documentation can be found at https://documentation.wazuh.com/current/getting-started/components/wazuh-dashboard.html
Name:        wazuh-dashboard
Version:     %{_version}
Release:     %{_release}
License:     GPL
Group:       System Environment/Daemons
Source0:     %{name}-%{version}.tar.gz
URL:         https://www.wazuh.com/
buildroot:   %{_tmppath}/%{name}-%{version}-%{release}-wazuh-dashboard-%(%{__id_u} -n)
Vendor:      Wazuh, Inc <info@wazuh.com>
Packager:    Wazuh, Inc <info@wazuh.com>
Requires(pre):    /usr/sbin/groupadd /usr/sbin/useradd
Requires(preun):  /sbin/service
Requires(postun): /sbin/service
AutoReqProv: no
Requires: libcap
ExclusiveOS: linux

# -----------------------------------------------------------------------------

%global USER %{name}
%global GROUP %{name}
%global CONFIG_DIR /etc/%{name}
%global PID_DIR /run/%{name}
%global INSTALL_DIR /usr/share/%{name}
%global DASHBOARD_FILE wazuh-dashboard-base-%{version}-%{release}-linux-x64.tar.xz
%define _source_payload w9.gzdio
%define _binary_payload w9.gzdio

# -----------------------------------------------------------------------------


%description
Wazuh dashboard is a user interface and visualization tool for security-related data. This Wazuh central component enables exploring, visualizing, and analyzing the stored security alerts generated by the Wazuh server. Wazuh dashboard enables inspecting the status and managing the configurations of the Wazuh cluster and agents as well as creating and managing users and roles. In addition, it allows testing the ruleset and making calls to the Wazuh API. Documentation can be found at https://documentation.wazuh.com/current/getting-started/components/wazuh-dashboard.html

# -----------------------------------------------------------------------------

%prep

cp /tmp/%{DASHBOARD_FILE} ./

groupadd %{GROUP}
useradd -g %{GROUP} %{USER}

# -----------------------------------------------------------------------------

%build

tar -xf %{DASHBOARD_FILE}

# Set custom config dir
sed -i 's/OSD_NODE_OPTS_PREFIX/OSD_PATH_CONF="\/etc\/wazuh-dashboard" OSD_NODE_OPTS_PREFIX/g' "wazuh-dashboard-base/bin/opensearch-dashboards"
sed -i 's/OSD_USE_NODE_JS_FILE_PATH/OSD_PATH_CONF="\/etc\/wazuh-dashboard" OSD_USE_NODE_JS_FILE_PATH/g' "wazuh-dashboard-base/bin/opensearch-dashboards-keystore"

# -----------------------------------------------------------------------------

%install

mkdir -p %{buildroot}%{CONFIG_DIR}
mkdir -p %{buildroot}%{INSTALL_DIR}
mkdir -p %{buildroot}/etc/systemd/system
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}/etc/default

cp wazuh-dashboard-base/etc/node.options %{buildroot}%{CONFIG_DIR}
cp wazuh-dashboard-base/etc/opensearch_dashboards.yml %{buildroot}%{CONFIG_DIR}
cp wazuh-dashboard-base/VERSION %{buildroot}%{INSTALL_DIR}

mv wazuh-dashboard-base/* %{buildroot}%{INSTALL_DIR}

# Set custom welcome styles

mkdir -p %{buildroot}%{INSTALL_DIR}/config

cp %{buildroot}%{INSTALL_DIR}/etc/services/wazuh-dashboard.service %{buildroot}/etc/systemd/system/wazuh-dashboard.service
cp %{buildroot}%{INSTALL_DIR}/etc/services/default %{buildroot}/etc/default/wazuh-dashboard

chmod 640 %{buildroot}/etc/systemd/system/wazuh-dashboard.service
chmod 640 %{buildroot}/etc/default/wazuh-dashboard

rm -rf %{buildroot}%{INSTALL_DIR}/etc/

find %{buildroot}%{INSTALL_DIR} -exec chown %{USER}:%{GROUP} {} \;
find %{buildroot}%{CONFIG_DIR} -exec chown %{USER}:%{GROUP} {} \;

chown root:root %{buildroot}/etc/systemd/system/wazuh-dashboard.service

if [ "%{version}" = "99.99.0" ];then
    runuser %{USER} --shell="/bin/bash" --command="%{buildroot}%{INSTALL_DIR}/bin/opensearch-dashboards-plugin install https://packages-dev.wazuh.com/futures/ui/dashboard/wazuh-99.99.0-%{release}.zip"
    runuser %{USER} --shell="/bin/bash" --command="%{buildroot}%{INSTALL_DIR}/bin/opensearch-dashboards-plugin install https://packages-dev.wazuh.com/futures/ui/dashboard/wazuhCheckUpdates-99.99.0-%{release}.zip"
    runuser %{USER} --shell="/bin/bash" --command="%{buildroot}%{INSTALL_DIR}/bin/opensearch-dashboards-plugin install https://packages-dev.wazuh.com/futures/ui/dashboard/wazuhCore-99.99.0-%{release}.zip"
else
    runuser %{USER} --shell="/bin/bash" --command="%{buildroot}%{INSTALL_DIR}/bin/opensearch-dashboards-plugin install %{_url_plugin_main}"
    runuser %{USER} --shell="/bin/bash" --command="%{buildroot}%{INSTALL_DIR}/bin/opensearch-dashboards-plugin install %{_url_plugin_updates}"
    runuser %{USER} --shell="/bin/bash" --command="%{buildroot}%{INSTALL_DIR}/bin/opensearch-dashboards-plugin install %{_url_plugin_core}"
fi

find %{buildroot}%{INSTALL_DIR}/plugins/wazuh/ -exec chown %{USER}:%{GROUP} {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuh/ -type f -perm 644 -exec chmod 640 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuh/ -type f -perm 755 -exec chmod 750 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuh/ -type d -exec chmod 750 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuh/ -type f -perm 744 -exec chmod 740 {} \;

find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCheckUpdates/ -exec chown %{USER}:%{GROUP} {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCheckUpdates/ -type f -perm 644 -exec chmod 640 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCheckUpdates/ -type f -perm 755 -exec chmod 750 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCheckUpdates/ -type d -exec chmod 750 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCheckUpdates/ -type f -perm 744 -exec chmod 740 {} \;

find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCore/ -exec chown %{USER}:%{GROUP} {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCore/ -type f -perm 644 -exec chmod 640 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCore/ -type f -perm 755 -exec chmod 750 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCore/ -type d -exec chmod 750 {} \;
find %{buildroot}%{INSTALL_DIR}/plugins/wazuhCore/ -type f -perm 744 -exec chmod 740 {} \;
# -----------------------------------------------------------------------------

%pre
# Create the wazuh-dashboard group if it doesn't exists
if [ $1 = 1 ]; then
  if command -v getent > /dev/null 2>&1 && ! getent group %{GROUP} > /dev/null 2>&1; then
    groupadd -r %{GROUP}
  elif ! getent group %{GROUP} > /dev/null 2>&1; then
    groupadd -r %{GROUP}
  fi
  # Create the wazuh-dashboard user if it doesn't exists
  if ! getent passwd %{USER} > /dev/null 2>&1; then
    useradd -g %{GROUP} -G %{USER} -d %{INSTALL_DIR}/ -r -s /sbin/nologin wazuh-dashboard
  fi
fi
# Stop the services to upgrade the package
if [ $1 = 2 ]; then
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 && systemctl is-active --quiet wazuh-dashboard > /dev/null 2>&1; then
    systemctl stop wazuh-dashboard.service > /dev/null 2>&1
    touch %{INSTALL_DIR}/wazuh-dashboard.restart
  # Check for SysV
  elif command -v service > /dev/null 2>&1 && service wazuh-dashboard status 2>/dev/null | grep "is running" > /dev/null 2>&1; then
    service wazuh-dashboard stop > /dev/null 2>&1
    touch %{INSTALL_DIR}/wazuh-dashboard.restart
  fi
fi

# -----------------------------------------------------------------------------

%post
setcap 'cap_net_bind_service=+ep' %{INSTALL_DIR}/node/bin/node
setcap 'cap_net_bind_service=+ep' %{INSTALL_DIR}/node/fallback/bin/node

# -----------------------------------------------------------------------------

%preun
if [ $1 = 0 ];then # Remove
  echo -n "Stopping wazuh-dashboard service..."
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1; then
      systemctl stop wazuh-dashboard.service > /dev/null 2>&1
  # Check for SysV
  elif command -v service > /dev/null 2>&1; then
    service wazuh-dashboard stop > /dev/null 2>&1
  fi
fi

# -----------------------------------------------------------------------------

%postun
if [ $1 = 0 ];then
  # If the package is been uninstalled
  # Remove the wazuh-dashboard user if it exists
  if getent passwd %{USER} > /dev/null 2>&1; then
    userdel %{USER} >/dev/null 2>&1
  fi
  # Remove the wazuh-dashboard group if it exists
  if command -v getent > /dev/null 2>&1 && getent group %{GROUP} > /dev/null 2>&1; then
    groupdel %{GROUP} >/dev/null 2>&1
  elif getent group %{GROUP} > /dev/null 2>&1; then
    groupdel %{GROUP} >/dev/null 2>&1
  fi

  # Remove /etc/wazuh-dashboard and /usr/share/wazuh-dashboard dirs
  rm -rf %{INSTALL_DIR}
  if [ -d %{PID_DIR} ]; then
    rm -rf %{PID_DIR}
  fi
fi

# -----------------------------------------------------------------------------

# posttrans code is the last thing executed in a install/upgrade
%posttrans
if [ ! -d %{PID_DIR} ]; then
    mkdir -p %{PID_DIR}
    chown %{USER}:%{GROUP} %{PID_DIR}
fi

# Move keystore file if upgrade (file exists in install dir in <= 4.6.0)
if [ -f "%{INSTALL_DIR}"/config/opensearch_dashboards.keystore ]; then
  mv "%{INSTALL_DIR}"/config/opensearch_dashboards.keystore "%{CONFIG_DIR}"/opensearch_dashboards.keystore
elif [ ! -f %{CONFIG_DIR}/opensearch_dashboards.keystore ]; then
  runuser %{USER} --shell="/bin/bash" --command="%{INSTALL_DIR}/bin/opensearch-dashboards-keystore create" > /dev/null 2>&1
  runuser %{USER} --shell="/bin/bash" --command="echo kibanaserver | %{INSTALL_DIR}/bin/opensearch-dashboards-keystore add opensearch.username --stdin" > /dev/null 2>&1
  runuser %{USER} --shell="/bin/bash" --command="echo kibanaserver | %{INSTALL_DIR}/bin/opensearch-dashboards-keystore add opensearch.password --stdin" > /dev/null 2>&1
  chmod 640 "%{CONFIG_DIR}"/opensearch_dashboards.keystore
fi

if ! grep -q "/app/wz-home" %{CONFIG_DIR}/opensearch_dashboards.yml; then
  sed -i 's/\/app\/wazuh/\/app\/wz-home/g' %{CONFIG_DIR}/opensearch_dashboards.yml
fi

if [ -f %{INSTALL_DIR}/wazuh-dashboard.restart ]; then
  rm -f %{INSTALL_DIR}/wazuh-dashboard.restart
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1; then
    systemctl restart wazuh-dashboard.service > /dev/null 2>&1
  # Check for SysV
  elif command -v service > /dev/null 2>&1; then
    service wazuh-dashboard restart > /dev/null 2>&1
  fi

fi


# -----------------------------------------------------------------------------

%clean
rm -fr %{buildroot}

# -----------------------------------------------------------------------------

%files
%defattr(-,%{USER},%{GROUP})

%dir %attr(750, %{USER}, %{GROUP}) %{CONFIG_DIR}
%dir %attr(750, %{USER}, %{GROUP}) %{INSTALL_DIR}
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/node"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/node_modules"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/data"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/plugins"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/bin"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/config"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/core"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/remove"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/list"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/lib"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/downloaders"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/__fixtures__"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/__fixtures__/replies"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_keystore"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_keystore/utils"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/setup_node_env"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/setup_node_env/root"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/setup_node_env/harden"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route/__fixtures__"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route/__fixtures__/plugin"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route/__fixtures__/plugin/foo"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/plugins"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve/integration_tests"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve/integration_tests/__fixtures__"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve/integration_tests/__fixtures__/reload_logging_config"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/utils"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/logging"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/logging/rotate"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/core"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/i18n"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/i18n/localization"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/warnings"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/http"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/config"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/keystore"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/apm"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/ui_render"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/ui_render/bootstrap"
%dir %attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/docs"

%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/*.json"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/*.yml"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/*.txt"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/remove/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/list/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/downloaders/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/__fixtures__/replies/*.zip"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/install/__fixtures__/replies/*.jpg"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_keystore/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_keystore/utils/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/setup_node_env/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/setup_node_env/root/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/setup_node_env/harden/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route/__fixtures__/plugin/foo/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/optimize/bundles_route/__fixtures__/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve/integration_tests/__fixtures__/*.yml"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli/serve/integration_tests/__fixtures__/reload_logging_config/*.yml"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/cli_plugin/lib/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/utils/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/logging/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/logging/rotate/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/core/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/i18n/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/i18n/localization/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/warnings/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/http/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/config/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/server/keystore/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/ui_render/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/ui_render/bootstrap/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/ui_render/bootstrap/*.hbs"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/legacy/ui/apm/*.js"
%attr(640, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/docs/*.js"

%attr(-, %{USER}, %{GROUP}) "%{INSTALL_DIR}/node/*"
%attr(-, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/core/*"
%attr(-, %{USER}, %{GROUP}) "%{INSTALL_DIR}/src/plugins/*
%attr(-, %{USER}, %{GROUP}) "%{INSTALL_DIR}/node_modules/*"
%attr(-, %{USER}, %{GROUP}) "%{INSTALL_DIR}/plugins/*"

%attr(440, %{USER}, %{GROUP}) "%{INSTALL_DIR}/VERSION"
%attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/node_modules/.yarn-integrity"
%attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/bin/use_node"
%attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/bin/opensearch-dashboards"
%attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/bin/opensearch-dashboards-plugin"
%attr(750, %{USER}, %{GROUP}) "%{INSTALL_DIR}/bin/opensearch-dashboards-keystore"
%attr(750, %{USER}, %{GROUP}) "/etc/default/wazuh-dashboard"
%attr(640, %{USER}, %{GROUP}) "%{CONFIG_DIR}/node.options"
%attr(640, root, root) "/etc/systemd/system/wazuh-dashboard.service"
%config(noreplace) %attr(640, %{USER}, %{GROUP}) "%{CONFIG_DIR}/opensearch_dashboards.yml"

%changelog
* Tue Oct 01 2024 support <info@wazuh.com> - 4.10.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-10-0.html
* Wed Jul 10 2024 support <info@wazuh.com> - 4.9.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-9-0.html
* Wed Jun 26 2024 support <info@wazuh.com> - 4.8.1
- More info: https://documentation.wazuh.com/current/release-notes/release-4-8-1.html
* Wed Jun 12 2024 support <info@wazuh.com> - 4.8.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-8-0.html
* Thu May 30 2024 support <info@wazuh.com> - 4.7.5
- More info: https://documentation.wazuh.com/current/release-notes/release-4-7-5.html
* Thu Apr 25 2024 support <info@wazuh.com> - 4.7.4
- More info: https://documentation.wazuh.com/current/release-notes/release-4-7-4.html
* Tue Feb 27 2024 support <info@wazuh.com> - 4.7.3
- More info: https://documentation.wazuh.com/current/release-notes/release-4-7-3.html
* Tue Jan 09 2024 support <info@wazuh.com> - 4.7.2
- More info: https://documentation.wazuh.com/current/release-notes/release-4-7-2.html
* Wed Dec 13 2023 support <info@wazuh.com> - 4.7.1
- More info: https://documentation.wazuh.com/current/release-notes/release-4-7-1.html
* Tue Nov 21 2023 support <info@wazuh.com> - 4.7.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-7-0.html
* Tue Oct 31 2023 support <info@wazuh.com> - 4.6.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-6-0.html
* Tue Oct 24 2023 support <info@wazuh.com> - 4.5.4
- More info: https://documentation.wazuh.com/current/release-notes/release-4-5-4.html
* Tue Oct 10 2023 support <info@wazuh.com> - 4.5.3
- More info: https://documentation.wazuh.com/current/release-notes/release-4-5-3.html
* Thu Aug 31 2023 support <info@wazuh.com> - 4.5.2
- More info: https://documentation.wazuh.com/current/release-notes/release-4-5-2.html
* Thu Aug 24 2023 support <info@wazuh.com> - 4.5.1
- More info: https://documentation.wazuh.com/current/release-notes/release-4-5.1.html
* Thu Aug 10 2023 support <info@wazuh.com> - 4.5.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-5-0.html
* Mon Jul 10 2023 support <info@wazuh.com> - 4.4.5
- More info: https://documentation.wazuh.com/current/release-notes/release-4-4-5.html
* Tue Jun 13 2023 support <info@wazuh.com> - 4.4.4
- More info: https://documentation.wazuh.com/current/release-notes/release-4-4-4.html
* Thu May 25 2023 support <info@wazuh.com> - 4.4.3
- More info: https://documentation.wazuh.com/current/release-notes/release-4-4-3.html
* Mon Apr 24 2023 support <info@wazuh.com> - 4.4.2
- More info: https://documentation.wazuh.com/current/release-notes/release-4-4-2.html
* Mon Apr 17 2023 support <info@wazuh.com> - 4.4.1
- More info: https://documentation.wazuh.com/current/release-notes/release-4-4-1.html
* Wed Jan 18 2023 support <info@wazuh.com> - 4.4.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-4-0.html
* Thu Nov 10 2022 support <info@wazuh.com> - 4.3.10
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-10.html
* Mon Oct 03 2022 support <info@wazuh.com> - 4.3.9
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-9.html
* Mon Sep 19 2022 support <info@wazuh.com> - 4.3.8
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-8.html
* Mon Aug 08 2022 support <info@wazuh.com> - 4.3.7
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-7.html
* Thu Jul 07 2022 support <info@wazuh.com> - 4.3.6
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-6.html
* Wed Jun 29 2022 support <info@wazuh.com> - 4.3.5
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-5.html
* Tue Jun 07 2022 support <info@wazuh.com> - 4.3.4
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-4.html
* Tue May 31 2022 support <info@wazuh.com> - 4.3.3
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-3.html
* Mon May 30 2022 support <info@wazuh.com> - 4.3.2
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-2.html
* Wed May 18 2022 support <info@wazuh.com> - 4.3.1
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-1.html
* Thu May 05 2022 support <info@wazuh.com> - 4.3.0
- More info: https://documentation.wazuh.com/current/release-notes/release-4-3-0.html
