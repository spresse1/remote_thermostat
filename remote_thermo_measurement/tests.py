#! /usr/bin/env python

"""
Tests for the thermo_daemon.py daemon.
"""

import mock
import unittest
import thermo_daemon
from mock import patch
from mock import call
from multiprocessing import Lock

BBIO_SETUP_ERROR = """Unable to setup ADC system. Possible causes are:
  - A cape with a conflicting pin mapping is loaded
  - A device tree object is loaded that uses the same name for a fragment: \
helper"""


class mock_radiotherm:
    """A mock of the radiotherm module for testing"""
    urlbase = "http://10.0.0.21/"

    def _construct_url(self, url_part):
        """Returns the "url" to the thermostat."""
        return self.urlbase + url_part


def main_signal(time=5):
    """Sends SIGTERM to the process, which should cause the main thread to
    exit."""
    import os
    from time import sleep
    import signal
    sleep(time)
    os.kill(os.getpid(), signal.SIGTERM)
    return


class test_Application(unittest.TestCase):
    """
    A series of simple tests to validate that this deamon works as intended.
    """

    def setUp(self):
        """Generic test setup. Just calls out to a generic setup function"""
        r = mock.Mock()
        r.text = "{ \"success\": 0 }"
        r.status_code = 200
        thermo_daemon.requests.post = mock.MagicMock(return_value=r)
        self.tstat = mock_radiotherm()
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            return_value=mock_radiotherm())
        p_read = patch('thermo_daemon.ADC.read')
        self.read = p_read.start()
        self.read.return_value = 0.37
        p_setup = patch('thermo_daemon.ADC.setup')
        self.setup = p_setup.start()
        p_logging = patch('thermo_daemon.logger')
        self.logging = p_logging.start()
        # Set up the lock as if setup had been called.
        thermo_daemon.exitLock = Lock()
        thermo_daemon.exitLock.acquire()

    def test_readTemp(self):
        """Test reading temperature from the mocked IO"""
        self.assertEqual(thermo_daemon.read_temp(), 61.88)
        self.logging.debug.assert_called_once_with(
            "Read a temperature of %.2f",
            61.88
        )

    def test_forceNoThermostatIOError(self):
        """Tests the behavior if the thermostat can't be found"""
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            side_effect=IOError(101, "Network is unreachable")
        )
        with self.assertRaises(IOError):
            thermo_daemon.connect()
        self.logging.critical.assert_called_once_with(
            "Unable to find the thermostat: %s (%d)",
            "Network is unreachable", 101
        )

    def test_forceNoThermostatIOErrorNoArgs(self):
        """Tests the behavior if the thermostat can't be found"""
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            side_effect=IOError()
        )
        with self.assertRaises(IOError):
            thermo_daemon.connect()
        self.logging.critical.assert_called_once_with(
            "Unable to find the thermostat: Generic IOError. Sorry, python"
            " wouldn't tell me any more."
        )

    def test_forceNoThermostatException(self):
        """Tests the behavior if the thermostat can't be found"""
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            side_effect=Exception()
        )
        with self.assertRaises(Exception):
            thermo_daemon.connect()
        self.logging.critical.assert_has_calls([
            call("Unable to connect to the thermostat:")
        ])

    @patch('signal.signal')
    def test_setup(self, signal):
        """Tests that setup functions as expected under normal conditions"""
        from signal import SIGTERM
        main = patch('thermo_daemon.main')
        main.start()
        thermo_daemon.setup()
        self.logging.debug.assert_has_calls([
            call("Setting up ADC"),
            call("Attaching signal handlers"),
            call('Building Lock for singal interrupts'),
            call("Running main loop"),
        ])
        self.setup.assert_called()
        signal.assert_called_with(SIGTERM, thermo_daemon.handle_exit)

    def test_setup_ADC_RuntimeException(self):
        """Tests that we properly show an error message if the adafruit BBIO
        library fails to initalize"""
        self.setup.side_effect = RuntimeError(BBIO_SETUP_ERROR)
        thermo_daemon.setup()
        self.logging.critical.assert_has_calls([
            call("Attempting to start the BBB GPIO library failed.  This can "
                 "be due to a number of things, including:"),
            call("- Too new a kernel.  Adafruit BBIO runs on 3.8.13.  "
                 "Downgrades to the version this is tested with can be done "
                 "easily via:"),
            call("  apt-get install linux-{image,headers}-3.8.13-bone79"),
            call("- Not running on a BBB"),
            call("- Conflicting capes"),
            call("Raw exception: %s", BBIO_SETUP_ERROR),
        ])

    def test_main(self):
        """Tests the main function.  Forks off a new thread, then uses the
        signal handler to kill it.
        """
        import signal
        from signal import SIGTERM
        from sys import argv
        from threading import Thread
        signal.signal(signal.SIGINT, thermo_daemon.handle_exit)
        signal.signal(signal.SIGTERM, thermo_daemon.handle_exit)
        t = Thread(target=main_signal)
        t.start()
        thermo_daemon.main(self.tstat, send_freq=2)
        self.read.assert_called()
        thermo_daemon.requests.post.assert_has_calls(
            [
                call(
                    "http://10.0.0.21/tstat/remote_temp",
                    data="{\"rem_temp\": 61.88 }"),
                call(
                    "http://10.0.0.21/tstat/remote_temp",
                    data="{\"rem_mode\": 0}"),
            ]
        )
        self.logging.info.assert_has_calls([
            call("%s starting up!", argv[0]),
            call('Recieved signal %d, sending exit signal', SIGTERM),
        ])
        self.logging.warning.assert_called_with("Caught exit signal, exiting.")
        self.logging.debug.assert_has_calls([
            call('Read a temperature of %.2f', 61.88),
            call("Payload to the server is: %s", '{"rem_temp": 61.88 }'),
            call("Server responded with code %d: %s", 200, '{ "success": 0 }'),
            call(
                "Deactivating remote temperature with payload %s",
                '{"rem_mode": 0}'
            ),
        ], any_order=True)

    def test_exitOnSIGTERM(self):
        """Tests that the handler for SIGTERM functions correctly."""
        from signal import SIGTERM
        from threading import Thread
        thermo_daemon.exitLock.release = mock.Mock()
        thermo_daemon.handle_exit(SIGTERM, None)
        thermo_daemon.exitLock.release.assert_called()

    def test_main_HTTP_400(self):
        """Test that we properly throw a warning on HTTP 400+"""
        import signal
        r = thermo_daemon.requests.post.return_value  # Mock request object
        r.text = "Not found"
        r.status_code = 400
        from threading import Thread
        signal.signal(signal.SIGINT, thermo_daemon.handle_exit)
        signal.signal(signal.SIGTERM, thermo_daemon.handle_exit)
        t = Thread(target=main_signal)
        t.start()
        thermo_daemon.main(self.tstat, send_freq=2)
        self.logging.warning.assert_any_call(
            "Server returned an HTTP error code (%d): %s",
            r.status_code, r.text
        )

if __name__ == "__main__":
    unittest.main()
