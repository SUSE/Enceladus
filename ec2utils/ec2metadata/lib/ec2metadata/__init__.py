# Copyright (c) 2013 Alon Swartz <alon@turnkeylinux.org>
# Copyright (c) 2014 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of ec2metadata.
#
# ec2metadata is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ec2metadata is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ec2metadata.  If not, see <http://www.gnu.org/licenses/>.

import time
import urllib
import socket

class EC2MetadataError(Exception):
    pass

class EC2Metadata:
    """Class for querying metadata from EC2"""

    def __init__(self, addr='169.254.169.254', api='2008-02-01'):
        self.addr    = addr
        self.api     = api
        self.dataCategories  = ['dynamic/', 'meta-data/']

        if not self._test_connectivity(self.addr, 80):
            msg = 'Could not establish connection to: %s' % self.addr
            raise EC2MetadataError(msg)

        self._resetetaOptsAPIMap()
        self._setMetaOpts()

    @staticmethod
    def _test_connectivity(addr, port):
        for i in range(6):
            s = socket.socket()
            try:
                s.connect((addr, port))
                s.close()
                return True
            except socket.error, e:
                time.sleep(1)

        return False

    def _addMetaOpts(self, path):
        """Add meta options available under the current path to the options
           to API map"""
        options = self.metaOptsAPIMap.keys()
        value = self._get(path)
        if not value:
            return None
        entries = value.split('\n')
        for item in entries:
            if item:
                if item == 'public-keys/':
                    continue
                if item not in options:
                    if item[-1] != '/':
                        self.metaOptsAPIMap[item] = path + item
                    else:
                        self._addMetaOpts(path+item)

    def _get(self, uri):
        url = 'http://%s/%s/%s' % (self.addr, self.api, uri)
        value = urllib.urlopen(url).read()
        if "404 - Not Found" in value:
            return None

        return value

    def _resetetaOptsAPIMap(self):
        """Set options that have special semantics"""
        self.metaOptsAPIMap = { 'public-keys' : 'meta-data/public-keys',
                                'user-data' : 'user-data'
                              }
        
    def _setMetaOpts(self):
        """Set the metadata options for the current API on this object."""
        for path in self.dataCategories:
            self._addMetaOpts(path)

    def get(self, metaopt):
        """Return value of metaopt"""

        path = self.metaOptsAPIMap.get(metaopt, None)
        if not path:
            raise EC2MetadataError('Unknown metaopt: %s' %metaopt)

        if metaopt == 'public-keys':
            public_keys = []
            data = self._get('meta-data/public-keys')
            if not data:
                return public_keys

            keyids = [ line.split('=')[0] for line in data.splitlines() ]
            for keyid in keyids:
                uri = 'meta-data/public-keys/%d/openssh-key' % int(keyid)
                public_keys.append(self._get(uri).rstrip())

            return public_keys

        return self._get(path)

    def getAvailableAPIVersions(self):
        """Return a list of the available API versions"""
        url = 'http://%s/' %self.addr
        value = urllib.urlopen(url).read()
        apiVers = value.split('\n')
        return apiVers
    
    def getMetaOptions(self):
        """Return the available options for the current api version"""
        options = self.metaOptsAPIMap.keys()
        options.sort()
        return options
    
    def setAPIVersion(self, apiVersion=None):
        """Set the API version to use for the query"""
        if not apiVersion:
            # Nothing to do
            return self.api
        url = 'http://%s' %self.addr
        availableAPIs = urllib.urlopen(url).read().split('\n')
        if apiVersion not in availableAPIs:
            msg = 'Requested API version "%s" not available' %apiVersion
            raise EC2MetadataError(msg)
        self.api = apiVersion
        self._resetetaOptsAPIMap()
        self._setMetaOpts()

