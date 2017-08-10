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
import requests
from mock import patch
from nose.tools import raises
from io import StringIO


def test_warn_includes_warning():
    """The point of warn is to say so"""

    out = StringIO()
    ifsrequest.__warn("test", out)
    assert('Warning:' in out.getvalue())


@raises(SystemExit)
def test_errr_includes_error():
    """The point of error is to say so"""
    out = StringIO()
    ifsrequest.__error("test", out)
    assert('Error:' in out.getvalue())


@patch('lib.susepubliccloudinfoclient.infoserverrequests.requests.get')
@patch('lib.susepubliccloudinfoclient.infoserverrequests.__error')
def test_connection_error(mock_error, mock_get):
    mock_get.side_effect = requests.ConnectionError("Whoops!")
    ifsrequest.__get_data('http://foo.de.bar')
    assert mock_error.called
