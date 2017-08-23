#!/usr/bin/env python
"""Setup module for gcemetadata"""

# Copyright (c) 2015 SUSE LLC
#
# This file is part of gcemetadata.
#
# gcemetadata is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gcemetadata is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gcemetadata.  If not, see <http://www.gnu.org/licenses/>.

import sys

try:
    import setuptools
except ImportError:
    sys.stderr.write('Python setuptools required, please install.')
    sys.exit(1)

version = open('lib/gcemetadata/VERSION').read().strip()

if __name__ == '__main__':
    setuptools.setup(
        name='gcemetadata',
        description=(
            'Command-line tool to collect GCE instance meta data'),
        url='https://github.com/SUSE/Enceladus',
        license='GPL-3.0+',
        author='SUSE',
        author_email='public-cloud-dev@susecloud.net',
        version=version,
        packages=setuptools.find_packages('lib'),
        package_data={'gcemetadata': ['VERSION']},
        package_dir={
            '': 'lib',
        },
        scripts=['gcemetadata']
    )
