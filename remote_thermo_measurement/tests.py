#! /usr/bin/env python

"""
Tests for the thermo_daemon.py daemon.
"""

import mock
import unittest
import thermo_daemon
from mock import patch


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
        r.text = "{ \"success\": 0}"
        thermo_daemon.requests.post = mock.MagicMock(return_value=r)
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            return_value=mock_radiotherm())
        p_read = patch('thermo_daemon.ADC.read')
        self.read = p_read.start()
        self.read.return_value = 0.37
        p_setup = patch('thermo_daemon.ADC.setup')
        self.setup = p_setup.start()

    def test_readTemp(self):
        """Test reading temperature from the mocked IO"""
        self.assertEqual(thermo_daemon.read_temp(), 61.88)

    def test_forceNoThermostat(self):
        """Tests the behavior if the thermostat can't be found"""
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            side_effect=IOError()
        )
        with self.assertRaises(IOError):
            thermo_daemon.connect()

    def test_exitOnSIGTERM(self):
        """Tests that the handler for SIGTERM functions correctly."""
        thermo_daemon.main(1, True)
        thermo_daemon.handle_exit(None, None)
        thermo_daemon.requests.post.assert_called_with(
            "http://10.0.0.21/tstat/remote_temp",
            data="{\"remote_mode\": 0}"
        )

    @patch("signal.signal")
    def test_main(self, signal):
        """Tests the main function.  Forks off a new thread, then uses the
        signal handler to kill it.
        """
        thermo_daemon.main(1, True)
        self.setup.assert_called()
        self.read.assert_called()
        thermo_daemon.requests.post.assert_called_with(
            "http://10.0.0.21/tstat/remote_temp",
            data="{\"rem_temp\": 61.880000 }"
        )
        from signal import SIGTERM
        signal.assert_called_with(SIGTERM, thermo_daemon.handle_exit)

if __name__ == "__main__":
    unittest.main()
