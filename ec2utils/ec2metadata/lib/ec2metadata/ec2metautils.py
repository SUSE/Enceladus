#
# Copyright (c) 2013 Alon Swartz <alon@turnkeylinux.org>
# Copyright (c) 2017 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
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

"""
Utilities to implement convenience functionality. Also allows us to keep
unnecessary state out of the metadata class
"""
import os
import sys
from io import IOBase

import ec2metadata


def _genXML(metadata, metaopts):
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
        raise ec2metadata.EC2MetadataError(msg)

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
        msg = 'Unable to write to file "%s"' % fout.name
        raise ec2metadata.EC2MetadataError(msg)
    finally:
        if close_file:
            fout.close()


def display(metadata, metaopts, prefix=False):
    """primitive: display metaopts (list) values with optional prefix"""

    writefile(sys.stdout, metadata, metaopts, prefix)


def displayXML(metadata, metaopts):
    """Collect the requested data and display it as XML"""
    data = _genXML(metadata, metaopts)
    print(data)


def showVersion():
    """Print the version"""
    verPath = os.path.dirname(__file__) + '/VERSION'
    print(open(verPath).read())


def writefile(filePath, metadata, metaopts, prefix=False):
    """Collect the requested data and write it to the given file."""

    data = ''
    for metaopt in metaopts:
        value = metadata.get(metaopt)
        if not value:
            value = "unavailable"

        if prefix:
            data += '%s: %s\n' % (metaopt, value)
        else:
            data += value + '\n'

    _write(filePath, data)


def writeXMLfile(filePath, metadata, metaopts):
    """Collect the requested data and write it to the given file as XML"""

    data = _genXML(metadata, metaopts)
    _write(filePath, data)
