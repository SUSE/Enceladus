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

import msftazure as azure


# ----------------------------------------------------------------------------
class Response():
    pass


# ____________________________________________________________________________
class Resolver():
    pass


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_metadata_request_fail(mock_logging, mock_request, mock_resolver):
    """Test proper exception handling when request to metadata server fails"""
    mock_request.side_effect = Exception
    mock_resolver.return_value = _get_no_nameservers_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'Unable to determine instance placement from metadata '
    expected += 'server "http://169.254.169.254/metadata/instance/location"'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_metadata_request_fail_server_error(mock_logging, mock_request):
    """Test metadata server error code return"""
    mock_request.return_value = _get_error_response()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'Unable to get availability zone metadata'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected
    expected = '\tReturn code: 500'
    actual = _get_msg(mock_logging.warning.call_args_list[1])
    assert actual == expected
    expected = '\tMessage: Test server failure'
    actual = _get_msg(mock_logging.warning.call_args_list[2])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.requests.get')
def test_metadata_request_success(mock_request):
    """Test unexpected return value"""
    mock_request.return_value = _get_expected_response_metadata()
    result = azure.generateRegionSrvArgs()
    assert result == 'regionHint=useast'


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_goal_state_request_fail(
        mock_logging,
        mock_request,
        mock_resolver
):
    """Test behavior goal state access triggering exception"""
    mock_request.side_effect = [None, Exception]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'Could not retrieve goal state XML from 1.1.1.1'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_goal_state_request_fail_server_error(
        mock_logging,
        mock_request,
        mock_resolver
):
    """Test behavior with goal state access triggering server error"""
    mock_request.side_effect = [None, _get_error_response()]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = '1.1.1.1 error for goal state request: 500'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_goal_state_request_success_no_match(
        mock_logging,
        mock_request,
        mock_resolver
):
    """Test behavior with goal state request success improper data"""
    mock_request.side_effect = [None, _get_unexpected_response()]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'No "<ExtensionsConfig>" in goal state XML'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_extension_request_fail(
        mock_logging,
        mock_request,
        mock_resolver
):
    """Test behavior with extension request triggering  exception"""
    mock_request.side_effect = [
        None,
        _get_proper_goal_state_resposne(),
        Exception
    ]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'Could not get extensions information from "'
    expected += 'http://ola%sdme&?getit=1"'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_extension_request_fail_server_error(
        mock_logging,
        mock_request,
        mock_resolver
):
    """Test request for extension data triggering server error"""
    mock_request.side_effect = [
        None,
        _get_proper_goal_state_resposne(),
        _get_error_response()
    ]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'Extensions request failed with: 500'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_extension_request_success_no_match(
        mock_logging,
        mock_request,
        mock_resolver
):
    """Test request for extension data success improper data"""
    mock_request.side_effect = [
        None,
        _get_proper_goal_state_resposne(),
        _get_unexpected_response()
    ]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == None
    assert mock_logging.warning.called
    expected = 'No "<Location>" in extensions XML'
    actual = _get_msg(mock_logging.warning.call_args_list[0])
    assert actual == expected


# ----------------------------------------------------------------------------
@patch('msftazure.dns.resolver.get_default_resolver')
@patch('msftazure.requests.get')
@patch('msftazure.logging')
def test_wire_request_sucess(mock_logging, mock_request, mock_resolver):
    """Test success for info on the wire server"""
    mock_request.side_effect = [
        None,
        _get_proper_goal_state_resposne(),
        _get_proper_extensions_response()
    ]
    mock_resolver.return_value = _get_nameserver_resolver()
    result = azure.generateRegionSrvArgs()
    assert result == 'regionHint=useast'


# ----------------------------------------------------------------------------
def _get_error_response():
    """Return an error code as the response of the request"""
    response = Response()
    response.status_code = 500
    response.text = 'Test server failure'
    return response


# ----------------------------------------------------------------------------
def _get_expected_response_metadata():
    """Return an object mocking a expected response"""
    response = Response()
    response.status_code = 200
    response.text = 'useast'
    return response


# ----------------------------------------------------------------------------
def _get_msg(log_moc_call):
    """Extract the message provided to the log mock"""
    args, kwargs = log_moc_call
    return args[0]


# ----------------------------------------------------------------------------
def _get_nameserver_resolver():
    """Return a resolver with a nameserver"""
    resolver = Resolver()
    resolver.nameservers = ['1.1.1.1']
    return resolver


# ----------------------------------------------------------------------------
def _get_no_nameservers_resolver():
    """Return a resolver with an empty nameserver"""
    resolver = Resolver()
    resolver.nameservers = []
    return resolver


# ----------------------------------------------------------------------------
def _get_proper_extensions_response():
    """Return a response that matches extensions config"""
    response = Response()
    response.status_code = 200
    data = 'the_doc '
    data += '<Location>useast</Location>'
    data += 'last'
    response.text = data
    return response


# ----------------------------------------------------------------------------
def _get_proper_goal_state_resposne():
    """Return a response that matches goal state config"""
    response = Response()
    response.status_code = 200
    data = 'the_doc '
    data += '<ExtensionsConfig>http://ola%sdme&amp;?getit=1</ExtensionsConfig>'
    data += 'last'
    response.text = data
    return response


# ----------------------------------------------------------------------------
def _get_unexpected_response():
    """Return an unexpected response, i.e. trigget a parse error"""
    response = Response()
    response.status_code = 200
    response.text = 'This matches nothing'
    return response
