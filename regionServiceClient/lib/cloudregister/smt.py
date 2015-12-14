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

import logging
import requests

from M2Crypto import X509


class SMT:
    """Store smt information"""
    def __init__(self, smtXMLNode):
        self._ip = smtXMLNode.attrib['SMTserverIP']
        self._fqdn = smtXMLNode.attrib['SMTserverName']
        self._fingerprint = smtXMLNode.attrib['fingerprint']
        self._cert = None

    # --------------------------------------------------------------------
    def get_cert(self):
        """Return the CA certificate for the SMT server"""
        if not self._cert:
            cert_rq = self.__request_cert()
            if cert_rq:
                cert = cert_rq.text
                if self.__is_cert_valid(cert):
                    self._cert = cert

        return self._cert

    # --------------------------------------------------------------------
    def get_domain_name(self):
        """Return the domain name for the server."""
        return self._fqdn.split('.', 1)[-1]

    # --------------------------------------------------------------------
    def get_fingerprint(self):
        """Return the fingerprint of the cert"""
        return self._fingerprint

    # --------------------------------------------------------------------
    def get_FQDN(self):
        """Return the fully qualified domain name"""
        return self._fqdn

    # --------------------------------------------------------------------
    def get_name(self):
        """Return the name"""
        return self._fqdn.split('.', 1)[0]

    # --------------------------------------------------------------------
    def get_ip(self):
        """Return the IP address"""
        return self._ip

    # --------------------------------------------------------------------
    def is_equivalent(self, smt_server):
        """When 2 SMT servers have the same cert fingerprint and their
           FQDN is the same they are equivalent."""
        if (
                self.get_FQDN() == smt_server.get_FQDN() and
                self.get_fingerprint() == smt_server.get_fingerprint()):
            return 1

        return None

    # --------------------------------------------------------------------
    def is_responsive(self):
        """Check if the SMT server is responsive"""
        request = self.__request_cert()
        if request and request.status_code == 200:
            if self.__is_cert_valid(request.text):
                return True
            msg = 'Cert verify failed during access test, notify administrator'
            logging.error(msg)

        return False

    # --------------------------------------------------------------------
    def write_cert(self, target_dir):
        """Write the certificate to the given directory"""
        logging.info('Writing SMT rootCA: %s' % target_dir)
        ca_file_path = (
            target_dir +
            '/registration_server_%s.pem' % self.get_ip().replace('.', '_'))
        try:
            smt_ca_file = open(ca_file_path, 'w')
            smt_ca_file.write(self.get_cert())
            smt_ca_file.close()
        except IOError:
            errMsg = 'Could not store SMT certificate'
            logging.error(errMsg)
            return 0

        return 1

    # Private
    # --------------------------------------------------------------------
    def __is_cert_valid(self, cert):
        """Verfify that the fingerprint of the given cert matches the
           expected fingerprint"""
        try:
            x509 = X509.load_cert_string(str(cert))
            x509_fingerprint = x509.get_fingerprint('sha1')
        except:
            errMsg = 'Could not read X509 fingerprint from cert'
            logging.error(errMsg)
            return False

        if x509_fingerprint != self.get_fingerprint().replace(':', ''):
            errMsg = 'Fingerprint could not be verified'
            logging.error(errMsg)
            return False

        return True

    # --------------------------------------------------------------------
    def __request_cert(self):
        """Request the cert from the SMT server and return the request"""
        cert_rq = None
        attempts = 0
        retries = 3
        while attempts < retries:
            attempts += 1
            try:
                cert_rq = requests.get('http://%s/smt.crt' % self.get_ip())
            except:
                # No response from server
                logging.error('=' * 20)
                logging.error('Attempt %s of %s' % (attempts, retries))
                logging.error('Server %s is unreachable' % self.get_ip())
            if cert_rq and cert_rq.status_code == 200:
                attempts = retries

        return cert_rq
