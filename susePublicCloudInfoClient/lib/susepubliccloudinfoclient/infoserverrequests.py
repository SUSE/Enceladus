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

import requests


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
    return __get_data(url)
