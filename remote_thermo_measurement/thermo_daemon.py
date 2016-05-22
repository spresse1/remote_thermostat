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
import signal
import logging
from traceback import format_exc

logging.basicConfig(level=logging.DEBUG)
print("Logging set up")

calibration = 0
decay_factor = .1

sensor_pin = 'P9_40'

tstat = None

main_should_exit = False


def connect():
    """Connect to the thermostat.  Returns a radiotherm object"""
    try:
        tstat = radiotherm.get_thermostat()
    except IOError as e:
        if len(e.args) == 0:
            logging.critical("Unable to find the thermostat: Generic IOError."
                             " Sorry, python wouldn't tell me any more.")
        else:
            logging.critical("Unable to find the thermostat: %s (%d)",
                             e.strerror, e.errno)
        raise
    except Exception:
        logging.critical("Unable to connect to the thermostat:")
        logging.critical(format_exc())
        raise
    return tstat


def read_temp():
    """Reads temperature locally.  Returns a float"""
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_f = ((millivolts - 500) / 10 * 9/5) + 32 + calibration
    logging.debug("Read a temperature of %.2f", temp_f)
    return temp_f


def main(read_freq=1, send_freq=30, run_once=False):
    """
    Main daemon function.

    read_freq is how long the program shoudl wait between reads, in seconds.
    send_freq is how many read cycles should occur before data is sent.
    run_once prevents the function from looping and is used in testing.
    """
    from sys import argv
    global tstat
    global main_should_exit
    main_should_exit = False
    logging.info("%s starting up!", argv[0])
    ADC.setup()  # TODO: try-catch on the RuntimeError this can throw.
    tstat = connect()
    remote_url = tstat._construct_url('tstat/remote_temp')
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    avgtemp = read_temp()
    reads = 1
    while not main_should_exit:
        # Perform the read and facotr into the average
        avgtemp = ((1 - decay_factor) * avgtemp) + \
            (decay_factor * read_temp())
        reads = (reads + 1) % send_freq
        if reads == 0:
            data = "{\"rem_temp\": %.2f }" % (avgtemp)
            logging.debug("Payload to the server is: %s", data)
            r = requests.post(remote_url, data=data)
            logging.debug("Server responded: %s", r.text)
            # TODO: actually check the response
        time.sleep(read_freq)
    data = "{\"rem_mode\": 0}"
    logging.warning("Caught exit signal, exiting.")
    logging.debug("Deactivating remote temperature with payload %s", data)
    requests.post(remote_url, data=data)


def handle_exit(signum, frame):
    """
    Handles shutdown by notifying the thermostat we no longer will be sending
    remote temperature data.
    """
    #from thread import interrupt_main
    global main_should_exit
    logging.info("Recieved signal %d, sending exit signal", signum)
    main_should_exit = True
    #interrupt_main()


if __name__ == "__main__":  # pragma: no cover
    run_once = False
    secs = 30
    main(secs, run_once)
