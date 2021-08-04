import sds011
import time

sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)
print(sensor.query())  # Gets (pm25, pm10)
sensor.sleep()  # Turn off fan and diode
while True:
    sensor.sleep(sleep=False)  # Turn on fan and diode
    time.sleep(15)  # Allow time for the sensor to measure properly
    print(sensor.query())
    sensor.sleep()
    time.sleep(15)

