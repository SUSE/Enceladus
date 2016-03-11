#  Copyright (C) 2016 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#  All rights reserved.
#
#  This file is part of serviceAccessConfig
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import ConfigParser
import pytest
import os
import sys

from mock import patch

# Our test utilities
import unittest_utils as utils

sys.path.insert(0, utils.get_code_path())

from serviceAccessConfig.accessrulegenerator import ServiceAccessGenerator
from serviceAccessConfig.generatorexceptions import *


# ======================================================================
def test_allowed_client_ip_addrs():
    """Test that we get the expected cidr blocks from a valid config
       file."""

    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    cidr_blocks = gen._get_allowed_client_ip_addrs()
    expected = '8.0.0.0/24,132.168.2.0/8,154.12.0.0/16,18.168.1.1/32'

    assert cidr_blocks == expected


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_allowed_client_ip_addrs_error_config(mock_logging):
    """Test that an error is generated when the config file does not
       exist, i.e. cannot be read"""

    gen = ServiceAccessGenerator(
        '%s/ip_data_syntax_error.cfg' % utils.get_data_path()
    )
    with pytest.raises(ServiceAccessGeneratorConfigError) as excinfo:
        cidr_blocks = gen._get_allowed_client_ip_addrs()

    assert mock_logging.error.called
    assert 'tests/data/ip_data_syntax_error.cfg' in str(excinfo.value)


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_allowed_client_ip_addrs_no_config(mock_logging):
    """Test that an error is generated when the config file has a syntax
       error"""

    gen = ServiceAccessGenerator('%s/foo.cfg' % utils.get_data_path())
    with pytest.raises(ServiceAccessGeneratorConfigError) as excinfo:
        cidr_blocks = gen._get_allowed_client_ip_addrs()

    assert mock_logging.error.called
    assert 'tests/data/foo.cfg' in str(excinfo.value)


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.os.path.exists',
       return_value=False)
@patch('serviceAccessConfig.accessrulegenerator.os.system',
       return_value=1)
@patch('serviceAccessConfig.accessrulegenerator.os')
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_restart_service_systemd(
        mock_logging,
        mock_os,
        mock_ossystem,
        mock_ospath):
    """Test that the proper systemd command is issued to start a service"""

    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    gen.service_name = 'foo'
    with pytest.raises(ServiceAccessGeneratorServiceRestartError) as excinfo:
        gen._restart_service()

    assert mock_logging.error.called
    mock_logging.error.assert_called_with('foo restart failed')
    mock_os.system.assert_called_with('systemctl restart foo.service')


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.os.path.exists',
       return_value=True)
@patch('serviceAccessConfig.accessrulegenerator.os.system',
       return_value=1)
@patch('serviceAccessConfig.accessrulegenerator.os')
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_restart_service_sysvinit(
        mock_logging,
        mock_os,
        mock_ossystem,
        mock_ospath):
    """Test that the proper sysV init command is issued to start a service"""

    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    gen.service_name = 'foo'
    with pytest.raises(ServiceAccessGeneratorServiceRestartError) as excinfo:
        gen._restart_service()

    assert mock_logging.error.called
    mock_logging.error.assert_called_with('foo restart failed')
    mock_os.system.assert_called_with('/etc/init.d/foo restart')


# ======================================================================
def test_set_config_values():
    """Test a properly configured setup"""

    config = utils.get_config('%s/base_config.cfg' % utils.get_data_path())
    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    result = gen.set_config_values(config, 'example')

    assert gen.service_name == 'foo'
    assert gen.service_config == '/tmp/serviceAccess/foo.cfg'
    assert gen.request == 'http://example.com/service'
    assert gen.interval == '-1'
    assert result == 1


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_set_config_values_no_interval(mock_logging):
    """Test configuration with missing 'updateInterval' option"""

    config = utils.get_config(
        '%s/base_no_interval_config.cfg' % utils.get_data_path()
    )
    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    with pytest.raises(ServiceAccessGeneratorConfigError) as excinfo:
        result = gen.set_config_values(config, 'example')

    expected_msg = 'Configuration error. An update interval '
    expected_msg += 'must be specified with the "updateInterval" option '
    expected_msg += 'in the "example" section of the config file.'

    assert mock_logging.error.called
    assert expected_msg == str(excinfo.value)


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_set_config_values_no_service_config(mock_logging):
    """Test configuration with missing 'serviceConfig' option"""

    config = utils.get_config(
        '%s/base_no_service_config.cfg' % utils.get_data_path()
    )
    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    with pytest.raises(ServiceAccessGeneratorConfigError) as excinfo:
        result = gen.set_config_values(config, 'example')

    expected_msg = 'Configuration error. A configuration file to modify '
    expected_msg += 'must be specified with the "serviceConfig" option in the '
    expected_msg += '"example" section of the config file.'

    assert mock_logging.error.called
    assert expected_msg == str(excinfo.value)


# ======================================================================
def test_set_config_values_no_service_name():
    """Test configuration with missing 'serviceName' option service and
       section name should be equal"""

    config = utils.get_config(
        '%s/base_no_service_name_config.cfg' % utils.get_data_path()
    )
    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    result = gen.set_config_values(config, 'example')

    assert gen.service_name == 'example'
    assert result == 1


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.logging')
def test_update_service_config(mock_logging):
    """Test that the base class logs an error when we reach the
       _update_service_config() method. This method must be implemented
       in the service specific plugin"""

    gen = ServiceAccessGenerator('%s/ip_data.cfg' % utils.get_data_path())
    gen._update_service_config()

    assert mock_logging.error.called
