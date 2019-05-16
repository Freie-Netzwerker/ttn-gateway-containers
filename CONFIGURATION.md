# Environment Variables
## gateway Required global variables
* GW_ID required
* GW_KEY required
  * This gateway ID and gateway Key for TTN will be used to fetch the gateway's information form the TTN console. When SERVER_TTN is true, this will also be used to conenct and forward packets to TTN.

## gateway Optional global variables
* GW_EUI - by default an EUI will be generated from the Raspberry Pi's ethernet MAC address.
  * The unique identifier for this gateway. It is used in LoRaWAN networks to identify where the packet was received and to address where a downlink packet needs to be sent from.
* GW_CONTACT_EMAIL - default an empty string
  * The gateway owner's contact information. Will be overridden by the value from the TTN console.
* GW_DESCRIPTION optional - default an empty string
  * A description of this gateway. Will be overridden by the value from the TTN console.
* GW_RESET_PIN - default 22
  * The physical pin number on the Raspberry Pi to which the concentrator's reset is connected. See the [README](README.md) file for a description and a list of common values.
* GW_GPS optional - default False
  * If true, use the hardware GPS. 
  * If false, 
    * use either fake gps if a location was configured in the TTN console, 
    * otherwise try using fake gps with the reference location as set via environment variables, 
    * otherwise don't send coordinates. 
* GW_GPS_PORT optional - default /dev/ttyAMA0
  * The UART to which the hardware GPS is connected to.
* GW_REF_LATITUDE optional - default 0
  * The latitude to use for fake gps if the coordinates are not set in the TTN console.
* GW_REF_LONGITUDE optional - default 0
  * The longitude to use for fake gps if the coordinates are not set in the TTN console.
* GW_REF_ALTITUDE optional - default 0
  * The altitude to use for fake gps if the coordinates are not set in the TTN console.
* GW_LOGGER optional - default false
  * Write a line to the terminal whenever a packet is received. ex: `08:54:37  INFO: [stats] received packet with valid CRC from mote: 26011C51 (fcnt=7)`
* GW_FWD_CRC_ERR optional - default false
  * Forward packets with an invalid CRC.
* GW_FWD_CRC_VAL optional - default true.
  * Forward packets with a valid CRC.
* GW_DOWNSTREAM optional - default true.
  * Globally enable (or disable) transmissions for this gateway.
* GW_ANTENNA_GAIN optional - default 0.
  * Set this to the dBd gain of your antenna. The dBd value is the dBi value minus 2.15dB, ie. dBd = dBi-2.15. This is used to reduce the TX power of the concentrator to stay within the legal limits.
* FREQ_PLAN_URL optional - default `https://account.thethingsnetwork.org/api/v2/frequency-plans/EU_863_870`
  * The URL where the base configuration file and frequency plan should be downloaded from. This is overwritten by the URL given by the TTN account server when using the TTN gateway connector protocol.
* GW_SPI_SPEED optional - default 8000000.
  * The SPI bus speed in Herz to use to communicate with the concentrator.
  
## collectd Optional global variables
* GW_COLLECTD_SERVER - IP address of the collectd server

## Server variables
All server variables are optional, but when a server is enabled, it is recommended to set all variables to configure it completely.
* SERVER_TTN optional - default true
  Should the gateway connect to the TTN backend
* SERVER_TTN_DOWNLINK - default true
  Enable downlink transmissions for this server

* SERVER_1_ENABLED optional - default false
* SERVER_1_TYPE - default "semtech"
* SERVER_1_ADDRESS
* SERVER_1_PORTUP - only when using type semtech
* SERVER_1_PORTDOWN - only when using type semtech
* SERVER_1_GWID - only when using type ttn
* SERVER_1_GWKEY - only when using type ttn
* SERVER_1_DOWNLINK - default false

* SERVER_2_ENABLED optional - default false
* SERVER_2_TYPE - default "semtech"
* SERVER_2_ADDRESS
* SERVER_2_PORTUP - only when using type semtech
* SERVER_2_PORTDOWN - only when using type semtech
* SERVER_2_GWID
* SERVER_2_GWKEY
* SERVER_2_DOWNLINK - default false

* SERVER_3_ENABLED optional - default false
* SERVER_3_TYPE - default "semtech"
* SERVER_3_ADDRESS
* SERVER_3_PORTUP - only when using type semtech
* SERVER_3_PORTDOWN - only when using type semtech
* SERVER_3_GWID
* SERVER_3_GWKEY
* SERVER_3_DOWNLINK - default false

As long as `SERVER_TTN` is set to false, you can also:
* SERVER_0_ENABLED optional - default false
* SERVER_0_TYPE - default "semtech"
* SERVER_0_ADDRESS
* SERVER_0_PORTUP - only when using type semtech
* SERVER_0_PORTDOWN - only when using type semtech
* SERVER_0_GWID
* SERVER_0_GWKEY
* SERVER_0_DOWNLINK - default false

## Example for using only legacy forwarder

| Variable          | Value |
| ----------------- | ----- |
| SERVER_TTN        | false |
| SERVER_1_ADDRESS  | bridge.eu.thethings.network |
| SERVER_1_ENABLED  | true  |
| SERVER_1_PORTDOWN | 1700  |
| SERVER_1_PORTUP   | 1700  |
| FREQ_PLAN_URL     | https://account.thethingsnetwork.org/api/v2/frequency-plans/EU_863_870 |
| GW_REF_LATITUDE   | -33.1 |
| GW_REF_LONGITUDE  | 18.9  |
| GW_REF_ALTITUDE   | 190   |

## Collectd variables
When collect is enabled (by selecting the `docker-compose-collectd.yml` file), system as well as TTN gateway facts will be sent to your collectd server (typically your InfluxDB/Grafana backend).

### Required variables
* GW_COLLECTD_SERVER
  * The IP address of the collectd server.

### Optional Variables
* GW_COLLECTD_INTERVAL - default 10
  * Interval in seconds for Collectd data collection  
  Set to 60 if bandwidth is a concern.
* GW_BACKPLANE - Default "none"
  * Set to "DBRGN" if you use the [Coredump](https://github.com/dbrgn/ic880a-backplane/) backplane with sensors  
  This will enable collection of the input voltage, temperature and humidity.
* GW_TTN_FAN - default false
  * Set to "true" if you have a fan controlled by the [Coredump](https://github.com/dbrgn/ic880a-backplane/) backplane
* GW_TARGET_TEMP - default 45
  * Target temperature in °C for the fan temperature regulation.
* GW_BME280 - default false
  * Set to `true` is you have a Bosch BME280 sensor on the I2C bus of your Raspberry Pi  
  This will enable collection of the temperature, pressure and relative humidity.
* GW_BME280_SMBUS - default 1
  * Bus number for your I2C bus (Should be 1 on all recent Raspberry Pi).
* GW_BME280_ADDR - default 0x78
  * I2C address for your BME280 sensor.

## Note about boolean values

Use `true` and `false` as lower case words to enable or disable features via environment variables. Any other format will not be interpreted correctly.
