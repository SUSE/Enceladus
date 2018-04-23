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
        closing_directive = ''
        directive = 'Allow from'
        opening_directive = ''
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
                    opening_directive = '    <RequireAny>'
                    directive = 'Require ip'
                    closing_directive = '    </RequireAny>'
                    break
            return opening_directive, directive, closing_directive

        apacheInfo = os.popen('%s -V' % apachectl).readlines()
        for ln in apacheInfo:
            if 'Server version:' in ln:
                ver = ln.split()[2].split('/')[-1]
                major, minor, release = ver.split('.')
                base_version = '%s%s' % (major, minor)
                if int(base_version) >= 24:
                    opening_directive = '    <RequireAny>'
                    directive = 'Require ip'
                    closing_directive = '    </RequireAny>'
                    break

        return opening_directive, directive, closing_directive

    # ======================================================================
    def _update_service_config(self, cidr_blocks):
        """Update the Apache configuragtion file"""

        order = '        Order allow,deny\n'
        cidr_blocks = cidr_blocks.split(',')
        allow = ''
        space = ' '
        indent = 4
        indent_mul = 2
        directive_settings = self._get_apache_ip_directive()
        opening_directive = directive_settings[0]
        ip_directive = directive_settings[1]
        closing_directive = directive_settings[2]
        if opening_directive:
            allow += opening_directive + '\n'
            indent_mul += 1
        indentation = space * indent * indent_mul
        while len(cidr_blocks) > 300:
            allow += '%s%s %s\n\n' % (indentation, ip_directive,
                                      space.join(cidr_blocks[:300]))
            del cidr_blocks[:300]

        allow += '%s%s %s\n' % (indentation, ip_directive,
                                space.join(cidr_blocks))
        if closing_directive:
            allow += closing_directive + '\n'

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
                    found_allow = None
                    # Inside the <Directory> directive
                elif found_dir_config:
                    # Replace the Order directive if it exists
                    if 'Order' in ln:
                        found_order = 1
                        if ip_directive == 'Allow from':
                            new_content += order
                    # Strip opening and closing directive from new
                    # access restriction list if they exist and are in the
                    # config file
                    elif ( ln.strip().startswith(opening_directive) ):
                        allow = allow[
                            len(opening_directive) + 1:
                            -(len(closing_directive) +1)
                        ]
                        new_content += ln
                        continue
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
                    elif '</Directory>' in ln or '</RequireAll>' in ln:
                        # Insert the Order directive
                        if not found_order and ip_directive == 'Allow from':
                            new_content += order
                        # Insert the Allow from directive
                        if not found_allow:
                            new_content += allow
                            found_allow = 1
                        # Add the closing tag for the directive
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
