#! /usr/bin/env python3

import Adafruit_BBIO.ADC as ADC
import time
import radiotherm, requests

sensor_pin = 'P9_40'

ADC.setup()
tstat = radiotherm.get_thermostat()

remote_url = tstat._construct_url('tstat/remote_temp')

while True:
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_c = (millivolts - 500) / 10
    temp_f = (temp_c * 9/5) + 32
    print('mv=%d C=%d F=%d' % (millivolts, temp_c, temp_f))
    data = "{\"rem_temp\": %d }" % (temp_f)
    r = requests.post(remote_url, data=data)
    print(r.text)
    time.sleep(30)
