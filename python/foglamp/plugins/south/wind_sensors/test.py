from pyftdi.i2c import I2cController
from am2315 import AM2315
from ina219 import INA219
from mma8451 import MMA8451


i2c=I2cController()
i2c.set_retry_count(1)
i2c.configure('ftdi://ftdi:232h:FT2BZGR5/1')


am2315=AM2315(i2c)
ina219=INA219(i2c)
mma8451=MMA8451(i2c)


while True:
    print(am2315.temperature())
    print(am2315.humidity())

    print("Bus Voltage:   {} V".format(ina219.bus_voltage()))
    print("Shunt Voltage: {} mV".format(ina219.shunt_voltage() / 1000))
    print("Current:       {} mA".format(ina219.current_value()))
    
    print(mma8451.get_values())

