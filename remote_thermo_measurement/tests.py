#! /usr/bin/env python

import mock
import unittest
import thermo_daemon
from mock import patch


class test_Application(unittest.TestCase):
    """
    A series of simple tests to validate that this deamon works as intended.
    """

    def setUp(self):
        """Generic test setup. Just calls out to a generic setup function"""
        r = mock.Mock()
        r.text = "{ \"success\": 1}"
        thermo_daemon.requests.post = mock.MagicMock(return_value=r)
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            return_value=mock_radiotherm())

    @patch("thermo_daemon.ADC.read")
    def test_readTemp(self, read):
        """Test reading temperature from the mocked IO"""
        read.return_value = 0.37
        self.assertEqual(thermo_daemon.read_temp(), 61.88)

    def test_forceNoThermostat(self):
        """Tests the behavior if the thermostat can't be found"""
        thermo_daemon.radiotherm.get_thermostat = mock.MagicMock(
            side_effect=IOError()
        )
        with self.assertRaises(IOError):
            thermo_daemon.connect()


class mock_radiotherm:
    """A mock of the radiotherm module for testing"""
    urlbase = "http://10.0.0.21/"

    def _construct_url(self, url_part):
        """Returns the "url" to the thermostat."""
        return self.urlbase + url_part


if __name__ == "__main__":
    unittest.main()
