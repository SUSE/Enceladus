# Copyright (c) 2017, SUSE LLC, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

import inspect
import logging
import os
import pytest
import sys

from mock import patch

test_path = os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe())))
code_path = os.path.abspath('%s/../lib/cloudregister' % test_path)

sys.path.insert(0, code_path)

import googlece as gce


# ----------------------------------------------------------------------------
class Response():
    pass


# ----------------------------------------------------------------------------
@patch('googlece.requests.get')
@patch('googlece.logging')
def test_request_fail(mock_logging, mock_request):
    """Test proper exception handling when request to metadata server fails"""
    mock_request.side_effect = Exception
    result = gce.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    msg = 'Unable to determine zone information from "'
    msg += 'http://169.254.169.254/computeMetadata/v1/instance/zone'
    msg += '"'
    mock_logging.warning.assert_called_with(msg)


# ----------------------------------------------------------------------------
@patch('googlece.requests.get')
@patch('googlece.logging')
def test_request_fail_parse_response(mock_logging, mock_request):
    """Test unexpected return value"""
    mock_request.return_value = _get_unexpected_response()
    result = gce.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    msg = 'Unable to form region string from text: '
    msg += 'projects/284177885636/zones/us-central1'
    mock_logging.warning.assert_called_with(msg)


# ----------------------------------------------------------------------------
@patch('googlece.requests.get')
@patch('googlece.logging')
def test_request_fail_response_error(mock_logging, mock_request):
    """Test unexpected return value"""
    mock_request.return_value = _get_error_response()
    result = gce.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    msg = '\tMessage: Test server failure'
    mock_logging.warning.assert_called_with(msg)


# ----------------------------------------------------------------------------
@patch('googlece.requests.get')
def test_request_succeed(mock_request):
    """Test behavior with expected return value"""
    mock_request.return_value = _get_expected_response()
    result = gce.generateRegionSrvArgs()
    assert 'regionHint=us-central1' == result


# ----------------------------------------------------------------------------
def _get_error_response():
    """Return an error code as the response of the request"""
    response = Response()
    response.status_code = 500
    response.text = 'Test server failure'
    return response


# ----------------------------------------------------------------------------
def _get_expected_response():
    """Return an object mocking a expected response"""
    response = Response()
    response.status_code = 200
    response.text = 'projects/284177885636/zones/us-central1-f'
    return response


# ----------------------------------------------------------------------------
def _get_unexpected_response():
    """Return an unexpected response, i.e. trigget a parse error"""
    response = Response()
    response.status_code = 200
    response.text = 'projects/284177885636/zones/us-central1'
    return response
