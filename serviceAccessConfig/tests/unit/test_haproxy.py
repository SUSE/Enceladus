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
import sys

from mock import patch

# Our test utilities
import unittest_utils as utils

sys.path.insert(0, utils.get_code_path())

from serviceAccessConfig.haproxy import ServiceAccessGeneratorHaproxy
from serviceAccessConfig.generatorexceptions import *


# ======================================================================
def test_generate_acl_entry():
    """Test the generation of an acl entry"""

    gen = ServiceAccessGeneratorHaproxy(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    cidr_blocks = ['8.0.0.0/24', '132.168.2.0/8', '154.12.0.0/16']
    acl_entry = gen._generate_acl_entry('network', 10, cidr_blocks)

    expected = '    acl network10 src 8.0.0.0/24 132.168.2.0/8 '
    expected += '154.12.0.0/16\n'

    assert acl_entry == expected


# ======================================================================
def test_generate_network_name():
    """Test the generation of a network name alias"""

    gen = ServiceAccessGeneratorHaproxy(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    net_name = gen._generate_network_name('foo', 1)

    expected = 'foo1'

    assert net_name == expected


# ======================================================================
def test_update_config():
    """Test we get the expected modifications for a haproxy configuration
       file"""

    utils.create_test_tmpdir()
    utils.copy_to_testdir('%s/haproxy.cfg' % utils.get_data_path())
    config = utils.get_config('%s/haproxy_setup.cfg' % utils.get_data_path())
    gen = ServiceAccessGeneratorHaproxy(
        '%s/ip_data.cfg' % utils.get_data_path()
    )
    gen.set_config_values(config)
    with pytest.raises(ServiceAccessGeneratorServiceRestartError) as excinfo:
        gen.update_config()

    # Load the reference result data
    ref_result_file = (
        '%s/haproxy.cfg' % utils.get_reference_result_path()
    )
    ref_result = open(ref_result_file).read()

    # Load the generated result
    gen_result_file = (
        '%s//haproxy.cfg' % utils.get_test_tmpdir()
    )
    gen_result = open(gen_result_file).read()

    if ref_result == gen_result:
        # success
        utils.remove_test_tmpdir()
    else:
        msg = 'Test failed, not removing test directory '
        msg += '"%s" to aid debugging ' % utils.get_test_tmpdir()
        assert 1 == 0, msg
