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

from serviceAccessConfig.generatorfactory import *
from serviceAccessConfig.generatorexceptions import *


# ======================================================================
def test_factory_apache():
    """Test that we get a genarator for Apache"""

    config = utils.get_config(
        '%s/apache_setup.cfg' % utils.get_data_path()
    )
    generators = get_access_rule_generators(config)

    assert len(generators) == 1
    assert generators[0].__class__.__name__ == 'ServiceAccessGeneratorApache'


# ======================================================================
def test_factory_haproxy():
    """Test that we get a genarator for Apache"""

    config = utils.get_config(
        '%s/haproxy_setup.cfg' % utils.get_data_path()
    )
    generators = get_access_rule_generators(config)

    assert len(generators) == 1
    assert generators[0].__class__.__name__ == 'ServiceAccessGeneratorHaproxy'


# ======================================================================
@patch('serviceAccessConfig.generatorfactory.logging')
def test_factory_missing_plugin(mock_logging):
    """Test that a configured service with no equivalent plugin produces
       an error message"""

    config = utils.get_config(
        '%s/missing_ipdata_opt.cfg' % utils.get_data_path()
    )
    with pytest.raises(ServiceAccessGeneratorConfigError) as excinfo:
        generators = get_access_rule_generators(config)

    assert mock_logging.error.called


# ======================================================================
@patch('serviceAccessConfig.generatorfactory.logging')
def test_factory_missing_option(mock_logging):
    """Test that an incomplete configuration file, with the missing 'ipdata'
       option in the 'accessservice' triggers and error"""

    config = utils.get_config(
        '%s/no_service_plugin.cfg' % utils.get_data_path()
    )
    generators = get_access_rule_generators(config)

    assert mock_logging.error.called


# ======================================================================
def test_factory_multi_services():
    """Test that the factory produces generators for all configured
       services"""

    config = utils.get_config(
        '%s/multi_service_setup.cfg' % utils.get_data_path()
    )
    generators = get_access_rule_generators(config)

    assert len(generators) == 2
