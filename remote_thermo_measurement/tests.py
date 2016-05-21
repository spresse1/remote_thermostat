#! /usr/bin/env python

"""
Tests for the thermo_daemon.py daemon.
"""

import mock
import unittest
import thermo_daemon
from mock import patch
from mock import call
from mock import MagicMock


class mock_radiotherm:
    """A mock of the radiotherm module for testing"""
    urlbase = "http://10.0.0.21/"

    def _construct_url(self, url_part):
        """Returns the "url" to the thermostat."""
        return self.urlbase + url_part


class test_Application(unittest.TestCase):
    """
    A series of simple tests to validate that this deamon works as intended.
    """

    def setUp(self):
        """Generic test setup. Just calls out to a generic setup function"""
        r = mock.Mock()
        r.text = "{ \"success\": 0 }"
        thermo_daemon.requests.post = mock.MagicMock(return_value=r)
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            return_value=mock_radiotherm())
        p_read = patch('thermo_daemon.ADC.read')
        self.read = p_read.start()
        self.read.return_value = 0.37
        p_setup = patch('thermo_daemon.ADC.setup')
        self.setup = p_setup.start()
        p_logging = patch('thermo_daemon.logging')
        self.logging = p_logging.start()

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

    def test_exitOnSIGTERM(self):
        """Tests that the handler for SIGTERM functions correctly."""
        # TODO - this maybe needs a version where the signal is actually sent?
        # would require rewriting portions of main - signal handlers can only
        # be installed in the main thread.
        from signal import SIGTERM
        thermo_daemon.main(1, True)
        #  We don't really care what main did, reset
        #  the mock and continue
        self.logging.reset_mock()
        thermo_daemon.handle_exit(SIGTERM, None)
        thermo_daemon.requests.post.assert_called_with(
            "http://10.0.0.21/tstat/remote_temp",
            data="{\"rem_mode\": 0}"
        )
        self.logging.info.assert_called_once_with(
            "Recieved signal %d, sending exit signal",
            SIGTERM
        )

    @patch("signal.signal")
    def test_main(self, signal):
        """Tests the main function.  Forks off a new thread, then uses the
        signal handler to kill it.
        """
        from sys import argv
        thermo_daemon.main(3, True)
        self.setup.assert_called()
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
        from signal import SIGTERM
        signal.assert_called_with(SIGTERM, thermo_daemon.handle_exit)
        self.logging.info.assert_called_with("%s starting up!", argv[0])
        self.logging.warning.assert_called_with("Caught exit signal, exiting.")
        self.logging.debug.assert_has_calls([
            call('Read a temperature of %.2f', 61.88),
            call("Payload to the server is: %s", '{"rem_temp": 61.88 }'),
            call("Server responded: %s", '{ "success": 0 }'),
            call(
                "Deactivating remote temperature with payload %s",
                '{"rem_mode": 0}'
            ),
        ])

if __name__ == "__main__":
    unittest.main()
