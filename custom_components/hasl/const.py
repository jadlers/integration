""" SL Platform Constants """
from homeassistant.const import (
    CONF_NAME,
    STATE_ON,
    STATE_OFF
)

DOMAIN = "hasl"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "3.0.0"

SENSOR_STANDARD = 'Departures'
SENSOR_STATUS = 'Traffic Status'
SENSOR_VEHICLE_LOCATION = 'Vehicle Locations'
SENSOR_DEVIATION = 'Deviations'

CONF_RI4_KEY = 'ri4key'
CONF_SI2_KEY = 'si2key'
CONF_TL2_KEY = 'tl2key'
CONF_SITE_ID = 'siteid'
CONF_DEBUG = 'debug'
CONF_FP_PT = 'fppt'
CONF_FP_RB = 'fprb'
CONF_FP_TVB = 'fptvb'
CONF_FP_SB = 'fpsb'
CONF_FP_LB = 'fplb'
CONF_FP_SPVC = 'fpspvc'
CONF_FP_TB1 = 'fptb1'
CONF_FP_TB2 = 'fptb2'
CONF_FP_TB3 = 'fptb3'
CONF_SENSOR = 'sensor'
CONF_SENSOR_PROPERTY = 'property'
CONF_LINES = 'lines'
CONF_ENABLED = 'enabled'
CONF_DIRECTION = 'direction'
CONF_DIRECTION_ANY=0
CONF_DIRECTION_LEFT=1
CONF_DIRECTION_RIGHT=2
CONF_TIMEWINDOW='timewindow'
CONF_SCAN_INTERVAL='scan_interval'
CONF_SENSOR_PROPERTY_MIN = 'min'
CONF_SENSOR_PROPERTY_TIME = 'time'
CONF_SENSOR_PROPERTY_DEVIATIONS = 'deviations'
CONF_SENSOR_PROPERTY_UPDATED = 'updated'
CONF_INTEGRATION_TYPE = 'type'
CONF_INTEGRATION_ID = 'id'
CONF_DEVIATION_LINE = 'line'
CONF_DEVIATION_STOP = 'stop'
CONF_DEVIATION_LINES = 'lines'
CONF_DEVIATION_STOPS = 'stops'

CONF_DIRECTION_LIST = [CONF_DIRECTION_ANY,CONF_DIRECTION_LEFT,CONF_DIRECTION_RIGHT]
CONF_SENSOR_PROPERTY_LIST = [CONF_SENSOR_PROPERTY_MIN,CONF_SENSOR_PROPERTY_TIME,CONF_SENSOR_PROPERTY_DEVIATIONS,CONF_SENSOR_PROPERTY_UPDATED]
CONF_INTEGRATION_LIST = [SENSOR_STANDARD,SENSOR_STATUS,SENSOR_VEHICLE_LOCATION,SENSOR_DEVIATION]

DEFAULT_DIRECTION = CONF_DIRECTION_ANY
DEFAULT_SENSOR_PROPERTY = CONF_SENSOR_PROPERTY_MIN
DEFAULT_INTEGRATION_TYPE = SENSOR_STANDARD
DEFAULT_SCAN_INTERVAL=5
DEFAULT_TIMEWINDOW=60

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
HASL (Home Assistant SL Sensor) v{VERSION}

This is a custom integration, issues are logged here:
https://github.com/hasl-platform/hasl-sensor/issues
-------------------------------------------------------------------
"""