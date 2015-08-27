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

import lib.susepubliccloudinfoclient.infoserverrequests as ifsrequest

import json
import mock
import os
import re
import sys

from mock import patch
from nose.tools import *
from StringIO import StringIO


def test_parse():
    """response from server should be parsed to a list of items"""
    expected = [
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150714',
            'id': 'ami-b97c8ffd'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp4-v20150714-pv-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150714',
            'id': 'ami-2f63906b'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp4-byos-v20150714-hvm-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150714',
            'id': 'ami-6f66952b'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp4-v20150714-hvm-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150714',
            'id': 'ami-17669553'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp4-rightscale-v20150714-pv-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150714',
            'id': 'ami-8d689bc9'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp4-rightscale-v20150714-hvm-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150714',
            'id': 'ami-d56e9d91'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp3-sapcal-v20150127-pv-mag-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150127',
            'id': 'ami-c88b928d'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-sp3-sapcal-v20150127-hvm-mag-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150127',
            'id': 'ami-a48b92e1'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-12-v20141023-pv-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20141023',
            'id': 'ami-cd5b4f88'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-12-byos-v20141023-pv-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20141023',
            'id': 'ami-99796ddc'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-12-v20141023-hvm-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20141023',
            'id': 'ami-b95b4ffc'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-12-byos-v20141023-hvm-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20141023',
            'id': 'ami-557a6e10'
        },
        {
            'deletedon': '',
            'name': 'suse-sles-11-manager-server-2-1-byos-20150408-hvm-ssd-x86_64',
            'region': 'us-west-1',
            'replacementname': '',
            'deprecatedon': '',
            'state': 'active',
            'replacementid': '',
            'publishedon': '20150420',
            'id': 'ami-01ec0145'
        }
    ]
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        server_response = fixture.read()
    parsed_result = ifsrequest.__parse_server_response_data(server_response, 'images')
    assert_equals(expected, parsed_result)


def test_reformat_to_json():
    """Spot test reconstituted json string from list of images"""
    images = [
        {
            'name': 'suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64',
            'state': 'active',
            'replacementname': '',
            'replacementid': '',
            'publishedon': '20150714',
            'deprecatedon': '',
            'region': 'us-west-1',
            'id': 'ami-b97c8ffd',
            'deletedon': ''
        }
    ]
    result = ifsrequest.__reformat(images, 'images', 'json')
    assert '{"images": [{' in result
    assert '"id": "ami-b97c8ffd"' in result
    assert '"name": "suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64"' in result


def test_reformat_to_xml():
    """Spot test reconstituted json string from list of images"""
    images = [
        {
            'name': 'suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64',
            'state': 'active',
            'replacementname': '',
            'replacementid': '',
            'publishedon': '20150714',
            'deprecatedon': '',
            'region': 'us-west-1',
            'id': 'ami-b97c8ffd',
            'deletedon': ''
        }
    ]
    result = ifsrequest.__reformat(images, 'images', 'xml')
    assert "<?xml version='1.0' encoding='UTF-8'?>" in result
    assert '<images>' in result
    assert 'id="ami-b97c8ffd"' in result
    assert 'name="suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64"' in result
