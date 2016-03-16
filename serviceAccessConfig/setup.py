#!/usr/bin/env python
"""Setup module for serviceAccessConfig"""

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

import sys

try:
    import setuptools
except ImportError:
    sys.stderr.write('Python setuptools required, please install.')
    sys.exit(1)

exec open('lib/serviceAccessConfig/version.py').read()

if __name__ == '__main__':
    setuptools.setup(
        name='serviceAccessConfig',
        description=(
            'Automatic generation of access control directives'),
         url='https://github.com/SUSE/Enceladus',
        license='GPL-3.0+',
        author='Robert Schweikert',
        author_email='rjschwei@suse.com',
        version=version,
        packages=setuptools.find_packages('lib'),
        package_dir={
            '': 'lib',
        },
        scripts=['usr/sbin/serviceAccessConfig']
    )
