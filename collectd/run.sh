#!/bin/bash
# Fix Collectd configuration file and start daemon

Config="/etc/collectd/collectd.conf"
ConfigNetwork="/etc/collectd/collectd.conf.d/network.conf"
ConfigPython="/etc/collectd/collectd.conf.d/python.conf"

echo "*** Starting TTN Collectd daemon"

if [ "${RESIN}" = "1" ]
then
  echo "*** Running in balena-cloud.com environment"

  # Expunge unexpanded variables from docker-compose
  GwVars=$(compgen -A variable GW_)
  for GwVar in ${GwVars}
  do
    [[ ${!GwVar} == \$\{* ]] && unset ${GwVar}
  done
  unset GwVars

  # Set hostname, we take GW_ID, or Resin device name
  HostName="${GW_ID:-$RESIN_DEVICE_NAME_AT_INIT}"
  echo "*** Setting hostname to ${HostName}"
  sed -i "s/^FQDNLookup .*/FQDNLookup false/" "${Config}"
  sed -i "s/^#Hostname .*/Hostname \"${HostName}\"/" "${Config}"
fi

if [ -n "${GW_COLLECTD_SERVER}" ]
then
  echo "*** Collectd server: ${GW_COLLECTD_SERVER}"
  sed -i "s/^\tServer .*/\tServer \"${GW_COLLECTD_SERVER}\"/" "${ConfigNetwork}"
else
  echo "*** Collectd server: Standard"
fi

if [ -n "${GW_COLLECTD_INTERVAL}" ]
then
  echo "*** Collectd interval: ${GW_COLLECTD_INTERVAL}"
  sed -i "s/^#Interval .*/Interval ${GW_COLLECTD_INTERVAL}/" "${Config}"
fi

if [ "${GW_BME280}" = "true" ]
then
  echo "*** Support for BME280 enabled"
  sed -i 's/##BME280## //' "${ConfigPython}"
  if [ -n "${GW_BME280_ADDR}" ]
  then
    sed -i "s/BME280Address .*/BME280Address \"${GW_BME280_ADDR}\"/" "${ConfigPython}"
  fi
  if [ -n "${GW_BME280_SMBUS}" ]
  then
    sed -i "s/BME280SMBus .*/BME280SMBus ${GW_BME280_SMBUS}/" "${ConfigPython}"
  fi
fi

exec collectd -C "${Config}" -f
