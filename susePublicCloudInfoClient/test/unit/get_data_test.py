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


def test_warn_includes_warning():
    """The point of warn is to say so"""

    out = StringIO()
    ifsrequest.__warn("test", out)
    assert('Warning:' in out.getvalue())


def test_valid_keys_from_filter():
    """Find all valid attributes in the `filter` flag"""
    # image attributes
    filter_arg = (
        'id=foo,replacementid=foo,'
        'name~foo,replacementname~foo,'
        'publishedon=20150101,deprecatedon=20150101,deletedon=20150101'
    )
    filters = ifsrequest.__parse_filter(filter_arg)
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
    # server attributes
    filter_arg = 'name~foo,ip=54.197.240.216'
    filters = ifsrequest.__parse_filter(filter_arg)
    expected = ['name', 'ip']
    assert_equals(expected.sort(), [item['attr'] for item in filters].sort())


@patch('lib.susepubliccloudinfoclient.infoserverrequests.__warn')
def test_invalid_filters_raise_warning(mock_out):
    """User should be warned that invalid filter phrases will be ignored"""
    filter_arg = "foo=bar"
    ifsrequest.__parse_filter(filter_arg)
    ifsrequest.__warn.assert_called_once_with(
        "Invalid filter phrase '%s' will be ignored." % filter_arg
    )


def test_parse():
    """response from server in xml or json should be parsed to the same dictionary"""
    expected = {'images': [
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
    ]}
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        server_response = fixture.read()
    parsed_result = ifsrequest.__parse_response(server_response, 'json')
    assert_equals(expected, parsed_result)

    with open('../data/v1_amazon_us-west-1_images_active.xml', 'r') as fixture:
        server_response = fixture.read()
    parsed_result = ifsrequest.__parse_response(server_response, 'xml')
    assert_equals(expected, parsed_result)


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


def test_filter_instr():
    """should only return results with substring match in attribute"""
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        images = json.load(fixture)['images']
    filtered_result = ifsrequest.__filter_instr(
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
    filters = ifsrequest.__parse_filter('id=ami-b97c8ffd')
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
    filters = ifsrequest.__parse_filter('name~11-sp4-byos')
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
    filters = ifsrequest.__parse_filter('publishedon=20150420')
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
    filters = ifsrequest.__parse_filter('publishedon<20141024')
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
    filters = ifsrequest.__parse_filter('publishedon>20150713')
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


@patch('lib.susepubliccloudinfoclient.infoserverrequests.__get_data')
def test_get_and_filter_data(mock_get_data):
    """Given a url and a filter arg, return a filtered dict"""
    url = "https://foo.de.bar"
    with open('../data/v1_amazon_us-west-1_images_active.json', 'r') as fixture:
        mock_get_data.return_value = fixture.read()
    expected = {'images': [
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
    ]}
    filtered_result = ifsrequest.__get_and_filter_data(url, 'id=ami-b97c8ffd')
    mock_get_data.assert_called_once_with(url)
    assert_equals(expected, filtered_result)


def test_reformat_to_json():
    """Spot test reconstituted json string from result_set dict"""
    result_set = {'images': [
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
    ]}
    result = ifsrequest.__reformat(result_set, 'json')
    assert '{"images": [{' in result
    assert '"id": "ami-b97c8ffd"' in result
    assert '"name": "suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64"' in result


def test_reformat_to_xml():
    """Spot test reconstituted json string from result_set dict"""
    result_set = {'images': [
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
    ]}
    result = ifsrequest.__reformat(result_set, 'xml')
    assert "<?xml version='1.0' encoding='UTF-8'?>" in result
    assert '<images>' in result
    assert 'id="ami-b97c8ffd"' in result
    assert 'name="suse-sles-11-sp4-byos-v20150714-pv-ssd-x86_64"' in result
