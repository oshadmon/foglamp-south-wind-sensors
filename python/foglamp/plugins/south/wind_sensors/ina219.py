# Based on - https://github.com/adafruit/Adafruit_CircuitPython_INA219/blob/master/adafruit_ina219.py

from pyftdi.i2c import I2cController, I2cNackError, I2cPort
try:
    import struct
except ImportError:
    import ustruct as struct


#pylint: disable=bad-whitespace
# Internal constants:
_INA219_DEFAULT_ADDRESS           = 0x44

_REG_CONFIG                       = 0x00
_REG_SHUNTVOLTAGE                 = 0x01
_REG_BUSVOLTAGE                   = 0x02
_REG_POWER                        = 0x03
_REG_CURRENT                      = 0x04
_REG_CALIBRATION                  = 0x05

_CONFIG_BVOLTAGERANGE_32V         = 0x2000
_CONFIG_SADCRES_12BIT_1S_532US    = 0x0018
_CONFIG_GAIN_8_320MV              = 0x1800
_CONFIG_BADCRES_12BIT             = 0x0400
_CONFIG_MODE_SANDBVOLT_CONTINUOUS = 0x0007

"""
=== _to_signed function ===
"""
def _to_signed(num:int=0)->int:
    if num > 0x7FFF:
        num -= 0x10000
    return num

class INA219:
   def __init__(self, i2c): 
      self.slave=self.__i2c_slave_port(i2c) 
      self.i2c_addr =_INA219_DEFAULT_ADDRESS
      # Multiplier in mA used to determine current from raw reading
      self._current_lsb = 0
      # Multiplier in W used to determine power from raw reading
      self._power_lsb = 0
      # Set chip to known config values to start
      self._cal_value = 4096

      # call set_calibration_32V_2A
      self.set_calibration_32V_2A()

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
         slave = i2c.get_port(_INA219_DEFAULT_ADDRESS)
      except: 
         print('Unable to get Port for %s' %_INA219_DEFAULT_ADDRESS)
         exit(1)
      return slave 

   def _write_register(self, reg:int=0x00, value:int=0):
      """
      Write to register
      :args:
         reg:int - register to write to 
         value:int - value to write to register
      :param:
         seq:bytearray - bytearry of value 
      """
      seq = bytearray([(value >> 8) & 0xFF, value & 0xFF])
      self.slave.write_to(reg, seq)

   def _read_register(self, reg:int=0x00)->int:
       """
       Read from register 
       :args: 
          reg:int - register to read from 
       :param:
          buff : - raw result from read
       :return:
          result from read
       """
       buf = self.slave.read_from(reg, 3)
       return (buf[0] << 8) | (buf[1])

   def set_calibration_32V_2A(self): 
       """
       Configures to INA219 to be able to measure up to 32V and 2A of current. 
       Counter overflow occurs at 3.2A.
       """
       # By default we use a pretty huge range for the input voltage,
       # which probably isn't the most appropriate choice for system
       # that don't use a lot of power.  But all of the calculations
       # are shown below if you want to change the settings.  You will
       # also need to change any relevant register settings, such as
       # setting the VBUS_MAX to 16V instead of 32V, etc.

       # VBUS_MAX = 32V             (Assumes 32V, can also be set to 16V)
       # VSHUNT_MAX = 0.32          (Assumes Gain 8, 320mV, can also be 0.16, 0.08, 0.04)
       # RSHUNT = 0.1               (Resistor value in ohms)

       # 1. Determine max possible current
       # MaxPossible_I = VSHUNT_MAX / RSHUNT
       # MaxPossible_I = 3.2A

       # 2. Determine max expected current
       # MaxExpected_I = 2.0A

       # 3. Calculate possible range of LSBs (Min = 15-bit, Max = 12-bit)
       # MinimumLSB = MaxExpected_I/32767
       # MinimumLSB = 0.000061              (61uA per bit)
       # MaximumLSB = MaxExpected_I/4096
       # MaximumLSB = 0,000488              (488uA per bit)

       # 4. Choose an LSB between the min and max values
       #    (Preferrably a roundish number close to MinLSB)
       # CurrentLSB = 0.0001 (100uA per bit)
       self._current_lsb = .1  # Current LSB = 100uA per bit

       # 5. Compute the calibration register
       # Cal = trunc (0.04096 / (Current_LSB * RSHUNT))
       # Cal = 4096 (0x1000)
       self._cal_value = 4096

       # 6. Calculate the power LSB
       # PowerLSB = 20 * CurrentLSB
       # PowerLSB = 0.002 (2mW per bit)
       self._power_lsb = .002  # Power LSB = 2mW per bit

       # 7. Compute the maximum current and shunt voltage values before overflow
       #
       # Max_Current = Current_LSB * 32767
       # Max_Current = 3.2767A before overflow
       #
       # If Max_Current > Max_Possible_I then
       #    Max_Current_Before_Overflow = MaxPossible_I
       # Else
       #    Max_Current_Before_Overflow = Max_Current
       # End If
       #
       # Max_ShuntVoltage = Max_Current_Before_Overflow * RSHUNT
       # Max_ShuntVoltage = 0.32V
       #
       # If Max_ShuntVoltage >= VSHUNT_MAX
       #    Max_ShuntVoltage_Before_Overflow = VSHUNT_MAX
       # Else
       #    Max_ShuntVoltage_Before_Overflow = Max_ShuntVoltage
       # End If

       # 8. Compute the Maximum Power
       # MaximumPower = Max_Current_Before_Overflow * VBUS_MAX
       # MaximumPower = 3.2 * 32V
       # MaximumPower = 102.4W

       # Set Calibration register to 'Cal' calculated above
       self._write_register(_REG_CALIBRATION, self._cal_value)

       # Set Config register to take into account the settings above
       config = _CONFIG_BVOLTAGERANGE_32V | \
                _CONFIG_GAIN_8_320MV | \
                _CONFIG_BADCRES_12BIT | \
                _CONFIG_SADCRES_12BIT_1S_532US | \
                _CONFIG_MODE_SANDBVOLT_CONTINUOUS
       self._write_register(_REG_CONFIG, config)

   def shunt_voltage(self): 
       """
       The shunt voltage (between V+ and V-) in Volts (so +-.327V)
       :param: 
          raw_shunt_voltage:int - raw shunt voltage returnd 
          shunt_voltage_mv:int - shunt voltage 
       :return:
          shunt voltage in least signficant bit is 10uV which is 0.00001 volts
       """
       raw_shunt_voltage = self._read_register(_REG_SHUNTVOLTAGE)
       shunt_voltage_mv = _to_signed(raw_shunt_voltage)
       return shunt_voltage_mv * 0.00001

   def bus_voltage(self):
       """
       The bus voltage (between V- and GND) in Volts
       :param: 
          raw_voltage:int - raw bus voltage
          voltage_mv:int - bus voltage
       :return:
          bus voltage signficant bit is 4mV
       """
       raw_voltage=self._read_register(_REG_BUSVOLTAGE)
       voltage_mv = _to_signed(raw_voltage) 
       return voltage_mv * 0.001

   def current_value(self):
      """
      current through the shunt resistor in milliamps
      :param: 
         raw_current;int raw current
      :return:
         current in milliamps
      """
      self._write_register(_REG_CALIBRATION, self._cal_value)
      raw_current=self._read_register(_REG_CURRENT)
      raw_current=_to_signed(raw_current)
      return raw_current * self._current_lsb

if __name__ == '__main__': 
    i2c=I2cController()
    i2c.set_retry_count(1)
    i2c.configure('ftdi://ftdi:232h:FT2BZGR5/')
    gd=INA219(i2c)
    print("Bus Voltage:   {} V".format(gd.bus_voltage()))
    print("Shunt Voltage: {} mV".format(gd.shunt_voltage() / 1000))
    print("Current:       {} mA".format(gd.current_value()))
