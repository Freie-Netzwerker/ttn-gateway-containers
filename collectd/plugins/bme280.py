#!/usr/bin/env python
# -*- coding: utf-8 -*-

 # Read data from the Bosch BME280 environmental sensor
#    Official datasheet available from :
#    https://www.bosch-sensortec.com/bst/products/all_products/bme280

 import smbus
import time


 class BME280:
    """Class to read temperature, pressure and humidity from BME280 sensor """

     # Default hardware parameters
    _BME280_ADDR = 0x76
    _SMBUS_BUS = 1

     # NVM addresses
    # Triming paramters (Datasheet 4.2.2)
    # 3 callib with their size
    _TRIM_BLOCK = (
        (0x88, 24),
        (0xA1, 1),
        (0xE1, 7)
    )
    # Registers adresses
    _REG_ID = 0xD0
    _REG_CTRL_HUM = 0xF2
    _REG_CTRL_MEAS = 0xF4
    _REG_CONFIG = 0xF5
    _REG_PRESS = 0xF7

     # Read mode
    _MODE_FORCED = 1

     def __init__(self, smbus_bus=_SMBUS_BUS, bme280_addr=_BME280_ADDR):
        """Initializes the device and reads triming parameters
        """
        self.bus = smbus.SMBus(smbus_bus)
        self.addr = bme280_addr

         # Read trimming parameters
        callib = []
        for block in self._TRIM_BLOCK:
            callib.append(self.bus.read_i2c_block_data(bme280_addr, block[0], block[1]))  # noqa

         # Convert byte data to word values
        self.dig_t1 = BME280._get_uint16(callib[0], 0)
        self.dig_t2 = BME280._get_int16(callib[0], 2)
        self.dig_t3 = BME280._get_int16(callib[0], 4)

         self.dig_p1 = BME280._get_uint16(callib[0], 6)
        self.dig_p2 = BME280._get_int16(callib[0], 8)
        self.dig_p3 = BME280._get_int16(callib[0], 10)
        self.dig_p4 = BME280._get_int16(callib[0], 12)
        self.dig_p5 = BME280._get_int16(callib[0], 14)
        self.dig_p6 = BME280._get_int16(callib[0], 16)
        self.dig_p7 = BME280._get_int16(callib[0], 18)
        self.dig_p8 = BME280._get_int16(callib[0], 20)
        self.dig_p9 = BME280._get_int16(callib[0], 22)

         self.dig_h1 = BME280._get_uint8(callib[1], 0)
        self.dig_h2 = BME280._get_int16(callib[2], 0)
        self.dig_h3 = BME280._get_uint8(callib[2], 2)

         # H4 and H5 are 12 bits signed
        self.dig_h4 = (callib[2][3] << 4) | (callib[2][4] & 0x0F)
        self.dig_h4 = (self.dig_h4 & 0x7ff) - (self.dig_h4 & 0x800)

         self.dig_h5 = (callib[2][5] << 4) | (callib[2][4] >> 4)
        self.dig_h5 = (self.dig_h5 & 0x7ff) - (self.dig_h5 & 0x800)

         self.dig_h6 = BME280._get_int8(callib[2], 6)

     def get_id(self):
        """Returns the chip identification number"""
        chip_id = self.bus.read_byte_data(self.addr, self._REG_ID)
        return chip_id

     def read_data(self, osrs_t=1, osrs_p=1, osrs_h=1):
        """Read sensor data in forced mode"""

         # Setcontrol registers, humidity needs to be done first
        self.bus.write_byte_data(self.addr, self._REG_CTRL_HUM, osrs_h)

         ctrl = osrs_t << 5 | osrs_p << 2 | self._MODE_FORCED
        self.bus.write_byte_data(self.addr, self._REG_CTRL_MEAS, ctrl)

         # Measurement time (Datasheet appendix B)
        measurement_time = 1.25 + \
            (2.3 * osrs_t) + \
            (2.3 * osrs_p + 0.575) + \
            (2.3 * osrs_h + 0.575)

         # Wait until measurement completion
        time.sleep(measurement_time/1000)

         # Read all data
        data = self.bus.read_i2c_block_data(self.addr, self._REG_PRESS, 8)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_h = (data[6] << 8) | data[7]

         # Compensation formulas -- Datasheet 4.2.3

         # Temperature in DegC, resolution is 0.01 DegC. Output value of "5123"
        # equals 51.23 DegC.
        # t_fine carries fine temperature as global value
        var1 = ((((adc_t >> 3) - (self.dig_t1 << 1))) * (self.dig_t2)) >> 11
        var2 = (((((adc_t >> 4) - (self.dig_t1)) * ((adc_t >> 4) - (self.dig_t1))) >> 12) * (self.dig_t3)) >> 14  # noqa
        t_fine = var1 + var2
        self.t = (t_fine * 5 + 128) >> 8

         # Pressure in Pa as unsigned 32 bit integer in Q24.8 format
        # (24 integer bits and 8 fractional bits).
        # Output value of "24674867" represents:
        # 24674867/256 = 96386.2 Pa = 963.862 hPa
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.dig_p6
        var2 = var2 + ((var1 * self.dig_p5) << 17)
        var2 = var2 + ((self.dig_p4) << 35)
        var1 = ((var1 * var1 * self.dig_p3) >> 8) + ((var1 * self.dig_p2) << 12)  # noqa
        var1 = ((((1) << 47) + var1)) * (self.dig_p1) >> 33
        if var1 == 0:
            p = 0
        else:
            p = 1048576 - adc_p
            p = (((p << 31) - var2) * 3125) / var1
            var1 = ((self.dig_p9) * (p >> 13) * (p >> 13)) >> 25
            var2 = ((self.dig_p8) * p) >> 19
            p = ((p + var1 + var2) >> 8) + ((self.dig_p7) << 4)
        self.p = p

         # Humidity in %RH as unsigned 32 bit integer in Q22.10 format
        # (22 integer and 10 fractional bits).
        # Output value of "47445" represents 47445/1024 = 46.333 %RH
        v_x1 = t_fine - 76800
        v_x1 = (((((adc_h << 14) - (self.dig_h4 << 20) - (self.dig_h5 * v_x1)) + 16384) >> 15) *  # noqa
            (((((((v_x1 * self.dig_h6) >> 10) * (((v_x1 * self.dig_h3) >> 11) + 32768)) >> 10) + 2097152) * self.dig_h2 + 8192) >> 14))  # noqa
        v_x1 = v_x1 - (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * (self.dig_h1)) >> 4)  # noqa
        if v_x1 < 0:
            v_x1 = 0
        elif v_x1 > 419430400:
            v_x1 = 419430400
        v_x1 = v_x1 >> 12
        self.v_x1 = v_x1

     def get_temperature(self):
        """Returns temperature in DegC as float"""
        return self.t / 100.0

     def get_pressure(self):
        """Returns pressure in hPa as float"""
        return self.p / 256.0 / 100.0

     def get_humidity(self):
        """Returns %RH as percentage as float"""
        return self.v_x1 / 1024.0

     @staticmethod
    def _get_int16(data, index):
        """Returns two bytes from data as a signed 16-bit value"""
        short = (data[index+1] << 8) + data[index]
        return (short & 0x7fff) - (short & 0x8000)

     @staticmethod
    def _get_uint16(data, index):
        """Returns two bytes from data as an unsigned 16-bit value"""
        short = (data[index+1] << 8) + data[index]
        return short

     @staticmethod
    def _get_int8(data, index):
        """Returns one byte from data as a signed byte"""
        byte = data[index]
        return (byte & 0x7f) - (byte & 0x80)

     @staticmethod
    def _get_uint8(data, index):
        """Returns one byte from data as an unsigned byte"""
        byte = data[index]
        return byte & 0x7f


 def main():
    bme280 = BME280()
    print("Chip id: {0}".format(bme280.get_id()))

     bme280.read_data()
    print("Temperature: {0:.2f}°C ".format(bme280.get_temperature()))
    print("Pressure: {0:.2f}hPa".format(bme280.get_pressure()))
    print("Humidity: {0:.2f}%".format(bme280.get_humidity()))


 if __name__ == "__main__":
    main()