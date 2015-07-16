#!/usr/bin/python
#
# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of susePublicCloudInfoClient
#
# susePublicCloudInfoClient is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# susePublicCloudInfoClient is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with susePublicCloudInfoClient. If not, see
# <http://www.gnu.org/licenses/>.
#

import os
import sys

from nose.tools import *

this_path = os.path.dirname(os.path.abspath(__file__))
mod_path = this_path + os.sep + '../../lib/susepubliccloudinfoclient'
sys.path.insert(0, mod_path)

import infoserverrequests as ifsrequest

def test_api_version():
    assert_equals('v1', ifsrequest.__get_api_version())

def test_get_base_url():
    expected = 'https://susepubliccloudinfo.suse.com'
    assert_equals(expected, ifsrequest.__get_base_url())

def test_form_url_servers_all_json():
    """Form the URL for all servers in JSON format"""
    url = ifsrequest.__form_url('amazon', 'servers', 'json')
    expected = 'https://susepubliccloudinfo.suse.com/v1/amazon/servers.json'
    assert_equals(expected, url)

def test_form_url_servers_smt_xml():
    """Form the URL for all SMT servers in XML"""
    url = ifsrequest.__form_url('hp', 'servers', server_type='smt')
    expected = 'https://susepubliccloudinfo.suse.com/v1/hp/servers/smt.xml'
    assert_equals(expected, url)

def test_form_url_images_active_region_json():
    """Form the URL for active images in JSON format in a given region"""
    url = ifsrequest.__form_url(
        'amazon',
        'images',
        data_format='json',
        region='us-east-1',
        image_state='active')
    expected = 'https://susepubliccloudinfo.suse.com/v1/'
    expected += 'amazon/us-east-1/images/active.json'
    assert_equals(expected, url)

def test_form_url_images_all_xml():
    """Form URL for all images in XML format"""
    url = ifsrequest.__form_url('google', 'images')
    expected = 'https://susepubliccloudinfo.suse.com/v1/google/images.xml'
    assert_equals(expected, url)


