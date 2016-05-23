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
import radiotherm
import requests
import signal
import logging
from traceback import format_exc
from multiprocessing import Lock

calibration = 0
decay_factor = .1

sensor_pin = 'P9_40'

logger = logging.getLogger(__name__)

exitLock = None


def connect():
    """Connect to the thermostat.  Returns a radiotherm object"""
    try:
        tstat = radiotherm.get_thermostat()
    except IOError as e:
        if len(e.args) == 0:
            logger.critical("Unable to find the thermostat: Generic IOError."
                            " Sorry, python wouldn't tell me any more.")
        else:
            logger.critical("Unable to find the thermostat: %s (%d)",
                            e.strerror, e.errno)
        raise
    except Exception:
        logger.critical("Unable to connect to the thermostat:")
        logger.critical(format_exc())
        raise
    return tstat


def read_temp():
    """Reads temperature locally.  Returns a float"""
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_f = ((millivolts - 500) / 10 * 9/5) + 32 + calibration
    logger.debug("Read a temperature of %.2f", temp_f)
    return temp_f


def setup():
    """Performs basic setup for the daemon and ADC"""
    global exitLock
    logger.debug("Setting up ADC")
    try:
        ADC.setup()
    except RuntimeError as e:
        logger.critical(
            "Attempting to start the BBB GPIO library failed.  This can be "
            "due to a number of things, including:"
        )
        logger.critical(
            "- Too new a kernel.  Adafruit BBIO runs on 3.8.13.  Downgrades "
            "to the version this is tested with can be done easily via:")
        logger.critical(
            "  apt-get install linux-{image,headers}-3.8.13-bone79")
        logger.critical("- Not running on a BBB")
        logger.critical("- Conflicting capes")
        logger.critical("Raw exception: %s", str(e))
        return
    tstat = connect()  # TODO: retries
    logger.debug("Attaching signal handlers")
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    logger.debug("Building Lock for singal interrupts")
    exitLock = Lock()
    exitLock.acquire()
    logger.debug("Running main loop")
    return tstat


def main(tstat, read_freq=1, send_freq=30, run_once=False):
    """
    Main daemon function.

    read_freq is how long the program should wait between reads, in seconds.
    send_freq is how many read cycles should occur before data is sent.
    run_once prevents the function from looping and is used in testing.
    """
    from sys import argv
    logger.info("%s starting up!", argv[0])
    remote_url = tstat._construct_url('tstat/remote_temp')
    avgtemp = read_temp()
    reads = 1
    # acquire() returns true on succesful acquisition, which is when we
    # want to exit - acquisition means signal was recieved.
    while not exitLock.acquire(timeout=read_freq):
        # Perform the read and facotr into the average
        avgtemp = ((1 - decay_factor) * avgtemp) + \
            (decay_factor * read_temp())
        reads = (reads + 1) % send_freq
        if reads == 0:
            data = "{\"rem_temp\": %.2f }" % (avgtemp)
            logger.debug("Payload to the server is: %s", data)
            r = requests.post(remote_url, data=data)
            logger.debug("Server responded with code %d: %s",
                         r.status_code, r.text)
            if r.status_code >= 400:  # HTTP errors
                logger.warning("Server returned an HTTP error code (%d): %s",
                               r.status_code, r.text)
    data = "{\"rem_mode\": 0}"
    logger.warning("Caught exit signal, exiting.")
    logger.debug("Deactivating remote temperature with payload %s", data)
    requests.post(remote_url, data=data)
    return


def handle_exit(signum, frame):
    """
    Handles shutdown by notifying the thermostat we no longer will be sending
    remote temperature data.
    """
    logger.info("Recieved signal %d, sending exit signal", signum)
    exitLock.release()


if __name__ == "__main__":  # pragma: no cover
    tstat = setup()
    main(tstat)
