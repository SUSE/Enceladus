#!/usr/bin/env python
"""Setup module for ec2deprecateimg"""

# Copyright (c) 2015 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of ec2deprecateimg.
# ec2deprecateimg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ec2deprecateimg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ec2deprecateimg. If not, see <http://www.gnu.org/licenses/>.

try:
    import setuptools
except ImportError:
    sys.stderr.write('Python setuptools required, please install.')
    sys.exit(1)

version = open('VERSION').read().strip()

if __name__ == '__main__':
    setuptools.setup(
        name='ec2deprecateimg',
        description=(
            'Command-line tool to deprecate EC2 images'),
        url='https://github.com/SUSE/Enceladus',
        license='GPL-3.0+',
        author='Robert Schweikert',
        author_email='rjschwei@suse.com',
        version=version,
        scripts=['ec2deprecateimg']
    )
