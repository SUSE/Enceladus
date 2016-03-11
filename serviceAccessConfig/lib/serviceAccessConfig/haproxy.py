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

"""serviceAccessConfig plugin for HAProxy"""

import ConfigParser
import logging

from accessrulegenerator import ServiceAccessGenerator
from generatorexceptions import *


class ServiceAccessGeneratorHaproxy(ServiceAccessGenerator):
    """Specific access rule generator for HAProxy"""

    # ======================================================================
    def __init__(self, ip_source_config_file_name):
        self.section_name = 'haproxy'
        super(ServiceAccessGeneratorHaproxy, self).__init__(
            ip_source_config_file_name)
        self.block_start_marker = '# Generated ACL Begin'
        self.block_end_marker = '# Generated ACL End'

    # ======================================================================
    def _generate_acl_entry(self, acl_name_prefix, counter, acl_cidr_blocs):
        """Generate a string that identifies a network name and associates
           cidr blocks with the name"""
        space = ' '
        acl_network = '    acl %s src ' % self._generate_network_name(
            acl_name_prefix,
            counter
        )
        acl_network += space.join(acl_cidr_blocs)
        acl_network += '\n'

        return acl_network

    # ======================================================================
    def _generate_network_name(self, acl_name_prefix, counter):
        """Generate a network name to be used as a reference for cidr
           blocks"""
        return '%s%d' % (acl_name_prefix, counter)

    # ======================================================================
    def _update_service_config(self, cidr_blocks):
        """Update the HAProxy configuragtion file"""

        # Generate ACL definition section
        # a prefix for the ACL names
        acl_name_prefix = 'network'
        # Counter for number of ACLs that get generated
        acl_count = 1
        # Keep track of number of IP ranges in a given ACL
        cidr_block_count = 0
        # Built list of ranges for a given ACL
        acl_cidr_blocks = []
        # Keep track off all the ACL names used
        acl_network_names = []
        cidr_blocks = cidr_blocks.split(',')
        acl_section = '%s\n' % self.block_start_marker
        for cidr_block in cidr_blocks:
            acl_cidr_blocks.append(cidr_block)
            cidr_block_count += 1
            # The number of 35 cidr_blocks per network definition is emperical
            # and has worked well
            if cidr_block_count == 35:
                acl_network_names.append(self._generate_network_name(
                    acl_name_prefix,
                    counter)
                )
                acl_section += self._generate_acl_entry(
                    acl_name_prefix,
                    acl_count,
                    acl_cidr_blocks
                )
                acl_count += 1
                cidr_block_count = 0
                acl_cidr_blocks = []

        acl_network_names.append(self._generate_network_name(
            acl_name_prefix,
            acl_count)
        )
        acl_section += self._generate_acl_entry(
            acl_name_prefix,
            acl_count,
            acl_cidr_blocks
        )
        acl_section += '    tcp-request connection accept if '
        or_operator = ' || '
        acl_section += or_operator.join(acl_network_names)
        acl_section += '\n%s\n' % self.block_end_marker

        # Update the file
        for cfg in self.service_config.split(','):
            new_content = ''
            skip = None
            lines = open(cfg, 'r').readlines()
            for ln in lines:
                if self.block_start_marker in ln:
                    new_content += acl_section
                    skip = 1
                    continue
                if self.block_end_marker in ln:
                    skip = None
                    continue
                if skip:
                    continue
                new_content += ln

            # Write the updated config
            fout = open(cfg, 'w')
            fout.write(new_content)
            fout.close()
            logging.info('Updated HAproxy config file %s' % cfg)

        return 1
