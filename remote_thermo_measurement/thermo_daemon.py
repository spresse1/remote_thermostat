#! /usr/bin/env python

"""
This is a daemon for "moving" where the thermostat measures temperature.  This
is useful if you're like me and spend most of your time in a different room.
Especially if it also happens to include a gming desktop running full tilt!

Based heavily on
https://learn.adafruit.com/measuring-temperature-with-a-beaglebone-black?\
view=all
"""

import Adafruit_BBIO.ADC as ADC
import time
import radiotherm
import requests
import traceback
import sys
import signal

calibration = 0
decay_factor = .1

sensor_pin = 'P9_40'

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
    global tstat
    ADC.setup()
    tstat = connect()
    remote_url = tstat._construct_url('tstat/remote_temp')
    signal.signal(signal.SIGTERM, handle_exit)
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
            return


def handle_exit(signum, frame):
    """
    Handles shutdown by notifying the thermostat we no longer will be sending
    remote temperature data.
    """
    global tstat
    url = tstat._construct_url('tstat/remote_temp')
    data = "{\"remote_mode\": 0}"
    r = requests.post(url, data=data)
    sys.exit(0)


class mock_radiotherm:
    """A mock of the radiotherm module for testing"""
    urlbase = "http://10.0.0.21/"

    def _construct_url(self, url_part):
        """Returns the "url" to the thermostat."""
        return self.urlbase + url_part


if __name__ == "__main__":
    run_once = False
    secs = 30
    if len(sys.argv) > 1 and sys.argv[1] == "testing":  # pragma: no cover
        run_once = True
        secs = 1
        import mock
        from mock import patch
        p_read = patch('thermo_daemon.ADC.read')
        read = p_read.start()
        read.return_value = 0.37
        p_setup = patch('thermo_daemon.ADC.setup')
        read = p_setup.start()
        r = mock.Mock()
        r.text = "{ \"success\": 1}"
        requests.post = mock.MagicMock(return_value=r)
        radiotherm.get_thermostat = mock.MagicMock(
            return_value=mock_radiotherm())
    main(secs, run_once)
