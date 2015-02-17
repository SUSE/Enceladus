#
# Copyright (c) 2015 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
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

def _cleanUpOptions(metadata, options):
    """Removes options with overloaded semantics is a suboption is provided"""
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
        

def display(metadata, metaopts, prefix=False):
    """primitive: display metaopts (list) values with optional prefix"""

    options = _cleanUpOptions(metadata, metaopts)

    for metaopt in options:
        value = None
        try:
            value = metadata.get(metaopt)
        except gcemetadata.GCEMetadataException, e:
            print >> sys.stderr, "Error:", e
        if not value:
            value = "unavailable"

        if prefix:
            print "%s: %s" % (metaopt, value)
        else:
            print value
