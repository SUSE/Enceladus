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
import inspect
import os

test_path = os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe())))
code_path = os.path.abspath('%s/../../lib' % test_path)
data_path = os.path.abspath('%s/../data' % test_path)
ref_result_path = os.path.abspath('%s/../reference' % test_path)

test_tmp_dir = '/tmp/serviceAccess/'


# ======================================================================
def copy_to_testdir(file_name):
    """Copy the given file to the test temporary directory"""

    os.system('cp %s %s' % (file_name, test_tmp_dir))


# ======================================================================
def get_code_path():
    """The path to the source in the development tree"""

    return code_path


# ======================================================================
def get_data_path():
    """The path to the unit test data"""

    return data_path


# ======================================================================
def get_reference_result_path():
    """Return the path to the directory containing reference results"""

    return ref_result_path


# ======================================================================
def get_test_tmpdir():
    """The location of the temporary test directory"""

    return test_tmp_dir


# ======================================================================
def get_config(config_file_name):
    """Expected to always succeed, if it fails it is most likely a data
       problem"""

    config = ConfigParser.RawConfigParser()
    config.read(config_file_name)

    return config


# ======================================================================
def create_test_tmpdir():
    """Create a temporay directory on the file system for testing"""

    remove_test_tmpdir()
    os.system('mkdir -p %s' % test_tmp_dir)


# ======================================================================
def remove_test_tmpdir():
    """Remove the temporary test directory on the file system"""

    os.system('rm -rf %s' % test_tmp_dir)
