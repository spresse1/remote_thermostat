#! /usr/bin/env python

import Adafruit_BBIO.ADC as ADC
import time
import radiotherm
import requests
import traceback
import sys
import unittest
import mock

"""
This is a daemon for "moving" where the thermostat measures temperature.  This
is useful if you're like me and spend most of your time in a different room.
Especially if it also happens to include a gming desktop running full tilt!

Based heavily on
https://learn.adafruit.com/measuring-temperature-with-a-beaglebone-black?\
view=all
"""

calibration = 0
decay_factor = .1

sensor_pin = 'P9_40'


class test_Application(unittest.TestCase):
    """
    A series of simple tests to validate that this deamon works as intended.
    """
    def setUp(self):
        """Generic test setup. Just calls out to a generic setup function"""
        setup_tests()

    def test_readTemp(self):
        """Test reading temperature from the mocked IO"""
        self.assertEqual(read_temp(), 61.88)

    def test_forceNoThermostat(self):
        """Tests the behavior if the thermostat can't be found"""
        radiotherm.get_thermostat = mock.MagicMock(
            side_effect=IOError()
        )
        with self.assertRaises(IOError):
            connect()


class mock_radiotherm:
    """A mock of the radiotherm module for testing"""
    urlbase = "http://10.0.0.21/"

    def _construct_url(self, url_part):
        """Returns the "url" to the thermostat."""
        return self.urlbase + url_part


def setup_tests():
    """
    Sets up testing by mocking out many of the imported modules.
    """
    ADC.read = mock.MagicMock(return_value=0.37)
    ADC.setup = mock.MagicMock()
    r = mock.Mock()
    r.text = "{ \"success\": 1}"
    requests.post = mock.MagicMock(return_value=r)
    radiotherm.get_thermostat = mock.MagicMock(return_value=mock_radiotherm())

tstat = None


def connect():
    """Connect to the thermostat.  Returns a radiotherm object"""
    try:
        tstat = radiotherm.get_thermostat()
    except Exception:
        print("Unable to connect to the thermostat:")
        traceback.print_exc()
        raise
    return tstat


def read_temp():
    """Reads temperature locally.  Returns a float"""
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_f = ((millivolts - 500) / 10 * 9/5) + 32 + calibration
    return temp_f


def main(secs=30, run_once=False):
    """
    Main daemon function.

    secs is the number of seconds over which a running average should be kept
    and how often the temperature is reported to the thermostat.
    run_once prevents the function from looping and is used in testing.
    """
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
        if run_once:  # pragma: no cover
            exit(0)

if __name__ == "__main__":
    run_once = False
    secs = 30
    if len(sys.argv) > 1 and sys.argv[1] == "testing":  # pragma: no cover
        run_once = True
        secs = 1
        setup_tests()
    main(secs, run_once)
