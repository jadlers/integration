""" SL Platform Sensor """
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant, State
from homeassistant.util.dt import now
from .haslworker import HaslWorker as worker
from .globals import get_worker

from .slapi import (
    slapi,
    slapi_fp,
    slapi_tl2,
    slapi_ri4,
    slapi_si2,
    SLAPI_Error,
    SLAPI_API_Error,
    SLAPI_HTTP_Error
)
from .slapi.const import (
    __version__ as slapi_version
)

from .const import (
    DOMAIN,
    VERSION,
    SENSOR_STANDARD,
    SENSOR_STATUS,
    SENSOR_VEHICLE_LOCATION,
    SENSOR_DEVIATION,
    CONF_FP_PT,
    CONF_FP_RB,
    CONF_FP_TVB,
    CONF_FP_SB,
    CONF_FP_LB,
    CONF_FP_SPVC,
    CONF_FP_TB1,
    CONF_FP_TB2,
    CONF_FP_TB3,       
    CONF_TL2_KEY,
    CONF_RI4_KEY,
    CONF_SI2_KEY,
    CONF_SITE_ID,
    CONF_SENSOR,
    CONF_INTEGRATION_TYPE,
    CONF_INTEGRATION_ID,
    CONF_DEVIATION_LINES,
    CONF_DEVIATION_STOPS,
    CONF_DEVIATION_LINE,
    CONF_DEVIATION_STOP,
    STATE_OFF,
    STATE_ON
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities(await setup_hasl_sensor(hass,config))

async def async_setup_entry(hass, config_entry, async_add_devices):
    async_add_devices(await setup_hasl_sensor(hass, config_entry))

async def setup_hasl_sensor(hass,config):
    """Setup sensor platform."""
    sensors = []
    worker = get_worker()
   
    #try:

    if config.data[CONF_INTEGRATION_TYPE]==SENSOR_STANDARD:
        if CONF_RI4_KEY in config.options and CONF_SITE_ID in config.options:
            await worker.assert_ri4(config.options[CONF_RI4_KEY],config.options[CONF_SITE_ID])
            sensors.append(HASLDepartureSensor(config,stopstalle))
        await worker.process_ri4();

    if config.data[CONF_INTEGRATION_TYPE]==SENSOR_DEVIATION:
        if CONF_SI2_KEY in config.options:
            for deviationid in ','.join(set(config.options[CONF_DEVIATION_LINES].split(','))).split(','):
                await worker.assert_si2_line(config.options[CONF_SI2_KEY],deviationid)
                sensors.append(HASLDeviationSensor(hass,config,CONF_DEVIATION_LINE,deviationid))
            for deviationid in ','.join(set(config.options[CONF_DEVIATION_STOPS].split(','))).split(','):
                await worker.assert_si2_stop(config.options[CONF_SI2_KEY],deviationid)
                sensors.append(HASLDeviationSensor(hass,config,CONF_DEVIATION_STOP,deviationid))
        await worker.process_si2()
        
    if config.data[CONF_INTEGRATION_TYPE]==SENSOR_STATUS:
        if CONF_TL2_KEY in config.options:
            await worker.assert_tl2(config.options[CONF_TL2_KEY])
            sensors.append(HASLTrafficStatusSensor(hass,config))
        await worker.process_tl2()

    if config.data[CONF_INTEGRATION_TYPE]==SENSOR_VEHICLE_LOCATION:
        if CONF_FP_PT in config.options and config.options[CONF_FP_PT]:
            await worker.assert_fp("PT")
            sensors.append(HASLTrainLocationSensor(hass,config,'PT'))
        if CONF_FP_RB in config.options and config.options[CONF_FP_RB]:
            await worker.assert_fp("RB")
            sensors.append(HASLTrainLocationSensor(hass,config,'RB'))
        if CONF_FP_TVB in config.options and config.options[CONF_FP_TVB]:
            await worker.assert_fp("TVB")
            sensors.append(HASLTrainLocationSensor(hass,config,'TVB'))
        if CONF_FP_SB in config.options and config.options[CONF_FP_SB]:
            await worker.assert_fp("SB")
            sensors.append(HASLTrainLocationSensor(hass,config,'SB'))
        if CONF_FP_LB in config.options and config.options[CONF_FP_LB]:
            await worker.assert_fp("LB")
            sensors.append(HASLTrainLocationSensor(hass,config,'LB'))
        if CONF_FP_SPVC in config.options and config.options[CONF_FP_SPVC]:
            await worker.assert_fp("SpvC")
            sensors.append(HASLTrainLocationSensor(hass,config,'SpvC'))
        if CONF_FP_TB1 in config.options and config.options[CONF_FP_TB1]:
            await worker.assert_fp("TB1")
            sensors.append(HASLTrainLocationSensor(hass,config,'TB1'))
        if CONF_FP_TB2 in config.options and config.options[CONF_FP_TB2]:
            await worker.assert_fp("TB2")
            sensors.append(HASLTrainLocationSensor(hass,config,'TB2'))
        if CONF_FP_TB2 in config.options and config.options[CONF_FP_TB2]:
            await worker.assert_fp("TB3")
            sensors.append(HASLTrainLocationSensor(hass,config,'TB3'))
        await worker.process_fp();

    #except:
    #    return

    return sensors
    
class HASLDevice(Entity):
    """HASL Device class."""
    @property
    def device_info(self):
        """Return device information about HASL Device."""
        return {
            "identifiers": {(DOMAIN, f"10ba5386-5fad-49c6-8f03-c7a047cd5aa5-{self._config.data[CONF_INTEGRATION_ID]}")},
            "name": f"SL {self._config.data[CONF_INTEGRATION_TYPE]} Device",
            "manufacturer": "hasl.sorlov.com",
            "model": f"slapi-v{slapi_version}",
            "sw_version": VERSION,
        }
        
class HASLDepartureSensor(HASLDevice):
    """HASL Departure Sensor class."""

    def __init__(self, config, siteid):
        """Initialize."""
        
        unit_table = {
            'min': 'min',
            'time': '',
            'deviations': '',
            'updated': '',
        }
    
        self._name = f"SL Departure Sensor {self._stop}"
        self._config = config
        self._lines = config.options[CONF_LINES]
        self._siteid = siteid
        self._enabled_sensor = config.options[CONF_SENSOR]
        self._sensorproperty = config.options[CONF_SENSOR_PROPERTY]
        self._direction = config.options[CONF_DIRECTION]
        self._timewindow = config.options[CONF_TIMEWINDOW]
        self._nextdeparture_minutes = '0'
        self._nextdeparture_expected = '-'
        self._lastupdate = '-'
        self._unit_of_measure = unit_table.get(self._config.options[CONF_SENSOR_PROPERTY], 'min')
        self._sensordata = None
        
    async def async_update(self):
        """Update the sensor."""
        worker = get_worker()

        if worker.system.status.background_task:
            return

        self._sensordata = worker.data.ri4[self._stop]
        
        if worker.data.si2[f"stop_{self._stop}"]:
            self._sensordata["deviations"] = worker.data.si2[f"stop_{self._stop}"]["data"]
        else:
            self._sensordata["deviations"] = []
               
        self._last_updated = self._sensordata["last_updated"]
        
        return

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"sl_stop_{self._stop}_sensor_{self._config.data[CONF_INTEGRATION_ID]}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        sensorproperty = self._config.options[CONF_SENSOR_PROPERTY]

        if self._sensordata == []:
            return 'Unknown'
            
        if sensorproperty is 'min':
            next_departure = self.nextDeparture()
            if not next_departure:
                return '-'

            delta = next_departure['expected'] - datetime.datetime.now()
            expected_minutes = math.floor(delta.total_seconds() / 60)
            return expected_minutes

        # If the sensor should return the time at which next departure occurs.
        if sensorproperty is 'time':
            next_departure = self.nextDeparture()
            if not next_departure:
                return '-'

            expected = next_departure['expected'].strftime('%H:%M:%S')
            return expected

        # If the sensor should return the number of deviations.
        if sensorproperty is 'deviations':
            return len(self._sensordata["deviations"])

        if sensorproperty is 'updated':
            return self._sensordata["last_updated"]
            
        # Failsafe
        return '-'
        
    def nextDeparture(self):
        if not self._sensordata:
            return None

        now = datetime.datetime.now()
        for departure in self._sensordata["data"]:
            if departure['expected'] > now:
                return departure
        return None        

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:train"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measure

    @property
    def device_state_attributes(self):
        """ Return the sensor attributes ."""

        # Initialize the state attributes.
        val = {}

        if self._sensordata == []:
            return val

        # Format the next exptected time.
        next_departure = self.nextDeparture()
        if next_departure:
            expected_time = next_departure['expected']
            delta = expected_time - datetime.datetime.now()
            expected_minutes = math.floor(delta.total_seconds() / 60)
            expected_time = expected_time.strftime('%H:%M:%S')
        else:
            expected_time = '-'
            expected_minutes = '-'

        # Setup the unit of measure.
        if self._unit_of_measure is not '':
            val['unit_of_measurement'] = self._unit_of_measure

        # Check if sensor is currently updating or not.
        if self._enabled_sensor is not None:
            sensor_state = self._hass.states.get(self._enabled_sensor)

        if self._enabled_sensor is None or sensor_state.state is STATE_ON:
            val['refresh_enabled'] = STATE_ON
        else:
            val['refresh_enabled'] = STATE_OFF

        if self._sensordata["api_result"] == "Success":
            val['api_result'] = "Ok"
        else:
            val['api_result'] = self._sensordata["api_error"]

        # Set values of the sensor.
        val['attribution'] = self._sensordata["attribution"]
        val['departures'] = self._sensordata["data"]
        val['deviations'] = self._sensordata["deviations"]
        val['last_refresh'] = self._sensordata["last_updated"]
        val['next_departure_minutes'] = expected_minutes
        val['next_departure_time'] = expected_time
        val['deviation_count'] = len(self._sensordata["deviations"])

        return val  
        
class HASLDeviationSensor(HASLDevice):
    """HASL Deviation Sensor class."""

    def __init__(self, config, deviationtype, deviationkey):
        """Initialize."""
        self._config = config
        self._deviationkey = deviationkey
        self._deviationtype = deviationtype
        self._enabled_sensor = config.options[CONF_SENSOR]
        self._name = f"SL {self._deviationtype.capitalize()} Deviation Sensor {self._stop}"
        self._sensordata = []
        self._enabled_sensor
        
    async def async_update(self):
        """Update the sensor."""
        worker = get_worker()

        if worker.system.status.background_task:
            return

        newdata = worker.data.si2[f"{self._devationtype}_{self._deviationkey}"]
        self._sensordata = newdata
        
        return

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"sl_deviation_{self._deviationtype}_{self._deviationkey}_sensor_{self._config.data[CONF_INTEGRATION_ID]}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._sensordata == []:
            return 'Unknown'
        else:
            return len(self._sensordata["data"])

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:train"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ""

    @property
    def device_state_attributes(self):
        """ Return the sensor attributes."""
        val = {}
        
        if self._sensordata == []:
            return val        
        
        # Check if sensor is currently updating or not.
        if self._enabled_sensor is not None:
            sensor_state = self._hass.states.get(self._enabled_sensor)

        if self._enabled_sensor is None or sensor_state.state is STATE_ON:
            val['refresh_enabled'] = STATE_ON
        else:
            val['refresh_enabled'] = STATE_OFF
        
        if self._sensordata["api_result"] == "Success":
            val['api_result'] = "Ok"
        else:
            val['api_result'] = self._sensordata["api_error"]

        # Set values of the sensor.
        val['attribution'] = self._sensordata["attribution"]
        val['deviations'] = self._sensordata["data"]
        val['last_refresh'] = self._sensordata["last_updated"]
        val['deviation_count'] = len(self._sensordata["data"])
        
        return val           
        
class HASLTrainLocationSensor(HASLDevice):
    """HASL Train Location Sensor class."""

    def __init__(self, hass, config, traintype):
        """Initialize."""
        self._hass = hass
        self._config = config
        self._traintype = traintype
        self._enabled_sensor = config.options[CONF_SENSOR]
        self._name = f"SL {self._traintype} Location Sensor"
        self._sensordata = []

    async def async_update(self):
        """Update the sensor."""
        worker = get_worker()

        if worker.system.status.background_task:
            return

        self._sensordata = worker.data.fp[self._traintype]
        
        return

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"sl_fl_{self._traintype}_sensor_{self._config.data[CONF_INTEGRATION_ID]}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._sensordata == []:
            return 'Unknown'
        else:
            return len(self._sensordata["data"])

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:train"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ""

    @property
    def device_state_attributes(self):
        val = {}
        
        if self._sensordata == []:
            return val
        
        # Check if sensor is currently updating or not.
        if not self._enabled_sensor == "":
            sensor_state = self._hass.states.get(self._enabled_sensor)
            if sensor_state.state is STATE_ON:
                val['refresh_enabled'] = STATE_ON
            else:
                val['refresh_enabled'] = STATE_OFF            
        else:
            val['refresh_enabled'] = STATE_ON
               
        if self._sensordata["api_result"] == "Success":
            val['api_result'] = "Success"
        else:
            val['api_result'] = self._sensordata["api_error"]

        # Set values of the sensor.
        val['attribution'] = self._sensordata["attribution"]
        val['data'] = self._sensordata["data"]
        val['last_refresh'] = self._sensordata["last_updated"]
        val['vehicle_count'] = len(self._sensordata["data"])
        
        return val           
     

class HASLTrafficStatusSensor(HASLDevice):
    """HASL Traffic Status Sensor class."""

    def __init__(self, hass, config):
        """Initialize."""
        self._hass = hass
        self._config = config
        self._enabled_sensor = config.options[CONF_SENSOR]
        self._name = f"SL Traffic Status Sensor"
        self._sensordata = []

    async def async_update(self):
        """Update the sensor."""
        worker = get_worker()

        if worker.system.status.background_task:
            return

        self._sensordata = worker.data.tl2[self._config.options[CONF_TL2_KEY]]
        
        return

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"sl_traffic_sensor_{self._config.data[CONF_INTEGRATION_ID]}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._sensordata == []:
            return 'Unknown'
        else:
            return self._sensordata["last_updated"]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:train-car"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ""

    @property
    def device_state_attributes(self):
        val = {}
        
        if self._sensordata == []:
            return val
             
        # Check if sensor is currently updating or not.
        if self._enabled_sensor is not None:
            sensor_state = self._hass.states.get(self._enabled_sensor)

        if self._enabled_sensor is None or sensor_state.state is STATE_ON:
            val['refresh_enabled'] = STATE_ON
        else:
            val['refresh_enabled'] = STATE_OFF
        
        if self._sensordata["api_result"] == "Success":
            val['api_result'] = "Ok"
        else:
            val['api_result'] = self._sensordata["api_error"]

        # Set values of the sensor.
        val['attribution'] = self._sensordata["attribution"]
        val['data'] = self._sensordata["data"]
        val['last_refresh'] = self._sensordata["last_updated"]

        return val
        
