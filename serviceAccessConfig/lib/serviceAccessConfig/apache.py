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

"""serviceAccessConfig plugin for Apache"""

import ConfigParser
import glob
import logging
import os
import re

from accessrulegenerator import ServiceAccessGenerator
from generatorexceptions import *

apache_directory_directive = re.compile(r'\s*<Directory .*>')


class ServiceAccessGeneratorApache(ServiceAccessGenerator):
    """Specific access rule generator for Apache Web Server"""

    # ======================================================================
    def __init__(self, ip_source_config_file_name):
        self.section_name = 'apache'
        super(ServiceAccessGeneratorApache, self).__init__(
            ip_source_config_file_name)

    # ======================================================================
    def _get_apache_ip_directive(self):
        """Figure out the version of Apache and return the appropriate
           Apache directive for IP address filtering"""
        apachectl = None
        directive = 'Allow from'
        if os.path.exists('/usr/sbin/apache2ctl'):
            apachectl = '/usr/sbin/apache2ctl'
        else:
            apachectl = '/usr/sbin/apachectl'

        if not os.access(apachectl, os.X_OK):
            # Do some really ugly stuff
            upgradeScript = glob.glob('/usr/share/apache2/*-upgrade')
            for scr in upgradeScript:
                toVer = scr.split('-')[2]
                if int(toVer) >= 24:
                    directive = 'Require ip'
                    break
            return directive

        apacheInfo = os.popen('%s -V' % apachectl).readlines()
        for ln in apacheInfo:
            if 'Server version:' in ln:
                ver = ln.split()[2].split('/')[-1]
                major, minor, release = ver.split('.')
                base_version = '%s%s' % (major, minor)
                if int(base_version) >= 24:
                    directive = 'Require ip'
                    break

        return directive

    # ======================================================================
    def _update_service_config(self, cidr_blocks):
        """Update the Apache configuragtion file"""

        order = '        Order allow,deny\n'
        cidr_blocks = cidr_blocks.split(',')
        allow = ''
        space = ' '
        ip_directive = self._get_apache_ip_directive()
        while len(cidr_blocks) > 300:
            allow += '        %s %s\n\n' % (ip_directive,
                                            space.join(cidr_blocks[:300]))
            del cidr_blocks[:300]

        allow += '        %s %s\n' % (ip_directive, space.join(cidr_blocks))

        found_dir_config = None
        found_allow = None
        found_order = None
        for cfg in self.service_config.split(','):
            new_content = ''
            lines = open(cfg, 'r').readlines()
            for ln in lines:
                # Write the <Directory ......> directive
                if apache_directory_directive.match(ln):
                    new_content += ln
                    found_dir_config = 1
                    # Inside the <Directory> directive
                elif found_dir_config:
                    # Replace the Order directive if it exists
                    if 'Order' in ln:
                        found_order = 1
                        if ip_directive == 'Allow from':
                            new_content += order
                    # Replace the Allow from directive if it exists
                    elif (
                            ('Allow from' in ln or
                             'Require ip' in ln) and
                            not found_allow
                    ):
                        found_allow = 1
                        new_content += allow
                    # Skip other Allow directives, new one has been written
                    elif (
                            ('Allow from' in ln or
                             'Require ip' in ln) and
                            found_allow
                    ):
                        continue
                    # Recognize the end of the <Directory> directive
                    elif '</Directory>' in ln:
                        # Insert the Order directive
                        if not found_order and ip_directive == 'Allow from':
                            new_content += order
                        # Insert the Allow from directive
                        if not found_allow:
                            new_content += allow
                        # Add the closing tag for the <Directory> directive
                        new_content += ln
                    else:
                        new_content += ln
                # Write everything else
                else:
                    new_content += ln

        # Write the updated config
        fout = open(cfg, 'w')
        fout.write(new_content)
        fout.close()
        logging.info('Updated Apache config file %s' % cfg)

        return 1
