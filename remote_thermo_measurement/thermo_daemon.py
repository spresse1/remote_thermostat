#! /usr/bin/env python

import Adafruit_BBIO.ADC as ADC
import time
import radiotherm, requests
import traceback
import sys

calibration=0
decay_factor=.1

sensor_pin = 'P9_40'

ADC.setup()

try:
  tstat = radiotherm.get_thermostat()
except Exception as e:
  print("Unable to connect to the thermostat:")
  traceback.print_exc()
  exit(1)

remote_url = tstat._construct_url('tstat/remote_temp')

def read_temp():
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_f = ((millivolts - 500) / 10 * 9/5) + 32 + calibration
    #print('mv=%d F=%f' % (millivolts, temp_f))
    return temp_f

avgtemp=read_temp()
while True:
    i=0
    while i<30:
        avgtemp = (( 1- decay_factor ) * avgtemp) + ( decay_factor * read_temp())
        #print avgtemp
        i=i+1
        time.sleep(1)
    data = "{\"rem_temp\": %02f }" % (avgtemp)
    print(data)
    r = requests.post(remote_url, data=data)
    print(r.text)
