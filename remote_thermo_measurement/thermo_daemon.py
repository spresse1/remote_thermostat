#! /usr/bin/env python

import Adafruit_BBIO.ADC as ADC
import time
import radiotherm
import requests
import traceback
import sys
import unittest
import mock

calibration = 0
decay_factor = .1

sensor_pin = 'P9_40'


class test_Application(unittest.TestCase):
    def setUp(self):
        setup_tests()

    def test_readTemp(self):
        self.assertEqual(read_temp(), 61.88)

    def test_force(self):
        radiotherm.get_thermostat = mock.MagicMock(
            side_effect=IOError()
        )
        with self.assertRaises(IOError):
            connect()


class mock_radiotherm:
    def _construct_url(self, url_part):
        return "http://10.0.0.21/" + url_part


def setup_tests():
    ADC.read = mock.MagicMock(return_value=0.37)
    ADC.setup = mock.MagicMock()
    r = mock.Mock()
    r.text = "{ \"success\": 1}"
    requests.post = mock.MagicMock(return_value=r)
    radiotherm.get_thermostat = mock.MagicMock(return_value=mock_radiotherm())

tstat = None


def connect():
    try:
        tstat = radiotherm.get_thermostat()
    except Exception as e:
        print("Unable to connect to the thermostat:")
        traceback.print_exc()
        raise
    return tstat


def read_temp():
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_f = ((millivolts - 500) / 10 * 9/5) + 32 + calibration
    return temp_f


def main(secs=30, run_once=False):
    ADC.setup()
    tstat = connect()
    remote_url = tstat._construct_url('tstat/remote_temp')
    avgtemp = read_temp()
    while True:
        i = 0
        while i < secs:
            avgtemp = ((1 - decay_factor) * avgtemp) + \
                (decay_factor * read_temp())
            i = i+1
            time.sleep(1)
        data = "{\"rem_temp\": %02f }" % (avgtemp)
        print(data)
        r = requests.post(remote_url, data=data)
        print(r.text)
        if run_once:
            exit(0)

if __name__ == "__main__":
    from sys import argv
    run_once = False
    secs = 30
    if sys.argv[1] == "testing":
        run_once = True
        secs = 1
        setup_tests()
    main(secs, run_once)
