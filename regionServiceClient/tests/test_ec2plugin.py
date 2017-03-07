# Copyright (c) $2017, SUSE LLC, All rights reserved.
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

import amazonec2 as ec2


# ----------------------------------------------------------------------------
class Response():
    pass


# ----------------------------------------------------------------------------
@patch('amazonec2.requests.get')
@patch('amazonec2.logging')
def test_request_fail(mock_logging, mock_request):
    """Test proper exception handling when request to metadata server fails"""
    mock_request.side_effect = Exception
    result = ec2.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    msg = 'Unable to determine instance placement from "'
    msg += 'http://169.254.169.254/latest/meta-data/placement/'
    msg += 'availability-zone'
    msg += '"'
    mock_logging.warning.assert_called_with(msg)


# ----------------------------------------------------------------------------
@patch('amazonec2.requests.get')
@patch('amazonec2.logging')
def test_request_fail_response_error(mock_logging, mock_request):
    """Test unexpected return value"""
    mock_request.return_value = _get_error_response()
    result = ec2.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    msg = '\tMessage: Test server failure'
    mock_logging.warning.assert_called_with(msg)


# ----------------------------------------------------------------------------
@patch('amazonec2.requests.get')
def test_request_succeed(mock_request):
    """Test behavior with expected return value"""
    mock_request.return_value = _get_expected_response()
    result = ec2.generateRegionSrvArgs()
    assert 'regionHint=us-east-1' == result


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
    response.text = 'us-east-1f'
    return response


# ----------------------------------------------------------------------------
def _get_unexpected_response():
    """Return an unexpected response, i.e. trigget a parse error"""
    response = Response()
    response.status_code = 200
    response.text = ''
    return response
