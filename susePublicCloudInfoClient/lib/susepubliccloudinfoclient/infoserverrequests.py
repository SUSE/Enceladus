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

import json
import re
import requests
import sys
import xml.etree.ElementTree as ET


def __apply_filters(superset, filters):
    # map operators to filter functions
    filter_operations = {
        '=': __filter_exact,
        '~': __filter_instr,
        '>': __filter_greater_than,
        '<': __filter_less_than
    }
    # prepopulate the result set with all the items
    result_set = superset
    # run through the filters, allowing each to reduce the result set...
    for a_filter in filters:
        result_set = filter_operations[a_filter['operator']](
            result_set,
            a_filter['attr'],
            a_filter['value']
        )    
    return result_set


def __filter_exact(items, attr, value):
    return [item for item in items if item[attr] == value]


def __filter_instr(items, attr, value):
    return [item for item in items if value in item[attr]]


def __filter_less_than(items, attr, value):
    return [item for item in items if int(item[attr]) < int(value)]


def __filter_greater_than(items, attr, value):
    return [item for item in items if int(item[attr]) > int(value)]


def __form_url(
        framework,
        info_type,
        data_format='xml',
        region=None,
        image_state=None,
        server_type=None):
    """Form the URL for the request"""
    url_components = []
    url_components.append(__get_base_url())
    url_components.append(__get_api_version())
    url_components.append(framework)
    if region:
        url_components.append(region)
    url_components.append(info_type)
    doc_type = image_state or server_type
    if doc_type:
        doc_type += '.' + data_format
        url_components.append(doc_type)
    else:
        url_components[-1] = url_components[-1] + '.' + data_format
    url = '/'
    return url.join(url_components)


def __get_api_version():
    """Return the API version to use"""
    return 'v1'


def __get_base_url():
    """Return the base url for the information service"""
    return 'https://susepubliccloudinfo.suse.com'


def __get_data(url):
    """Make the request and return the data or None in case of failure"""
    response = requests.get(url)
    return response.text


def __get_and_filter_data(url, filter_arg):
    response = __get_data(url)
    if response:
        filters = __parse_filter(filter_arg)
        result_set = __parse_response(response)
        item_type = result_set.keys()[0]
        return {item_type: __apply_filters(result_set[item_type], filters)}


def __inflect(plural):
    inflections = {'images': 'image', 'servers': 'server'}
    return inflections[plural]


def __parse_filter(arg):
    """Break down the filter arg into a usable dictionary"""
    valid_filters = {
        'id': '^(?P<attr>id)(?P<operator>[=])(?P<value>.+)$',
        'replacementid': '^(?P<attr>replacementid)(?P<operator>[=])(?P<value>.+)$',
        'name': '^(?P<attr>name)(?P<operator>[~])(?P<value>.+)$',
        'replacementname': '(?P<attr>replacementname)(?P<operator>[~])(?P<value>.+)$',
        'publishedon': '(?P<attr>publishedon)(?P<operator>[<=>])(?P<value>\d+)$',
        'deprecatedon': '(?P<attr>deprecatedon)(?P<operator>[<=>])(?P<value>\d+)$',
        'deletedon': '(?P<attr>deletedon)(?P<operator>[<=>])(?P<value>\d+)$'
    }
    filters = []
    for entry in arg.split(','):
        valid = False
        for attr, regex in valid_filters.iteritems():
            match = re.match(regex, entry)
            if match:
                valid = True
                filters.append(match.groupdict())
                break
        if not valid:
            __warn("Invalid filter phrase '%s' will be ignored." % entry)
    return filters


def __parse_response(response, fmt='json'):
    if fmt is 'json':
        return json.loads(response)
    elif fmt is 'xml':
        root = ET.fromstring(response)
        return {root.tag: [child.attrib for child in root]}


def __reformat(result_set, result_format):
    if result_format == 'json':
        return json.dumps(result_set)
    elif result_format == 'xml':
        root_tag = result_set.keys()[0]
        root = ET.Element(root_tag)
        for item in result_set[root_tag]:
            ET.SubElement(root, __inflect(root_tag), item)
        return ET.tostring(root, 'UTF-8', 'xml')


def __warn(str, out=sys.stdout):
    out.write("Warning: %s" % str)


def get_image_data(
        framework,
        image_state,
        result_format='plain',
        region='all',
        data_filter=None):
    """Return the requested image information"""
    generate_plain_text = False
    if result_format == 'plain':
        generate_plain_text = True
        result_format = 'xml'
    if region == 'all':
        region = None
    url = __form_url(
        framework,
        'images',
        result_format,
        region,
        image_state)
    if data_filter:
        __reformat(__get_and_filter_data(url, data_filter), result_format)
    else:
        return __get_data(url)


def get_server_data(
        framework,
        server_type,
        result_format='plain',
        region='all',
        data_filter=None):
    """Return the requested server information"""
    generate_plain_text = False
    if result_format == 'plain':
        generate_plain_text = True
        result_format = 'xml'
    if region == 'all':
        region = None
    url = __form_url(
        framework,
        'servers',
        result_format,
        region,
        server_type=server_type)
    if data_filter:
        __reformat(__get_and_filter_data(url, data_filter), result_format)
    else:
        return __get_data(url)
