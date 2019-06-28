# -*- coding: utf-8 -*-
"""
BME280 Plugin.

Publishes temperature, pressure and humidity from BME280 i2c sensor

BME280 code is from Matt Hawkins / www.raspberrypi-spy.co.uk
"""
import collectd
from bme280 import BME280

# Global definitions
plugin_name = "bme280"
# Recommended profile from datasheet - weather monitoring profile:
#   - pressure x 1, temperature x 1, humidity x 1
#   - forced mode, 1 sample / minute
sample_interval = 60
osrs_t = osrs_p = osrs_h = 1

# Collectd paramters: device I2C address and I2C bus
bme280_address = 0x76
bme280_smbus = 1

# bme280 instance
bme280 = None


def config(config):
    """Gets parameters from collectd configuration"""
    global bme280_address, bme280_smbus

    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'bme280address':
            bme280_address = int(val, 0)
            collectd.info('bme280 plugin: device address set to {0}'
                          .format(hex(bme280_address)))
        elif key == 'bme280smbus':
            bme280_smbus = int(val)
            collectd.info('bme280 plugin: SMBus set to {0}'
                          .format(bme280_smbus))


def init():
    """Initializes BME280"""
    global bme280
    bme280 = BME280(bme280_smbus, bme280_address)


def read():
    """Read sensor data and dispatch values"""
    bme280.read_data(osrs_t, osrs_p, osrs_h)

    v_temp = collectd.Values(plugin=plugin_name, type='temperature')
    v_temp.dispatch(values=[bme280.get_temperature()])
    v_pres = collectd.Values(plugin=plugin_name, type='pressure')
    v_pres.dispatch(values=[bme280.get_pressure()])
    v_humi = collectd.Values(plugin=plugin_name, type='humidity')
    v_humi.dispatch(values=[bme280.get_humidity()])


# Register callback
collectd.register_config(config, name=plugin_name)
collectd.register_init(init, name=plugin_name)
collectd.register_read(read, interval=sample_interval, name=plugin_name)