# Based on - https://github.com/adafruit/Adafruit_CircuitPython_MMA8451/blob/master/adafruit_mma8451.py

from pyftdi.i2c import I2cController, I2cNackError, I2cPort
try:
    import struct
except ImportError:
    import ustruct as struct


#pylint: disable=bad-whitespace
# Internal constants:
_MMA8451_DEFAULT_ADDRESS   = 0x1D
_MMA8451_REG_OUT_X_MSB     = 0x01
_MMA8451_REG_SYSMOD        = 0x0B
_MMA8451_REG_WHOAMI        = 0x0D
_MMA8451_REG_XYZ_DATA_CFG  = 0x0E
_MMA8451_REG_PL_CFG        = 0x11
_MMA8451_REG_CTRL_REG1     = 0x2A
_MMA8451_REG_CTRL_REG2     = 0x2B
_MMA8451_REG_CTRL_REG4     = 0x2D
_MMA8451_REG_CTRL_REG5     = 0x2E
_SENSORS_GRAVITY_EARTH     = 9.80665

# External user-facing constants:
PL_LRB           = 5      # Landscape, right, back
PL_LLB           = 7      # Landscape, left, back
RANGE_8G         = 0b10   # +/- 8g
RANGE_4G         = 0b01   # +/- 4g (default value)
RANGE_2G         = 0b00   # +/- 2g

class MMA8451: 
    def __init__(self, i2c): 
        self.slave=self.__configure_slave(i2c) 
        
    def __i2c_slave_port(self, i2c:I2cController=None)->I2cPort:
        """
        Get slave port 
        :args: 
            i2c:pyftdi.i2c.I2cController - I2C controller object 
        :param: 
            slave:pyftdi.i2c.I2cPort - 
        :return: 
            slave port object 
        """
        slave = i2c.get_port(_MMA8451_DEFAULT_ADDRESS)
        if slave.read_from(_MMA8451_REG_WHOAMI, 1)[0] != 0x1a:
           raise RuntimeError('Failed to find MMA8451, check wiring!')
        return slave 

    def __configure_slave(self, i2c:I2cController=None)->I2cPort:
        """
        Configure the slave
        :args: 
            slave:pyftdi.i2c.I2cPort
        """
        slave=self.__i2c_slave_port(i2c)
        slave.write_to(_MMA8451_REG_CTRL_REG2, [0x40])
        while slave.read_from(_MMA8451_REG_CTRL_REG2, 1)[0] & 0x40 > 0:
            pass
        slave.write_to(_MMA8451_REG_XYZ_DATA_CFG, [RANGE_4G])
        # High resolution mode.
        slave.write_to(_MMA8451_REG_CTRL_REG2, [0x02])
        # DRDY on INT1
        slave.write_to(_MMA8451_REG_CTRL_REG4, [0x01])
        slave.write_to(_MMA8451_REG_CTRL_REG5, [0x01])
        # Turn on orientation config
        slave.write_to(_MMA8451_REG_PL_CFG, [0x40])
        # Activate at max rate, low noise mode
        slave.write_to(_MMA8451_REG_CTRL_REG1, [0x01 | 0x04])
        return slave

    def get_values(self)->(float, float, float): 
        """
        Get sensor values
        :return:
            x;float - x-axy value 
            y:float - y-axy value 
            z:float - z-axy value 
        """
        x,y,z = struct.unpack('>hhh', self.slave.read_from(_MMA8451_REG_OUT_X_MSB, 6))
        x >>= 2
        y >>= 2
        z >>= 2

        _range = self.slave.read_from(_MMA8451_REG_XYZ_DATA_CFG,1 )[0] & 0x03
        if _range == RANGE_8G:
            x,y,z= (x/1024.0*_SENSORS_GRAVITY_EARTH,
                    y/1024.0*_SENSORS_GRAVITY_EARTH,
                    z/1024.0*_SENSORS_GRAVITY_EARTH)
        elif _range == RANGE_4G:
            x,y,z= (x/2048.0*_SENSORS_GRAVITY_EARTH,
                    y/2048.0*_SENSORS_GRAVITY_EARTH,
                    z/2048.0*_SENSORS_GRAVITY_EARTH)
        elif _range == RANGE_2G:
            x,y,z= (x/4096.0*_SENSORS_GRAVITY_EARTH,
                    y/4096.0*_SENSORS_GRAVITY_EARTH,
                    z/4096.0*_SENSORS_GRAVITY_EARTH)
        else:
            raise RuntimeError('Unexpected range!')
        return x, y, z

if __name__ == '__main__': 
    i2c=I2cController()
    i2c.set_retry_count(1)
    i2c.configure('ftdi://ftdi:232h:FT2BZGR5/')
    gd=MMA8451(i2c) 
    print(gd.get_values())
