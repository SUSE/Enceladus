#!/usr/bin/env python
#
# Copyright (c) 2013 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of ec2metadata.
#
# ec2metadata is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
"""
Query and display EC2 metadata related to the AMI instance

If no options are specified, all will be displayed.
"""

import sys
import getopt

import ec2metadata

def usage(e=None):
    if e:
        print >> sys.stderr, "Error:", e

    print >> sys.stderr, "Syntax: %s [--options]" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()

    print >> sys.stderr, "Options:"
    for metaopt in ec2metadata.METAOPTS:
        print >> sys.stderr, "    --" + metaopt

    sys.exit(1)

def main():
    try:
        getopt_metaopts = ec2metadata.METAOPTS[:]
        getopt_metaopts.append('help')
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", getopt_metaopts)
    except getopt.GetoptError, e:
        usage(e)

    if len(opts) == 0:
        ec2metadata.display(ec2metadata.METAOPTS, prefix=True)
        return

    metaopts = []
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        metaopts.append(opt.replace('--', ''))

    ec2metadata.display(metaopts)


if __name__ == "__main__":
   main()
