# Copyright (c) 2015, SUSE LLC, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

"""Class to hold the information we need to connect and identify an SMT
   server."""


class SMT:
    """Store smt information"""
    def __init__(self, smtXMLNode):
        self.IP = smtXMLNode.attrib['SMTserverIP']
        self.FQDN = smtXMLNode.attrib['SMTserverName']
        self.fingerprint = smtXMLNode.attrib['fingerprint']

    # --------------------------------------------------------------------
    def get_domain_name(self):
        """Return the domain name for the server."""
        return self.FQDN.split('.', 1)[-1]

    # --------------------------------------------------------------------
    def get_fingerprint(self):
        """Return the fingerprint of the cert"""
        return self.fingerprint

    # --------------------------------------------------------------------
    def get_FQDN(self):
        """Return the fully qualified domain name"""
        return self.FQDN

    # --------------------------------------------------------------------
    def get_name(self):
        """Return the name"""
        return self.FQDN.split('.', 1)[0]

    # --------------------------------------------------------------------
    def get_ip(self):
        """Return the IP address"""
        return self.IP
