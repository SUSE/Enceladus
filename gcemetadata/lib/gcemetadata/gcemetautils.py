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

import gcemetadata
import sys

def _cleanUpOptions(metadata, options):
    """Removes options with overloaded semantics if a suboption is provided"""
    if '--disks' in options:
        diskOpts = metadata.getDiskOptions()
        for dOpt in diskOptions:
            if dOpt in options:
                options.remove('disks')
                break
    elif '--network-interfaces' in options:
        netOpts = metadata.getNetOptions()
        for nOpt in netOptions:
            if nOpt in options:
                options.remove('network-interfaces')
                break

    return options

def _genXML(metadata, metaopts):
    """Use the option name as a tag name to wrap the data."""

    xml = ''
    for metaopt in metaopts:
        value = metadata.get(metaopt)
        if not value:
            value = "unavailable"
        xml += '<%s>' %metaopt
        xml += str(value)
        xml += '</%s>\n' %metaopt
        
    return xml

def _write(filePath, data):
    """Write the data to the given file"""
    fout = None
    if type(filePath) is str:
        fout = open(filePath, 'w')
    elif type(filePath) is file:
        fout = filePath
    fout.write(data)
    fout.close()

def displayAll(metadata, outfile=sys.stdout, gen_xml=False):
    """Display all metdata values"""
    apiMap = metadata.getAPIMap()
    categories = metadata.getOptionCategories()
    data = ''
    categories.sort()
    for cat in categories:
        metadata.setDataCat(cat)
        for option in apiMap[cat].keys():
            if option != 'disks' and option != 'network-interfaces':
                if gen_xml:
                    data += _genXML(metadata, [option])
                else:
                    try:
                        value = metadata.get(option)
                    except gcemetadata.GCEMetadataException, e:
                        print >> sys.stderr, "Error:", e
                    if not value:
                        value = "unavailable"
                    data += "%s: %s\n" % (option, value)
            else:
                ids = apiMap[cat][option].keys()
                for devID in ids:
                    if option == 'disks':
                        metadata.setDiskDevice(devID)
                    else:
                        metadata.setNetDevice(devID)
                    for entry in apiMap[cat][option][devID]:
                        if gen_xml:
                            data += _genXML(metadata, [option])
                        else:
                            try:
                                value = metadata.get(option)
                            except gcemetadata.GCEMetadataException, e:
                                print >> sys.stderr, "Error:", e
                            if not value:
                                value = "unavailable"
                            data += "%s: %s\n" % (option, value) 

    try:
        _write(outfile, data)
    except:
        print syst.stderr, 'Could not write file "%s"' %outfile
        sys.exit(1)
                            
    
def display(metadata, metaopts, prefix=False):
    """primitive: display metaopts (list) values with optional prefix"""

    write_file(sys.stdout, metadata, metaopts, prefix)

def display_xml(metadata, metaopts):
    """Collect the requested data and display it as XML"""

    options = _cleanUpOptions(metadata, metaopts)

    data = _genXML(metadata, options)
    _write(sys.stdout, data)

def write_file(filePath, metadata, metaopts, prefix=False):
    """Collect the requested data and write it to the given file."""

    options = _cleanUpOptions(metadata, metaopts)

    data = ''
    for metaopt in options:
        value = None
        try:
            value = metadata.get(metaopt)
        except gcemetadata.GCEMetadataException, e:
            print >> sys.stderr, "Error:", e
        if not value:
            value = "unavailable"

        if prefix:
            data += "%s: %s\n" %(metaopt, value)
        else:
            data += "%s\n" %value

    _write(filePath, data)

def write_xml_file(filePath, metadata, metaopts):
    """Collect the requested data and write it to the given file as XML"""

    options = _cleanUpOptions(metadata, metaopts)

    data = _genXML(metadata, metaopts)
    _write(filePath, data)
