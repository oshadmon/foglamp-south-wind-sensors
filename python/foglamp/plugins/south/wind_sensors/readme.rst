This directory contains a South plugin that implements a group of sensor data points used to monitor awind turbine. It generates one data point each second. Over the course of 60 seconds, it returns the following values, one after the another. The 61st data point begins again at the beginning.

# Example 
```
- Temperature/Humidity Sensor (am2315)
Temp: 23.3
Humidity: 41.6

- XYZ-Acceleration Sensor (mma8451)
(-1.8100164550781248, -9.404424121093749, -0.1484405029296875)

- Circuit Sensor ( ina219)
Bus Voltage:   1.762 V
Shunt Voltage: -6.000000000000001e-08 mV
Current:       -0.4 mA
```

