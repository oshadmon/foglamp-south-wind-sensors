# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Plugin for AM2315 temprature/humidity sensor attached using FTDI breakerboard. """

from datetime import datetime, timezone
import copy
import uuid
import logging

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions
from pyftdi.i2c import I2cController

# Code connecting to MMA8451 
from foglamp.plugins.south.wind_sensors import am2315
from foglamp.plugins.south.wind_sensors import ina219 
from foglamp.plugins.south.wind_sensors import mma8451



__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Python module name of the plugin to load',
        'type': 'string',
        'default': 'wind_sensors',
        'readonly': 'true'
    },
    'assetName': {
        'description': 'Asset name',
        'type': 'string',
        'default': "wind_sensors",
        'order': "1"
    },
    'pollInterval': {
        'description': 'The interval between poll calls to the sensor poll routine expressed in milliseconds.',
        'type': 'integer',
        'default': '1000',
        'order': '2'
    },
    'i2c_retry': {
        'description': 'I2C connection retry count', 
        'type': 'integer',
        'default': '1',
        'order': '3'
    },
    'ftdi_url': {
        'description': 'I2C URL address', 
        'type': 'string',
        'default': 'ftdi://ftdi:232h:FT2BZGR5/1',
        'order': '4'
    }

}

_LOGGER = logger.setup(__name__)
""" Setup the access to the logging system of FogLAMP """
_LOGGER.setLevel(logging.INFO)

def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'wind_sensors',
        'version': '1.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.

    Args:
        config: JSON configuration document for the plugin configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    handle = copy.deepcopy(config)

    # using wind_sensors/i2c.py 
    # handle['i2c']=i2c.I2CCommunication()

    i2c=I2cController()
    i2c.set_retry_count(int(handle['i2c_retry']['value']))
    i2c.configure(handle['ftdi_url']['value'])

    handle['am2315']=am2315.AM2315(i2c)
    handle['ina219']=ina219.INA219(i2c)
    handle['mma8451']=mma8451.MMA8451(i2c) 

    return handle


def call_am2315(handle, time_stamp)->(dict, dict): 
    """
    Get data from AM2315 
    :param: 

    :return:
       dict object of am2315 data 
    """
    try:
       temp=handle['am2315'].temperature()
    except: 
       temp={} 
    if temp != {}:    
       readings={'temperature': temp} 
       temp_wrapper = {
           'asset':     'temperature',
           'timestamp': time_stamp,
           'key':       str(uuid.uuid4()),
           'readings':  readings
       }

    try: 
       humid=handle['am2315'].humidity() 
    except: 
       humid={} 
    if humid != {}: 
       readings={'humidity': humid}
       humid_wrapper = {
           'asset':     'humidity', 
           'timestamp': time_stamp,
           'key':       str(uuid.uuid4()),
           'readings':  readings
       }
    return temp_wrapper, humid_wrapper

def call_ina219(handle, time_stamp):
    """
    Get data from INA219
    :param:
       handle: handle returned by the plugin initialisation call
       time_stamp: timestamp for given sensor
    :return:
       dict object of INA219 data
    """
    try: 
       current=handle['ina219'].current_value() 
    except: 
       current={}
    if current != {}:
       readings={'current': current} 
       wrapper = {
           'asset':     'current', 
           'timestamp': time_stamp,
           'key':       str(uuid.uuid4()),
           'readings':  readings
       }
    return wrapper

def call_mma8451(handle, time_stamp): 
    """
    Get data from MMA8451 
    :param: 
       handle: handle returned by the plugin initialisation call
       time_stamp: timestamp for given sensor 
    :return:
       dict object of mma8451 data 
    """
    try: 
       x, y, z = handle['mma8451'].get_values()
    except: 
        x=y=z={} 
    if x != {}:
       readings={'x': x, 'y': y, 'z': z} 
       wrapper = {
           'asset': 'xyz-acceleration', 
           'timestamp': time_stamp,
           'key':       str(uuid.uuid4()),
           'readings':  readings
       }
    return wrapper

def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """
    time_stamp = utils.local_timestamp()
    wrapper = list()
    temp_wrapper, humid_wrapper = call_am2315(handle, time_stamp)
    if temp_wrapper != {}: 
       wrapper.append(temp_wrapper)
    if humid_wrapper != {}:
       wrapper.append(humid_wrapper)
    current_wrapper = call_ina219(handle, time_stamp)
    if current_wrapper != {}: 
        wrapper.append(current_wrapper)
    a_wrapper = call_mma8451(handle, time_stamp)
    if a_wrapper != {}: 
        wrapper.append(a_wrapper) 

    return wrapper



def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin, it should be called when the configuration of the plugin is changed during the
        operation of the south service.
        The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for AM2315 plugin {} \n new config {}".format(handle, new_config))

    new_handle = copy.deepcopy(new_config)
    new_handle['restart'] = 'no'

    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info("AM2315 Poll plugin shutdown")
