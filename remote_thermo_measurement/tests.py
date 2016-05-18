#! /usr/bin/env python

"""
Tests for the thermo_daemon.py daemon.
"""

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
            return_value=thermo_daemon.mock_radiotherm())

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


if __name__ == "__main__":
    unittest.main()
