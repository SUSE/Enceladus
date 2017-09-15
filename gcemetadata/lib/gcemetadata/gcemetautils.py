#
# Copyright (c) 2017 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of gcemetadata.
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

"""
Utilities to implement convenience functionality. Also allows us to keep
unnecessary state out of the metadata class
"""

import sys
from io import IOBase

import gcemetadata
from gcemetadata.gcemetaExceptions import *


def _clean_up_options(metadata, options):
    """Removes options with overloaded semantics if a suboption is provided"""
    if '--disks' in options:
        disk_options = metadata.get_disk_options()
        for disk_option in disk_options:
            if disk_option in options:
                options.remove('disks')
                break
    elif '--licenses' in options:
        license_options = metadata.get_license_options()
        for license_option in license_options:
            if license_option in options:
                options.remove('licenses')
                break
    elif '--network-interfaces' in options:
        net_options = metadata.getNetOptions()
        for net_option in net_options:
            if net_option in options:
                options.remove('network-interfaces')
                break

    return options


def _gen_xml(metadata, metaopts):
    """Use the option name as a tag name to wrap the data."""

    xml = ''
    for metaopt in metaopts:
        value = metadata.get(metaopt)
        if not value:
            value = "unavailable"
        xml += '<%s>' % metaopt
        xml += str(value)
        xml += '</%s>\n' % metaopt

    return xml


def _open_file(path):
    """Open a file for the given path"""
    fout = None
    try:
        fout = open(path, 'w')
    except:
        msg = 'Unable to open file "%s" for writing' % path
        raise GCEMetadataException(msg)

    return fout


def _write(file_path, data):
    """Write the data to the given file"""
    fout = None
    close_file = False
    if type(file_path) is str:
        fout = _open_file(file_path)
        close_file = True
    elif isinstance(file_path, IOBase):
        if file_path.closed:
            fout = _open_file(file_path.name)
            close_file = True
        else:
            fout = file_path
    try:
        fout.write(data)
    except:
        if close_file:
            fout.close()
        msg = 'Unable to write to file "%s"' % fout.name
        raise GCEMetadataException(msg)

    if close_file:
        fout.close()


def display_all(metadata, outfile=sys.stdout, gen_xml=False):
    """Display all metdata values"""
    metadata.query_all_sub_options(True)
    api_map = metadata.get_api_map()
    categories = metadata.get_option_categories()
    data = ''
    categories.sort()
    for cat in categories:
        metadata.set_data_category(cat)
        for option, item in api_map[cat].items():
            if type(item) is not dict:
                if gen_xml:
                    data += _gen_xml(metadata, [option])
                else:
                    try:
                        value = metadata.get(option)
                    except gcemetadata.GCEMetadataException as e:
                        print("Error:", e, file=sys.stderr)
                    if not value:
                        value = "unavailable"
                    data += "%s: %s\n" % (option, value)
            else:
                ids = api_map[cat][option].keys()
                for query_id in ids:
                    if option == 'disks':
                        metadata.set_disk_device(query_id)
                    elif option == 'licenses':
                        metadata.set_license_id(query_id)
                    else:
                        metadata.set_net_device(query_id)
                    for entry in api_map[cat][option][query_id].keys():
                        if gen_xml:
                            data += _gen_xml(metadata, [entry])
                        else:
                            try:
                                value = metadata.get(entry)
                            except gcemetadata.GCEMetadataException as e:
                                print("Error:", e, file=sys.stderr)
                            if not value:
                                value = "unavailable"
                            data += "%s: %s\n" % (entry, value)

    try:
        _write(outfile, data)
    except:
        print(sys.stderr, 'Could not write file "%s"' % outfile)
        sys.exit(1)


def display(metadata, metaopts, prefix=False):
    """primitive: display metaopts (list) values with optional prefix"""

    write_file(sys.stdout, metadata, metaopts, prefix)


def display_xml(metadata, metaopts):
    """Collect the requested data and display it as XML"""

    options = _clean_up_options(metadata, metaopts)

    data = _gen_xml(metadata, options)
    _write(sys.stdout, data)


def write_file(filePath, metadata, metaopts, prefix=False):
    """Collect the requested data and write it to the given file."""

    options = _clean_up_options(metadata, metaopts)

    data = ''
    for metaopt in options:
        value = None
        try:
            value = metadata.get(metaopt)
        except gcemetadata.GCEMetadataException as e:
            print("Error:", e, file=sys.stderr)
        if not value:
            value = "unavailable"

        if prefix:
            data += "%s: %s\n" % (metaopt, value)
        else:
            data += "%s\n" % value

    _write(filePath, data)


def write_xml_file(filePath, metadata, metaopts):
    """Collect the requested data and write it to the given file as XML"""

    options = _clean_up_options(metadata, metaopts)

    data = _gen_xml(metadata, options)
    _write(filePath, data)
