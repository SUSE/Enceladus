#!/usr/bin/env python
"""Setup module for ec2publishimg"""

# Copyright (c) 2015 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of ec2publishimg.
#
# ec2publishimg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ec2publishimg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ec2publishimg. If not, see <http://www.gnu.org/licenses/>.

try:
    import setuptools
except ImportError:
    sys.stderr.write('Python setuptools required, please install.')
    sys.exit(1)

version = open('lib/ec2utils/publish_VERSION').read().strip()

if __name__ == '__main__':
    setuptools.setup(
        name='ec2publishimg',
        description=(
            'Command-line tool to publish EC2 images'),
        url='https://github.com/SUSE/Enceladus',
        license='GPL-3.0+',
        author='Robert Schweikert',
        author_email='rjschwei@suse.com',
        version=version,
        packages=setuptools.find_packages('lib'),
        package_data={'ec2utils': ['publish_VERSION']},
        package_dir={
            '': 'lib',
        },
        scripts=['ec2publishimg']
    )
