# Copyright (c) 2015 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
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
# along with gcemetadata.  If not, see <http://www.gnu.org/licenses/>.

import os
import socket
import urllib2

from gcemetaExceptions import *

class GCEMetadata:
    """Class for interacting with the metadata from GCE"""

    def __init__(self, apiv='v1'):
        self.apiv   = apiv
        # GCE also has a deprecated API "0.1" but we always want to use
        # the "computeMetadata" API
        self.api            = 'computeMetadata'
        self.dataCategories = ['project/', 'instance/']
        self.defaultDiskID  = '0'
        self.default_license_id = '0'
        self.defaultNetID   = '0'
        self.disk_data_shown = []
        self.diskDevID      = -1
        self.header         = {'Metadata-Flavor' : 'Google'}
        self.identity_arg = None
        self.identity_format = 'standard'
        self.license_data_shown = []
        self.license_id = -1
        self.net_data_shown = []
        self.netDevID       = -1
        self.options        = {}
        self.query_disk_data = False
        self.query_license_data = False
        self.query_net_data = False
        self.server         = 'metadata.google.internal'

        if apiv not in self.getAvailableAPIVersions():
            msg = 'Given API version "%s" not available' %apiv
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


    def _add_arguments(self, option):
        """Add an argument to the uri"""
        arg_map = { 
            'identity' : 'audience=%s&format=%s' %(
                self.identity_arg, self.identity_format
            )
        }
        if option in arg_map.keys():
            return '?%s' %arg_map[option]

        return ''
        
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
                elif (
                        item == 'disks/' or
                        item == 'network-interfaces/' or
                        item == 'licenses/'
                ):
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

    def _genFlatOptLst(self, optMap=None):
        """Flatten the API map to generate a list of quesry options"""
        optLst = []
        if not optMap:
            optMap = self.options
        for opt in optMap:
            if type(optMap[opt]) == dict:
                optLst += self._genFlatOptLst(optMap[opt])
            optLst.append(opt)

        return optLst

    def _genList(self, valueStr):
        """Return a list from a new line separated string with no trailing /"""
        values = valueStr.split('\n')
        items = []
        for value in values:
            if value:
                items.append(value.rstrip('/'))
        return items

    def _get(self, url):
        """Return the value for the requested uri"""
        req = urllib2.Request(url, headers=self.header)
        # DEBUG print REMOVE
        #print 'debug: Request URL: %s' %url
        try:
            value = urllib2.urlopen(req).read()
        except:
            return None

        return value

    def _get_item_id_list(self, deviceName):
        """Return a list of device IDs for the given device name"""
        url = self._buildFullURL('instance/' + deviceName)
        devIDs = self._get(url)
        return self._genList(devIDs)

    def _getDeviceOpts(self, devType):
        """Return the available query options for the given device type"""
        opts = []
        data = self.options[self.queryCat].get(devType, None)
        if not data:
            return ''
        for dev in data.keys():
            for opt in data[dev].keys():
                if opt not in opts:
                    opts.append(opt)
        return opts

    def _getPathFromSubOpt(self, option):
        """Find the given option in a nested tree"""
        diskOpts = self._getDeviceOpts('disks')
        netOpts = self._getDeviceOpts('network-interfaces')
        license_opts = self._getDeviceOpts('licenses')
        path = None
        opt_id = None
        category_data = self.options[self.queryCat]
        if option in diskOpts:
            self.disk_data_shown.append(option)
            if self.diskDevID == -1:
                opt_id = self.defaultDiskID
            else:
                opt_id = self.diskDevID
            path = category_data['disks'][opt_id].get(option, None)
        elif option in license_opts:
            self.license_data_shown.append(option)
            if self.license_id == -1:
                opt_id = self.default_license_id
            else:
                opt_id = self.license_id
            path = category_data['licenses'][opt_id].get(option, None)
        elif option in netOpts:
            self.net_data_shown.append(option)
            if self.netDevID == -1:
                opt_id = self.defaultNetID
            else:
                opt_id = self.netDevID
            path = category_data['network-interfaces'][opt_id].get(option, None)

        return path
        
    def get(self, option):
        """Get the data for the specified option"""
        optMap = self._genFlatOptLst()
        if not option in optMap:
            return None
        if (
                option == 'disks' or
                option == 'network-interfaces' or
                option == 'licenses'
        ):
            return self._get_item_id_list(option)

        path = None
        # Top level accessors and lovwer level accessors are not necessarily
        # unique, for example "id" is used for license and for instance id.
        # Thus we need to differentiate what the user is looking for. When
        # querying for a path that has suboptions such as disks, licenses,
        # and network interfaces we give preference to the sub options if
        # --diskid --licenseid or --netid where specifid. However we also
        # need to account for the usecase where the user may want both,
        # thus we need to keep track of the options already shown.
        if (
                (
                    self.query_disk_data or
                    self.query_license_data or
                    self.query_net_data
                )
                and 
                (
                    option not in self.disk_data_shown and
                    option not in self.license_data_shown and
                    option not in self.net_data_shown
                )
        ):
            path = self._getPathFromSubOpt(option)
        if not path:
            path = self.options[self.queryCat].get(option, None)
        # Try the sub options again as the user may have specified a unique
        # suboption identifier such as --disk-name that we can find without
        # special handling
        if not path:
            path = self._getPathFromSubOpt(option)

        if not path:
            msg = 'No query path for option "%s", please file a bug' %option
            raise GCEMetadataException(msg)

        path += option + self._add_arguments(option)

        return self._get(self._buildFullURL(path))
        
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
        return self._getDeviceOpts('disks')

    def getFlatenedOpts(self, category=None):
        """Return a list for all query options"""
        return self._genFlatOptLst(category)

    def get_license_options(self):
        "Return a list of available query options for selected licenses"""
        return self._getDeviceOpts('licenses')

    def getNetOptions(self):
        """Return a list of available query options for the selected device"""
        return self._getDeviceOpts('network-interfaces')
        
    def getOptionCategories(self):
        """Return the list of option categories"""
        return self.dataCategories

    def getVersion(self):
        """Return the version string"""
        verPath = os.path.dirname(__file__) + '/VERSION'
        return open(verPath).read()

    def query_all_sub_options(self, on_off=False):
        """If set enables the querying of all suboptions"""
        if on_off:
            self.query_disk_data = True
            self.query_license_data = True
            self.query_net_data = True

    def setAPIVersion(self, apiv):
        """Set the API Version to use for the query"""
        apiVers = self.getAvailableAPIVersions()

        if apiv not in apiVers:
            msg = 'Specififed api version "%s" not available ' %apiv
            msg += 'must be one of %s' %apiVers
            raise GCEMetadataException(msg)

        self.apiv = apiv

    def setDataCat(self, category):
        """Set the data category for this query"""
        if category[-1] != '/':
            category = category + '/'
        if category not in self.dataCategories:
            msg = 'Query option "%s" invalid, must be ' %category
            msg += 'one of %s' %self.dataCategories
            raise GCEMetadataException(msg)

        self.queryCat = category

        return 1

    def setDiskDevice(self, devID):
        """Set the disk device ID to query"""
        knownIDs = self._get_item_id_list('disks')
        if devID not in knownIDs:
            msg = 'Requested device "%s" not available for query. ' %devID
            msg += 'Available disks: %s' %knownIDs
            raise GCEMetadataException(msg)

        self.diskDevID = devID
        self.query_disk_data = True
        self.disk_data_shown = []

    def set_identity_arg(self, audience):
        """Set the argument for the JWT generation"""
        self.identity_arg = audience

    def set_identity_format(self, id_format):
        """Set the format for the identity token, full or standard"""
        self.identity_format = id_format

    def set_license_id(self, license_id):
        """Set the id for the license to query"""
        known_ids = self._get_item_id_list('licenses')
        if license_id not in known_ids:
            msg = 'Requested license "%s" not available for query. ' %license_id
            msg += 'Available license: %s' %known_ids
            raise GCEMetadataException(msg)

        self.license_id = license_id
        self.query_license_data = True
        self.license_data_shown = []

    def setNetDevice(self, devID):
        """Set the network device ID to query"""
        knownIDs = self._get_item_id_list('network-interfaces')
        if devID not in knownIDs:
            msg = 'Requested device "%s" not available for query. ' %devID
            msg += 'Available network interfaces: %s' %knownIDs
            raise GCEMetadataException(msg)

        self.netDevID = devID
        self.query_net_data = True
        self.net_data_shown = []
