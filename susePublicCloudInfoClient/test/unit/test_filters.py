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


@patch('lib.susepubliccloudinfoclient.infoserverrequests.__warn')
def test_valid_image_keys_from_filter(mock_warn):
    """Find all valid attributes in the `filter` flag"""
    # image attributes
    filter_arg = (
        'id=foo,replacementid=foo,'
        'name~foo,replacementname~foo,'
        'publishedon=20150101,deprecatedon=20150101,deletedon=20150101'
    )
    filters = ifsrequest.__parse_command_arg_filter(filter_arg)
    expected = [
        'id',
        'replacementid',
        'name',
        'replacementname',
        'publishedon',
        'deprecatedon',
        'deletedon'

    ]
    assert_equals(expected.sort(), [item['attr'] for item in filters].sort())
    assert_false(mock_warn.called, "warn() should not be called") 


@patch('lib.susepubliccloudinfoclient.infoserverrequests.__warn')
def test_valid_server_keys_from_filter(mock_warn):
    """Find all valid attributes in the `filter` flag"""
    # server attributes
    filter_arg = 'name~foo,ip=0.0.0.0'
    filters = ifsrequest.__parse_command_arg_filter(filter_arg)
    expected = ['name', 'ip']
    assert_equals(expected.sort(), [item['attr'] for item in filters].sort())
    assert_false(mock_warn.called, "warn() should not be called") 


@patch('lib.susepubliccloudinfoclient.infoserverrequests.__warn')
def test_invalid_filters_raise_warning(mock_out):
    """User should be warned that invalid filter phrases will be ignored"""
    filter_arg = "foo=bar"
    ifsrequest.__parse_command_arg_filter(filter_arg)
    ifsrequest.__warn.assert_called_once_with(
        "Invalid filter phrase '%s' will be ignored." % filter_arg
    )


def test_filter_exact():
    """should only return results with exact matches on attribute"""
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        images = json.load(fixture)['images']
    filtered_result = ifsrequest.__filter_exact(
        images,
        'id',
        'ami-b97c8ffd'
    )
    expected = [
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
    assert_equals(expected, filtered_result)


def test_filter_substring():
    """should only return results with substring match in attribute"""
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        images = json.load(fixture)['images']
    filtered_result = ifsrequest.__filter_substring(
        images,
        'name',
        '11-sp4-byos'
    )
    expected = [
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
        },
        {
            'name': 'suse-sles-11-sp4-byos-v20150714-hvm-ssd-x86_64',
            'state': 'active',
            'replacementname': '',
            'replacementid': '',
            'publishedon': '20150714',
            'deprecatedon': '',
            'region': 'us-west-1',
            'id': 'ami-6f66952b',
            'deletedon': ''
        }
    ]
    assert_equals(expected, filtered_result)


def test_filter_less_than():
    """should only return results with attribute less than value (as int)"""
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        images = json.load(fixture)['images']
    filtered_result = ifsrequest.__filter_less_than(
        images,
        'publishedon',
        '20141024'
    )
    expected_ids = [
        "ami-cd5b4f88",
        "ami-99796ddc",
        "ami-b95b4ffc",
        "ami-557a6e10"
    ]
    assert_equals(expected_ids, [item['id'] for item in filtered_result])


def test_filter_greater_than():
    """should only return results with attribute greater than value (as int)"""
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        images = json.load(fixture)['images']
    filtered_result = ifsrequest.__filter_greater_than(
        images,
        'publishedon',
        '20150713'
    )
    expected_ids = [
        "ami-b97c8ffd",
        "ami-2f63906b",
        "ami-6f66952b",
        "ami-17669553",
        "ami-8d689bc9",
        "ami-d56e9d91"
    ]
    assert_equals(expected_ids, [item['id'] for item in filtered_result])


def test_filter_images_on_id():
    filters = ifsrequest.__parse_command_arg_filter('id=ami-b97c8ffd')
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        superset = json.load(fixture)['images']
    filtered_result = ifsrequest.__apply_filters(superset, filters)
    expected = [
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
    assert_equals(expected, filtered_result)


def test_filter_images_on_name():
    filters = ifsrequest.__parse_command_arg_filter('name~11-sp4-byos')
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        superset = json.load(fixture)['images']
    filtered_result = ifsrequest.__apply_filters(superset, filters)
    expected = [
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
        },
        {
            'name': 'suse-sles-11-sp4-byos-v20150714-hvm-ssd-x86_64',
            'state': 'active',
            'replacementname': '',
            'replacementid': '',
            'publishedon': '20150714',
            'deprecatedon': '',
            'region': 'us-west-1',
            'id': 'ami-6f66952b',
            'deletedon': ''
        }
    ]
    assert_equals(expected, filtered_result)


def test_filter_images_on_publishedon():
    filters = ifsrequest.__parse_command_arg_filter('publishedon=20150420')
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        superset = json.load(fixture)['images']
    filtered_result = ifsrequest.__apply_filters(superset, filters)
    expected = [
        {
            'name': 'suse-sles-11-manager-server-2-1-byos-20150408-hvm-ssd-x86_64',
            'state': 'active',
            'replacementname': '',
            'replacementid': '',
            'publishedon': '20150420',
            'deprecatedon': '',
            'region': 'us-west-1',
            'id': 'ami-01ec0145',
            'deletedon': ''
        }
    ]
    assert_equals(expected, filtered_result)


def test_filter_images_on_publishedon_less_than():
    filters = ifsrequest.__parse_command_arg_filter('publishedon<20141024')
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        superset = json.load(fixture)['images']
    filtered_result = ifsrequest.__apply_filters(superset, filters)
    expected_ids = [
        "ami-cd5b4f88",
        "ami-99796ddc",
        "ami-b95b4ffc",
        "ami-557a6e10"
    ]
    assert_equals(expected_ids, [item['id'] for item in filtered_result])


def test_filter_images_on_publishedon_greater_than():
    filters = ifsrequest.__parse_command_arg_filter('publishedon>20150713')
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        superset = json.load(fixture)['images']
    filtered_result = ifsrequest.__apply_filters(superset, filters)
    expected_ids = [
        "ami-b97c8ffd",
        "ami-2f63906b",
        "ami-6f66952b",
        "ami-17669553",
        "ami-8d689bc9",
        "ami-d56e9d91"
    ]
    assert_equals(expected_ids, [item['id'] for item in filtered_result])
