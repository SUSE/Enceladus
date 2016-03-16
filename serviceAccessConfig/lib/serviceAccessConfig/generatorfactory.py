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

"""Factory for access rules generators"""

import ConfigParser
import glob
import inspect
import logging
import os

from generatorexceptions import *

module_path = os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe())))


# ======================================================================
def get_access_rule_generators(access_generator_config):
    """Return a list of access rule generators for each configured &
       known service"""
    available_modules = glob.glob('%s/*.py' % module_path)
    class_base_name = 'ServiceAccessGenerator'
    generators = []
    undefined_plugins = []
    if not access_generator_config.has_option('accessservice', 'ipdata'):
        error_msg = 'A source IP data file must be specified in the '
        error_msg += 'accessservice section of the configuration file.'
        logging.error(error_msg)
        raise ServiceAccessGeneratorConfigError(error_msg)
    ip_source_config_file_name = access_generator_config.get(
        'accessservice',
        'ipdata'
    )
    for section in access_generator_config.sections():
        if section == 'accessservice':
            continue
        plugin_name = '%s.py' % section
        for module_name in available_modules:
            if plugin_name in module_name:
                class_name = (
                    class_base_name +
                    section[0].upper() +
                    section[1:]
                )
                module = __import__(
                    'serviceAccessConfig.%s' % section,
                    globals(), locals(),
                    fromlist=[class_name]
                )
                exec 'generator = module.%s("%s")' % (
                    class_name,
                    ip_source_config_file_name
                )
                try:
                    generator.set_config_values(access_generator_config)
                except ServiceAccessGeneratorConfigError as e:
                    logging.error(e.message)
                    continue
                generators.append(generator)
                break
        else:
            error_msg = 'Configuration for plugin "%s" found, ' % plugin_name
            error_msg += 'but plugin not found'
            logging.error(error_msg)

    return generators
