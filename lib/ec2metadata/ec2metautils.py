#
# Copyright (c) 2013 Alon Swartz <alon@turnkeylinux.org>
# Copyright (c) 2014 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of ec2metadata.
#
# ec2metadata is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#

"""
Utilities to implement convenience functionality. Also allows us to keep
unnecessary state out of the metadata class
"""

import ec2metadata

def _genXML(metadata, metaopts):
    """Use the option name as a tag name to wrap the data."""

    xml = ''
    for metaopt in metaopts:
        value = metadata.get(metaopt)
        if not value:
            value = "unavailable"
        xml += '<%s>' %metaopt
        xml += value
        xml += '</%s>\n' %metaopt
        
    return xml

def _write(filePath, data):
    """Write the data to the given file"""
    fout = open(filePath, 'w')
    fout.write(data)
    fout.close()

def display(metadata, metaopts, prefix=False):
    """primitive: display metaopts (list) values with optional prefix"""

    for metaopt in metaopts:
        value = metadata.get(metaopt)
        if not value:
            value = "unavailable"

        if prefix:
            print "%s: %s" % (metaopt, value)
        else:
            print value

def displayXML(metadata, metaopts):
    """Collect the requested data and display it as XML"""
    data = _genXML(metadata, metaopts)
    print data

def writefile(filePath, metadata, metaopts, prefix=False):
    """Collect the requested data and write it to the given file."""

    data = ''
    for metaopt in metaopts:
        value = metadata.get(metaopt)
        if not value:
            value = "unavailable"

        if prefix:
            data += '%s: %s' % (metaopt, value)
        else:
            data += value

    _write(filePath, data)

def writeXMLfile(filePath, metadata, metaopts):
    """Collect the requested data and write it to the given file as XML"""

    data = _genXML(metadata, metaopts)
    _write(filePath, data)
