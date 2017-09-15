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
import time
import urllib.request, urllib.error, urllib.parse

from gcemetadata.gcemetaExceptions import *


class GCEMetadata:
    """Class for interacting with the metadata from GCE"""

    def __init__(self, apiv='v1'):
        self.apiv = apiv
        # GCE also has a deprecated API "0.1" but we always want to use
        # the "computeMetadata" API
        self.api = 'computeMetadata'
        self.data_categories = ['project/', 'instance/']
        self.default_disk_id = '0'
        self.default_license_id = '0'
        self.default_net_dev_id = '0'
        self.disk_data_shown = []
        self.disk_dev_id = -1
        self.header = {'Metadata-Flavor': 'Google'}
        self.identity_arg = None
        self.identity_format = 'standard'
        self.license_data_shown = []
        self.license_id = -1
        self.net_data_shown = []
        self.net_dev_id = -1
        self.options = {}
        self.query_disk_data = False
        self.query_license_data = False
        self.query_net_data = False
        self.server = 'metadata.google.internal'

        if apiv not in self.get_available_api_versions():
            msg = 'Given API version "%s" not available' % apiv
            raise GCEMetadataException(msg)

        if not self._test_connectivity(self.server, 80):
            msg = 'Could not connect to: %s' % self.server
            raise GCEMetadataException(msg)

        self._create_options_map()

    def _test_connectivity(self, addr, port):
        for i in range(6):
            s = socket.socket()
            try:
                s.connect((addr, port))
                s.close()
                return True
            except socket.error:
                time.sleep(1)

        return False

    def _add_arguments(self, option):
        """Add an argument to the uri"""
        arg_map = {
            'identity': 'audience=%s&format=%s' % (
                self.identity_arg, self.identity_format
            )
        }
        if option in arg_map.keys():
            return '?%s' % arg_map[option]

        return ''

    def _add_options(self, path, option_entry=None):
        """Collect all options in the given path"""
        options = {}
        value = self._get(self._build_full_url(path))
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
                    options[item[:-1]] = self._add_options(path + item)
                else:
                    next_level = None
                    if (
                            item[0].isdigit() and
                            path.find('service-account') == -1
                    ):
                        next_level = self._add_options(path + item, item[0])
                    elif option_entry:
                        next_level = self._add_options(
                            path + item, option_entry
                        )
                    else:
                        next_level = self._add_options(path + item)
                    if next_level:
                        if (
                                item[0].isdigit() and
                                item[0] != option_entry and
                                path.find('service-account') == -1
                        ):
                            options[item[0]] = next_level
                        else:
                            options.update(next_level)
        return options

    def _build_full_url(self, uri):
        """Return the complete url"""
        return 'http://%s/%s/%s/%s' % (self.server, self.api, self.apiv, uri)

    def _create_options_map(self):
        """Set up all options for the selected API"""
        for cat in self.data_categories:
            self.options[cat] = self._add_options(cat)

    def _gen_flat_option_list(self, option_map=None):
        """Flatten the API map to generate a list of quesry options"""
        option_list = []
        if not option_map:
            option_map = self.options
        for opt in option_map:
            if type(option_map[opt]) == dict:
                option_list += self._gen_flat_option_list(option_map[opt])
            option_list.append(opt)

        return option_list

    def _generate_list_from_str(self, valueStr):
        """Return a list from a new line separated string with no trailing /"""
        values = valueStr.split('\n')
        items = []
        for value in values:
            if value:
                items.append(value.rstrip('/'))
        return items

    def _get(self, url):
        """Return the value for the requested uri"""
        req = urllib.request.Request(url, headers=self.header)
        try:
            value = urllib.request.urlopen(req).read()
        except:
            return None

        return value.decode()

    def _get_item_id_list(self, item_name):
        """Return a list of device IDs for the given device name"""
        url = self._build_full_url('instance/' + item_name)
        item_ids = self._get(url)
        return self._generate_list_from_str(item_ids)

    def _get_item_suboptions(self, query_item):
        """Return the available query options for the given query option"""
        opts = []
        data = self.options[self.query_category].get(query_item, None)
        if not data:
            return ''
        for dev in data.keys():
            for opt in data[dev].keys():
                if opt not in opts:
                    opts.append(opt)
        return opts

    def _get_path_from_suboption(self, option):
        """Find the given option in a nested tree"""
        disk_options = self._get_item_suboptions('disks')
        net_options = self._get_item_suboptions('network-interfaces')
        license_options = self._get_item_suboptions('licenses')
        path = None
        opt_id = None
        category_data = self.options[self.query_category]
        if option in disk_options:
            self.disk_data_shown.append(option)
            if self.disk_dev_id == -1:
                opt_id = self.default_disk_id
            else:
                opt_id = self.disk_dev_id
            path = category_data['disks'][opt_id].get(option, None)
        elif option in license_options:
            self.license_data_shown.append(option)
            if self.license_id == -1:
                opt_id = self.default_license_id
            else:
                opt_id = self.license_id
            path = category_data['licenses'][opt_id].get(option, None)
        elif option in net_options:
            self.net_data_shown.append(option)
            if self.net_dev_id == -1:
                opt_id = self.default_net_dev_id
            else:
                opt_id = self.net_dev_id
            interfaces = category_data['network-interfaces']
            path = interfaces[opt_id].get(option, None)

        return path

    def get(self, option):
        """Get the data for the specified option"""
        option_map = self._gen_flat_option_list()
        if option not in option_map:
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
                ) and
                (
                    option not in self.disk_data_shown and
                    option not in self.license_data_shown and
                    option not in self.net_data_shown
                )
        ):
            path = self._get_path_from_suboption(option)
        if not path:
            path = self.options[self.query_category].get(option, None)
        # Try the sub options again as the user may have specified a unique
        # suboption identifier such as --disk-name that we can find without
        # special handling
        if not path:
            path = self._get_path_from_suboption(option)

        if not path:
            msg = 'No query path for option "%s", please file a bug' % option
            raise GCEMetadataException(msg)

        path += option + self._add_arguments(option)

        return self._get(self._build_full_url(path))

    def get_api_map(self):
        """Retrun the map of all options including the access path"""
        return self.options

    def get_available_api_versions(self):
        """Return a list of available API versions"""
        value = self._get('http://%s/%s' % (self.server, self.api))
        api_versions = None
        if value:
            api_versions = self._generate_list_from_str(value)
        return api_versions

    def get_disk_options(self):
        """Return a list of available query options for the selected disk"""
        return self._get_item_suboptions('disks')

    def get_flattened_opts(self, category=None):
        """Return a list for all query options"""
        return self._gen_flat_option_list(category)

    def get_license_options(self):
        "Return a list of available query options for selected licenses"""
        return self._get_item_suboptions('licenses')

    def get_net_dev_options(self):
        """Return a list of available query options for the selected device"""
        return self._get_item_suboptions('network-interfaces')

    def get_option_categories(self):
        """Return the list of option categories"""
        return self.data_categories

    def get_version(self):
        """Return the version string"""
        version_file_path = os.path.dirname(__file__) + '/VERSION'
        return open(version_file_path).read()

    def query_all_sub_options(self, on_off=False):
        """If set enables the querying of all suboptions"""
        if on_off:
            self.query_disk_data = True
            self.query_license_data = True
            self.query_net_data = True

    def set_api_version(self, apiv):
        """Set the API Version to use for the query"""
        known_api_versions = self.get_available_api_versions()

        if apiv not in known_api_versions:
            msg = 'Specififed api version "%s" not available ' % apiv
            msg += 'must be one of %s' % known_api_versions
            raise GCEMetadataException(msg)

        self.apiv = apiv

    def set_data_category(self, category):
        """Set the data category for this query"""
        if category[-1] != '/':
            category = category + '/'
        if category not in self.data_categories:
            msg = 'Query option "%s" invalid, must be ' % category
            msg += 'one of %s' % self.data_categories
            raise GCEMetadataException(msg)

        self.query_category = category

        return 1

    def set_disk_device(self, disk_id):
        """Set the disk device ID to query"""
        known_disk_ids = self._get_item_id_list('disks')
        if disk_id not in known_disk_ids:
            msg = 'Requested device "%s" not available for query. ' % disk_id
            msg += 'Available disks: %s' % known_disk_ids
            raise GCEMetadataException(msg)

        self.disk_dev_id = disk_id
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
            msg = 'Requested license "%s" ' % license_id
            msg += 'not available for query.  '
            msg += 'Available license: %s' % known_ids
            raise GCEMetadataException(msg)

        self.license_id = license_id
        self.query_license_data = True
        self.license_data_shown = []

    def set_net_device(self, net_dev_id):
        """Set the network device ID to query"""
        known_ids = self._get_item_id_list('network-interfaces')
        if net_dev_id not in known_ids:
            msg = 'Requested device "%s" not available for ' % net_dev_id
            msg += 'query. Available network interfaces: %s' % known_ids
            raise GCEMetadataException(msg)

        self.net_dev_id = net_dev_id
        self.query_net_data = True
        self.net_data_shown = []
