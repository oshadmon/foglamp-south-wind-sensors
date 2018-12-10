import os 
import sys 
import time 

from pyftdi.i2c import I2cController
from am2315 import AM2315
from ina219 import INA219
from mma8451 import MMA8451

class I2CCommunication:
    def __init__(self): 
       """
       Inititate the i2c protocol
       :param:
          self.i2c:I2cController - I2C controller object
       """
       self.i2c=I2cController()
       self.i2c.set_retry_count(1)
       self.i2c.configure('ftdi://ftdi:232h:FT2BZGR5/1')

    def call_am2315(self)->(float, float):
        """
        Get data from AM2315 
        :param: 
           am2315:clas.AM2315 - am2315 object
        :return: 
           temperature and humidity
        """
        am2315=AM2315(self.i2c)
        try: 
           temp=am2315.temperature()
        except:
           temp=0
        try: 
           humid=am2315.humidity()
        except:
           humid=0 
        return temp, humid 

    def call_ina219(self)->float:
        """
        Get data from INA219 
        :param: 
           ina219:class.INA219 - ina219 object
        :return: 
           current
        """
        ina219=INA219(self.i2c) 
        try: 
           current=ina219.current_value()
        except:
           current=0 
        return current

    def call_mma8451(self)->(float, float, float): 
        """
        Get data from MMA8451
        :param: 
           mma8451:class.MMA8451 - mma8451 object
        :return: 
           x, y, and z values for acceleration
        """
        mma8451=MMA8451(self.i2c)
        try: 
           x, y, z=mma8451.get_values()
        except: 
           x=y=z=0
        return x, y, z 

if __name__ == '__main__':
    gd=GetData()
    print(gd.call_am2315())
    print(gd.call_ina219())
    print(gd.call_mma8451())
