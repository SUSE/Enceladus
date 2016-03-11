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

"""Base class for all serviceAccessConfig plugins"""

import ConfigParser
import hashlib
import logging
import os
import requests
import sys
import threading

from generatorexceptions import *


class ServiceAccessGenerator(object):
    """Base class for any plugin that implements access rules generation
       for a specific service"""

    # ======================================================================
    def __init__(self, ip_source_config_file_name):
        self.ip_source_config_file_name = ip_source_config_file_name
        self.ip_source_config_file_sha1 = None

    # ======================================================================
    def set_config_values(self, service_access_config, section_name=None):
        """Load the configuration file for the rules generator"""

        base_error_msg = 'Configuration error. %s must be specified with the '
        base_error_msg += '"%s" option in the "%s" section of the config file.'

        if not section_name:
            section_name = self.section_name
        self.service_name = section_name
        if service_access_config.has_option(section_name, 'serviceName'):
            self.service_name = service_access_config.get(
                section_name,
                'serviceName'
            )

        if not service_access_config.has_option(section_name, 'serviceConfig'):
            error_msg = base_error_msg % (
                'A configuration file to modify',
                'serviceConfig',
                section_name
            )
            logging.error(error_msg)
            raise ServiceAccessGeneratorConfigError(error_msg)

        self.service_config = service_access_config.get(
            section_name,
            'serviceConfig'
        )

        self.request = None
        if service_access_config.has_option(section_name, 'request'):
            self.request = service_access_config.get(section_name, 'request')

        if not service_access_config.has_option(
                section_name,
                'updateInterval'):
            error_msg = base_error_msg % (
                'An update interval',
                'updateInterval',
                section_name
            )
            logging.error(error_msg)
            raise ServiceAccessGeneratorConfigError(error_msg)

        self.interval = service_access_config.get(
            section_name,
            'updateInterval'
        )

        return 1

    # ======================================================================
    def update_config(self):
        """Update the Apache configuration file"""
        ctx = open(self.ip_source_config_file_name, 'r').read()
        sha1 = hashlib.sha1()
        sha1.update(ctx)
        if (
                not self.ip_source_config_file_sha1 or
                self.ip_source_config_file_sha1 != sha1.digest()
        ):
            self.ip_source_config_file_sha1 = sha1.digest()
            cidr_blocks = self._get_allowed_client_ip_addrs()
            if cidr_blocks:
                self._update_service_config(cidr_blocks)
                self._restart_service()
                if self.request:
                    try:
                        response = requests.get(self.request, verify=False)
                        if not response.status_code == 200:
                            logging.error('=' * 20)
                            logging.error(
                                'Server returned: %d' % response.status_code
                            )
                            logging.error(response.text)
                            logging.error('=' * 20)
                    except:
                        logging.error('=' * 20)
                        logging.error('No response from server')
            else:
                logging.info('No access ranges defined, nothing to do')
        # Rerun the update based on the configured time interval
        if int(self.interval) > 0:
            threading.Timer(int(self.interval), self.update_config).start()

    # ======================================================================
    def _get_allowed_client_ip_addrs(self):
        """Extract all IP Address data from the ip_source_config_file and
           collect them in a comma separated string."""
        cidr_blocks = ''

        ip_source_config = ConfigParser.RawConfigParser()
        try:
            parsed = ip_source_config.read(self.ip_source_config_file_name)
        except:
            error_msg = 'Could not parse configured source ip '
            error_msg += 'config file %s' % self.ip_source_config_file_name
            logging.error(error_msg)
            type, value, tb = sys.exc_info()
            logging.error(value.message)
            raise ServiceAccessGeneratorConfigError(error_msg)

        if not parsed:
            error_msg = 'Error parsing source ip config '
            error_msg += 'file %s' % self.ip_source_config_file_name
            logging.error(error_msg)
            raise ServiceAccessGeneratorConfigError(error_msg)

        config_sections = ip_source_config.sections()
        for section in config_sections:
            public_ips = ip_source_config.get(section, 'public-ips')
            cidr_blocks += public_ips
            cidr_blocks += ','

        cidr_blocks = cidr_blocks[:-1]  # remove trainling ,

        return cidr_blocks

    # ======================================================================
    def _restart_service(self):
        """If the configuration file gets modified the service will get
           restarted"""
        res = None
        if os.path.exists('/etc/init.d/%s' % self.service_name):
            cmd = '/etc/init.d/%s restart' % self.service_name
            res = os.system(cmd)
        else:
            cmd = 'systemctl restart %s.service' % self.service_name
            res = os.system(cmd)

        if res == 0:
            logging.info('%s restarted' % self.service_name)
        else:
            error_msg = '%s restart failed' % self.service_name
            logging.error(error_msg)
            raise ServiceAccessGeneratorServiceRestartError(error_msg)

    # ======================================================================
    def _update_service_config(self, cidr_blocks=None):
        """This is the service specific implementation as must be implemented
           in the service specific plugin"""
        error_msg = 'Reached _update_service_config in ServiceAccessGenerator'
        error_msg += ' missing implementation in plugin %s'
        logging.error(error_msg % self.__class__.__name__)
