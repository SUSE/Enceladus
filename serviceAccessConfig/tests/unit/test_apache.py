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
import glob
import pytest
import os
import sys

from mock import patch

# Our test utilities
import unittest_utils as utils

sys.path.insert(0, utils.get_code_path())

from serviceAccessConfig.apache import ServiceAccessGeneratorApache
from serviceAccessConfig.generatorexceptions import *


# ======================================================================
class FakeApachectlInfo(object):
    """Fake the outputof apachctl for version 2.4"""

    def __init__(self, version):
        self.version = version

    def readlines(self):
        """File object method"""

        return ['Server version: Apache/%s (Linux/SUSE)\n' % self.version,
                'Server built:   2015-11-05 13:32:23.000000000 +0000\n']


# ======================================================================
apache22 = FakeApachectlInfo('2.2.8')
apache24 = FakeApachectlInfo('2.4.16')


# ======================================================================
@patch('serviceAccessConfig.apache.os.path.exists', return_value=True)
@patch('serviceAccessConfig.apache.os.access', return_value=True)
@patch('serviceAccessConfig.apache.os.popen',
       return_value=apache22)
def test_get_apache_ip_directive_apachectl_call_22(
        mock_ospopen,
        mock_osaccess,
        mock_ospath):
    """Test we get the expected directive value for Apache 2.2
       when 'apachctl' is called"""

    config = utils.get_config('%s/apache_setup_22.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorApache(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    ip_directive = gen._get_apache_ip_directive()

    assert ip_directive == ('', 'Allow from', '')


# ======================================================================
@patch('serviceAccessConfig.apache.os.path.exists', return_value=True)
@patch('serviceAccessConfig.apache.os.access', return_value=True)
@patch('serviceAccessConfig.apache.os.popen',
       return_value=apache24)
def test_get_apache_ip_directive_apachectl_call_24(
        mock_ospopen,
        mock_osaccess,
        mock_ospath):
    """Test we get the expected directive value for Apache 2.4
       when 'apachctl' is called"""

    config = utils.get_config('%s/apache_setup_24.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorApache(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    ip_directive = gen._get_apache_ip_directive()

    assert ip_directive == (
        '    <RequireAny>',
        'Require ip',
        '    </RequireAny>'
    )


# ======================================================================
@patch('serviceAccessConfig.apache.os.path.exists', return_value=False)
@patch('serviceAccessConfig.apache.os.access', return_value=False)
@patch('serviceAccessConfig.apache.glob.glob',
       return_value=['apache-20-22-upgrade'])
def test_get_apache_ip_directive_upgrade_file_22(
        mock_glob,
        mock_osaccess,
        mock_ospath):
    """Test we get the expected directive value for Apache 2.2
       when using the upgrade file filename"""

    config = utils.get_config('%s/apache_setup_22.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorApache(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    ip_directive = gen._get_apache_ip_directive()

    assert ip_directive == ('', 'Allow from', '')


# ======================================================================
@patch('serviceAccessConfig.apache.os.path.exists', return_value=False)
@patch('serviceAccessConfig.apache.os.access', return_value=False)
@patch('serviceAccessConfig.apache.glob.glob',
       return_value=['apache-22-24-upgrade'])
def test_get_apache_ip_directive_upgrade_file_24(
        mock_glob,
        mock_osaccess,
        mock_ospath):
    """Test we get the expected directive value for Apache 2.4
       when using the upgrade file filename"""

    config = utils.get_config('%s/apache_setup_24.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorApache(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    ip_directive = gen._get_apache_ip_directive()

    assert ip_directive == (
        '    <RequireAny>',
        'Require ip',
        '    </RequireAny>'
    )


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.os.path.exists',
       return_value=False)
@patch('serviceAccessConfig.apache.os.path.exists', return_value=False)
@patch('serviceAccessConfig.apache.os.access', return_value=False)
@patch('serviceAccessConfig.apache.glob.glob',
       return_value=['apache-20-22-upgrade'])
def test_update_config_v22(
        mock_glob,
        mock_osaccess,
        mock_ospath_apache,
        mock_ospath_base):
    """Test we get the expected modifications in the config file"""

    utils.create_test_tmpdir()
    utils.copy_to_testdir('%s/apache-vhost_22.cfg' % utils.get_data_path())
    config = utils.get_config('%s/apache_setup_22.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorApache(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    with pytest.raises(ServiceAccessGeneratorServiceRestartError) as excinfo:
        gen.update_config()

    # Load the reference result data
    ref_result_file = (
        '%s/apache-vhost-22.cfg' % utils.get_reference_result_path()
    )
    ref_result = open(ref_result_file).read()

    # Load the generated result
    gen_result_file = (
        '%s/apache-vhost_22.cfg' % utils.get_test_tmpdir()
    )
    gen_result = open(gen_result_file).read()

    if ref_result == gen_result:
        # success
        utils.remove_test_tmpdir()
    else:
        msg = 'Test failed, not removing test directory '
        msg += '"%s" to aid debugging ' % utils.get_test_tmpdir()
        assert False, msg


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.os.path.exists',
       return_value=False)
@patch('serviceAccessConfig.apache.os.path.exists', return_value=False)
@patch('serviceAccessConfig.apache.os.access', return_value=False)
@patch('serviceAccessConfig.apache.glob.glob',
       return_value=['apache-22-24-upgrade'])
def test_update_config_v24(
        mock_glob,
        mock_osaccess,
        mock_ospath_apache,
        mock_ospath_base):
    """Test we get the expected modifications in the config file"""

    utils.create_test_tmpdir()
    utils.copy_to_testdir('%s/apache-vhost_24.cfg' % utils.get_data_path())
    config = utils.get_config('%s/apache_setup_24.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorApache(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    with pytest.raises(ServiceAccessGeneratorServiceRestartError) as excinfo:
        gen.update_config()

    # Load the reference result data
    ref_result_file = (
        '%s/apache-vhost-24.cfg' % utils.get_reference_result_path()
    )
    ref_result = open(ref_result_file).read()

    # Load the generated result
    gen_result_file = (
        '%s/apache-vhost_24.cfg' % utils.get_test_tmpdir()
    )
    gen_result = open(gen_result_file).read()

    if ref_result == gen_result:
        # success
        utils.remove_test_tmpdir()
    else:
        msg = 'Test failed, not removing test directory '
        msg += '"%s" to aid debugging ' % utils.get_test_tmpdir()
        assert False, msg


# ======================================================================
@patch('serviceAccessConfig.accessrulegenerator.os.path.exists',
       return_value=False)
@patch('serviceAccessConfig.apache.os.path.exists', return_value=False)
@patch('serviceAccessConfig.apache.os.access', return_value=False)
@patch('serviceAccessConfig.apache.glob.glob',
       return_value=['apache-22-24-upgrade'])
def test_update_config_v24_large_IP_set(
        mock_glob,
        mock_osaccess,
        mock_ospath_apache,
        mock_ospath_base):
    """Test we get the expected modifications in the config file"""

    utils.create_test_tmpdir()
    utils.copy_to_testdir('%s/apache-vhost_24.cfg' % utils.get_data_path())
    config = utils.get_config('%s/apache_setup_24.cfg' % utils.get_data_path())
    ip_config = utils.get_config('%s/ip_data.cfg' % utils.get_data_path())
    large_ip_set = '192.168.1.0/24,' * 400
    large_ip_set += '192.168.1.0/24'
    ip_config.set('region3', 'public-ips', large_ip_set)
    large_ip_data = open('%s/large_ip_data.cfg' % utils.get_test_tmpdir(), 'w')
    ip_config.write(large_ip_data)
    large_ip_data.close()

    gen = ServiceAccessGeneratorApache(
        '%s/large_ip_data.cfg' % utils.get_test_tmpdir()
    )
    gen.set_config_values(config)
    with pytest.raises(ServiceAccessGeneratorServiceRestartError) as excinfo:
        gen.update_config()

    # Load the reference result data
    ref_result_file = (
        '%s/apache-vhost-24-large-ip-set.cfg'
        % utils.get_reference_result_path()
    )
    ref_result = open(ref_result_file).read()

    # Load the generated result
    gen_result_file = (
        '%s/apache-vhost_24.cfg' % utils.get_test_tmpdir()
    )
    gen_result = open(gen_result_file).read()

    if ref_result == gen_result:
        # success
        utils.remove_test_tmpdir()
    else:
        msg = 'Test failed, not removing test directory '
        msg += '"%s" to aid debugging ' % utils.get_test_tmpdir()
        assert False, msg

