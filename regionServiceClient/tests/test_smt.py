# Copyright (c) 2018 , SUSE LLC, All rights reserved.
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
import os
import sys

from lxml import etree
from mock import patch
from textwrap import dedent

test_path = os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe())))
code_path = os.path.abspath('%s/../lib/cloudregister' % test_path)

sys.path.insert(0, code_path)

from smt import SMT

smt_data_ipv4 = dedent('''\
    <smtInfo fingerprint="00:11:22:33"
     SMTserverIP="192.168.1.1"
     SMTserverName="fantasy.example.com"/>''')

smt_data_ipv6 = dedent('''\
    <smtInfo fingerprint="00:44:22:33"
     SMTserverIPv6="fc00::1"
     SMTserverName="fantasy.example.com"/>''')

smt_data_ipv46 = dedent('''\
    <smtInfo fingerprint="00:11:22:33"
     SMTserverIP="192.168.1.1"
     SMTserverIPv6="fc00::1"
     SMTserverName="fantasy.example.com"/>''')


# ----------------------------------------------------------------------------
class Response():
    """Fake a requeste response object"""
    pass


# ----------------------------------------------------------------------------
def test_ctor_ipv4():
    """Test object creation with IPv4 data only"""
    assert SMT(etree.fromstring(smt_data_ipv4))


# ----------------------------------------------------------------------------
def test_ctor_ipv6():
    """Test object creation with IPv6 data only"""
    assert SMT(etree.fromstring(smt_data_ipv6))


# ----------------------------------------------------------------------------
def test_ctor_dual():
    """Test object creation with IPv4 and IPv6 data only"""
    assert SMT(etree.fromstring(smt_data_ipv46))


# ----------------------------------------------------------------------------
def test_equal_ipv4():
    """Test two SMT servers with same data, IPv4 only are considered equal"""
    smt1 = SMT(etree.fromstring(smt_data_ipv4))
    smt2 = SMT(etree.fromstring(smt_data_ipv4))
    assert smt1 == smt2


# ----------------------------------------------------------------------------
def test_equal_ipv6():
    """Test two SMT servers with same data, IPv6 only are considered equal"""
    smt1 = SMT(etree.fromstring(smt_data_ipv6))
    smt2 = SMT(etree.fromstring(smt_data_ipv6))
    assert smt1 == smt2


# ----------------------------------------------------------------------------
def test_equal_dual():
    """Test two SMT servers with same data, IPv4 and IPv6 are
       considered equal"""
    smt1 = SMT(etree.fromstring(smt_data_ipv46))
    smt2 = SMT(etree.fromstring(smt_data_ipv46))
    assert smt1 == smt2


# ----------------------------------------------------------------------------
def test_not_equal_ipv4_ipv6():
    """Test two SMT servers with different data are not equal"""
    smt1 = SMT(etree.fromstring(smt_data_ipv4))
    smt2 = SMT(etree.fromstring(smt_data_ipv6))
    assert not smt1 == smt2


# ----------------------------------------------------------------------------
@patch('smt.logging')
@patch('smt.requests.get')
def test_get_cert_invalid_cert(mock_cert_pull, mock_logging):
    """Received an invalid cert"""
    response = Response()
    response.status_code = 200
    response.text = 'Not a cert'
    mock_cert_pull.return_value = response
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert not smt.get_cert()
    assert mock_logging.error.called
    msg = 'Could not read X509 fingerprint from cert'
    mock_logging.error.assert_called_with(msg)


# ----------------------------------------------------------------------------
@patch('smt.X509.load_cert_string')
@patch('smt.logging')
@patch('smt.requests.get')
def test_get_cert_no_match_cert(mock_cert_pull, mock_logging, mock_load_cert):
    """Received cert with different fingerprint"""
    response = Response()
    response.status_code = 200
    response.text = 'Not a cert'
    mock_cert_pull.return_value = response
    mock_load_cert.retun_value = 1
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert not smt.get_cert()
    assert mock_logging.error.called
    msg = 'Fingerprint could not be verified'
    mock_logging.error.assert_called_with(msg)


# ----------------------------------------------------------------------------
def test_get_domain_name():
    """Test get_domain_name returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv6))
    assert 'example.com' == smt.get_domain_name()


# ----------------------------------------------------------------------------
def test_get_fingerprint():
    """Test get_fingerprint returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert '00:11:22:33' == smt.get_fingerprint()


# ----------------------------------------------------------------------------
def test_get_FQDN():
    """Test get_FQDN returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert 'fantasy.example.com' == smt.get_FQDN()


# ----------------------------------------------------------------------------
def test_get_name():
    """Test get_name returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert 'fantasy' == smt.get_name()


# ----------------------------------------------------------------------------
def test_get_ipv4():
    """Test get_ipv4 returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert '192.168.1.1' == smt.get_ipv4()


# ----------------------------------------------------------------------------
def test_get_ipv4_null():
    """Test get_ipv4 returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv6))
    assert not smt.get_ipv4()


# ----------------------------------------------------------------------------
def test_get_ipv6():
    """Test get_ipv6 returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert 'fc00::1' == smt.get_ipv6()


# ----------------------------------------------------------------------------
def test_get_ipv6_null():
    """Test get_ipv6 returns expected value"""
    smt = SMT(etree.fromstring(smt_data_ipv4))
    assert not smt.get_ipv6()


# ----------------------------------------------------------------------------
def test_is_eqivalent():
    """Test two SMT servers with same name and fingerprint are treated
        as equivalent"""
    smt1 = SMT(etree.fromstring(smt_data_ipv4))
    smt2 = SMT(etree.fromstring(smt_data_ipv46))
    assert smt1.is_equivalent(smt2)


# ----------------------------------------------------------------------------
def test_is_eqivalent_fails():
    """Test two SMT servers with same name but different fingerprint are
       treated as not equivalent"""
    smt1 = SMT(etree.fromstring(smt_data_ipv4))
    smt2 = SMT(etree.fromstring(smt_data_ipv6))
    assert not smt1.is_equivalent(smt2)


# ----------------------------------------------------------------------------
@patch('smt.requests.get')
def test_is_responsive_server_offline(mock_cert_pull):
    """Verify we detect a non responsive server"""
    mock_cert_pull.return_value = None
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert not smt.is_responsive()


# ----------------------------------------------------------------------------
@patch('smt.requests.get')
def test_is_responsive_server_error(mock_cert_pull):
    """Verify we detect a server an error as non responsive"""
    response = Response()
    response.status_code = 500
    response.text = 'Not a cert'
    mock_cert_pull.return_value = response
    smt = SMT(etree.fromstring(smt_data_ipv46))
    assert not smt.is_responsive()
