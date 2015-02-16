# Copyright (c) 2015SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of gcemetadata.
#
# gcemetadata is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gcemetadata is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ec2metadata.  If not, see <http://www.gnu.org/licenses/>.

import os
import socket
import urllib2

class GCEMetadataException(Exception):
    pass

class GCEMetadata:
    """Class for interacting with the metadata from GCE"""

    def __init__(self, apiv='v1'):
        self.apiv   = apiv
        # GCE also has a deprecated API "0.1" but we always want to use
        # the "computeMetadata" API
        self.api            = 'computeMetadata'
        self.dataCategories = ['project/', 'instance/']
        self.defaultDiskID  = '0'
        self.defaultNetID   = '0'
        self.diskDevID      = -1
        self.header         = {'Metadata-Flavor' : 'Google'}
        self.netDevID       = -1
        self.options        = {}
        self.server         = 'metadata.google.internal'

        if apiv not in self.getAvailableAPIVersions():
            msg = 'Given API version "%s" not available' %s
            raise GCEMetadataException(msg)

        if not self._test_connectivity(self.server, 80):
            msg = 'Could not connect to: %s' %self.server
            raise GCEMetadataException(msg)

        self._createOptionsMap()
        # DEBUG print REMOVE
#        print 'RJS debug: --- Options Dict ---'
#        print self.options
        
        
    def _test_connectivity(self, addr, port):
        for i in range(6):
            s = socket.socket()
            try:
                s.connect((addr, port))
                s.close()
                return True
            except socket.error, e:
                time.sleep(1)

        return False

    def _addOptions(self, path, devID=None):
        """Collect all options in the given path"""
        options = {}
        value = self._get(self._buildFullURL(path))
        if not value:
            return None
        entries = value.split('\n')
        for item in entries:
            if item:
                if item[-1] != '/' and not item[0].isdigit():
                    options[item] = path
                elif item == 'disks/' or item == 'network-interfaces/':
                    options[item[:-1]] = self._addOptions(path + item)
                else:
                    nextLevel = None
                    if item[0].isdigit() and path.find('service-account') == -1:
                        nextLevel = self._addOptions(path + item, item[0])
                    elif devID:
                        nextLevel = self._addOptions(path + item, devID)
                    else:
                        nextLevel = self._addOptions(path + item)
                    if nextLevel:
                        if (item[0].isdigit()
                            and item[0] != devID
                            and path.find('service-account') == -1):
                            options[item[0]] = nextLevel
                        else:
                            options.update(nextLevel)
        return options

    def _buildFullURL(self, uri):
        """Return the complete url"""
        return 'http://%s/%s/%s/%s' %(self.server, self.api, self.apiv, uri)

    def _createOptionsMap(self):
        """Set up all options for the selected API"""
        for cat in self.dataCategories:
            self.options[cat] = self._addOptions(cat)

    def _genList(self, valueStr):
        """Return a list from a new line separated string with no trailing /"""
        values = valueStr.split('\n')
        return [value.rstrip('/') for value in values]

    def _get(self, url):
        """Return the value for the requested uri"""
        req = urllib2.Request(url, headers=self.header)
        # DEBUG print REMOVE
        #print 'Request URL: %s' %url
        try:
            value = urllib2.urlopen(req).read()
        except:
            return None

        return value

    def _getDevIDList(self, deviceName):
        """Return a list of device IDs for the given device name"""
        url = self._buildFUllURL('instance/' + deviceName)
        devIDs = self._get(url)
        return self._genList(devIDs)

    def get(self, option):
        """Get the data for the specified option"""
        optMap = self.options[self.queryCat]
        if not optMap.get(option, None):
            return None
        if option == 'disks' or option =='network-interfaces':
            return self._getDevice
        
    def getAPIMap(self):
        """Retrun the map of all options including the access path"""
        return self.options

    def getAvailableAPIVersions(self):
        """Return a list of available API versions"""
        value = self._get('http://%s/%s' %(self.server, self.api))
        apiVers = None
        if value:
            apiVers = self._genList(value)
        return apiVers

    def getDiskOptions(self):
        """Return a list of available query options for the selected disk"""
        return 

    def getNetOptions(self):
        """Return a list of available query options for the selected device"""
        return 
        
    def getOptionCategories(self):
        """Return the list of option categories"""
        return self.dataCategories

    def getVersion(self):
        """Return the version string"""
        verPath = os.path.dirname(__file__) + '/VERSION'
        return open(verPath).read()

    def setAPIVersion(self, apiv):
        """Set the API Version to use for the query"""
        apiVers = self.getAvailableAPIVersions()

        if apiv not in apiVers:
            msg = 'Specififed api version "%s" not available ' %apiv
            msg += 'must be one of %s' %apiVers
            raise GCEMetadataException(msg)

        self.apiv = apiv

    def setDataCat(category):
        """Set the data category for this query"""
        if category not in self.dataCategories:
            msg = 'Query option "%s" invalid, must be ' %category
            msg += 'one of %s' %self.dataCategories
            raise GCEMetadataException(msg)

        self.queryCat = category

        return 1

    def setDiskDevice(devID):
        """Set the disk device ID to query"""
        knownIDs = self._getDevIDList('disks')
        if devID not in knownIDs:
            msg = 'Requested device "%s" not available for query. ' %devID
            msg += 'Available disks: %s' %knownIDs

        self.diskDevID = devID

    def setNetDevice(devID):
        """Set the network device ID to query"""
        knownIDs = self._getDevIDList('network-interfaces')
        if devID not in knownIDs:
            msg = 'Requested device "%s" not available for query. ' %devID
            msg += 'Available network interfaces: %s' %knownIDs

        self.netDevID = devID
