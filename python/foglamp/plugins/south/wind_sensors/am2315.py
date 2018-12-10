# Based on - https://github.com/adafruit/Adafruit_CircuitPython_AM2320/blob/master/adafruit_am2320.py

from pyftdi.i2c import I2cController, I2cNackError, I2cPort
import time
try:
    import struct
except ImportError:
    import ustruct as struct


#pylint: disable=bad-whitespace
# Internal constants:
AM2320_DEFAULT_ADDR = 0x5C
AM2320_CMD_READREG  = 0x03
AM2320_REG_TEMP_H   = 0x02
AM2320_REG_HUM_H    = 0x00
LENGTH              = 2

def _crc16(data):
    crc = 0xffff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


class AM2315:
   def __init__(self, i2c): 
      self.slave=self.__i2c_slave_port(i2c) 

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
      try: 
         slave = i2c.get_port(AM2320_DEFAULT_ADDR)
      except: 
         raise ValueError('Unable to get Port for %s' % AM2320_DEFAULT_ADDR)
      return slave
      
   def _wake_sensor(self): 
       """
       Wake sensor
       """
       time.sleep(0.02)
       try:
           self.slave.write(bytes([0x00]))
       except OSError: 
           pass

   def _read_register(self, reg:int=0x00, length:int=0)->int:
       """
       Read from register 
       :args: 
          reg:int - register to read from 
          length:int - legister length 
       :param:
       :return:
          result from read
       """
       self._wake_sensor()
       cmd = [reg & 0xFF, length]
       try: 
          self.slave.write_to(AM2320_CMD_READREG, bytearray(cmd))
       except: 
           pass 
       try: 
          result = self.slave.read(readlen=length+4)
       except: 
           pass

       if result[0] != 0x3 or result[1] != length:
          raise RuntimeError('I2C read failure')
       # Check CRC on all but last 2 bytes
       crc1 = struct.unpack("<H", bytes(result[-2:]))[0]
       crc2 = _crc16(result[0:-2])
       if crc1 != crc2:
          raise RuntimeError('CRC failure 0x%04X vs 0x%04X' % (crc1, crc2))

       return result[2:-2]

   def temperature(self)->float:
       """
       Get temperature
       :return: 
          temperature
       """
       temp=self._read_register(AM2320_REG_TEMP_H, 2)
       temperature=struct.unpack(">H", temp)[0] 
       if temperature >= 32768:
          temperature = 32768 - temperature
       return temperature/10.0

   def humidity(self)->float: 
       """
       Get humidity
       :return: 
          humidity
       """
       humid=self._read_register(AM2320_REG_HUM_H, 2)
       humidity=struct.unpack(">H", humid)[0]
       return humidity/10.0


if __name__ == '__main__': 
    i2c=I2cController()
    i2c.set_retry_count(1)
    i2c.configure('ftdi://ftdi:232h:FT2BZGR5/')
    gd=AM2315(i2c)
    print('Temp: %s' % gd.temperature())
    print('Humidity: %s' % gd.humidity())

