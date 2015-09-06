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

"""Utility functions for the cloud guest registration"""

import base64
import glob
import logging
import os
import pickle
import requests
import stat
import subprocess
import sys

from cloudregister import smt
from M2Crypto import X509

REGISTRATION_DATA_DIR = '/var/lib/cloudregister/'
REGISTERED_SMT_SERVER_DATA_FILE_NAME = 'currentSMTInfo.obj'
AVAILABLE_SMT_SERVER_DATA_FILE_NAME = 'availableSMTInfo_%d.obj'


# ----------------------------------------------------------------------------
def check_registration(smt_server_name):
    """Check if the instance is already registerd"""
    credentials_exist = has_credentials()
    repos_exist = has_repos(smt_server_name)
    if repos_exist and credentials_exist:
        return 1
    elif repos_exist and not credentials_exist:
        remove_repos(smt_server_name)
    elif credentials_exist and not repos_exist:
        # We might have to rethink this when BYOL comes along and
        # registers with our SMT
        remove_credentials()

    return None


# ----------------------------------------------------------------------------
def clean_hosts_file(domain_name):
    """Remove the smt server entry from the /etc/hosts file"""
    new_hosts_content = []
    content = open('/etc/hosts', 'r').readlines()
    smt_announce_found = None
    for entry in content:
        if '# Added by SMT' in entry:
            smt_announce_found = True
            continue
        if smt_announce_found and domain_name in entry:
            smt_announce_found = False
            continue
        new_hosts_content.append(entry)

    hosts_file = open('/etc/hosts', 'w')
    for entry in new_hosts_content:
        hosts_file.write(entry)
    hosts_file.close()


# ----------------------------------------------------------------------------
def exec_subprocess(cmd):
    """Execute the given command as a subprocess (blocking)"""
    try:
        cmd = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        cmd.communicate()
    except:
        return 0

    return 1


# ----------------------------------------------------------------------------
def get_available_smt_servers():
    """Return a list of available SMT servers"""
    availabe_smt_servers = []
    if not os.path.exists(REGISTRATION_DATA_DIR):
        return availabe_smt_servers
    smt_data_files = glob.glob(REGISTRATION_DATA_DIR + 'availableSMTInfo*')
    for smt_data in smt_data_files:
        availabe_smt_servers.append(get_smt_from_store(smt_data))

    return availabe_smt_servers


# ----------------------------------------------------------------------------
def get_current_smt():
    """Return the data for the current SMT server"""
    return get_smt_from_store(get_registered_smt_file_path())


# ----------------------------------------------------------------------------
def get_registered_smt_file_path():
    """Return the file path for the SMT infor stored for the registered
       server"""
    return REGISTRATION_DATA_DIR + REGISTERED_SMT_SERVER_DATA_FILE_NAME


# ----------------------------------------------------------------------------
def get_smt_cert(smt_ip, retries=3):
    """Return the response object or none if the request fails."""

    cert = None
    attempts = 0
    while attempts < retries:
        attempts += 1
        try:
            cert = requests.get('http://%s/smt.crt' % smt_ip)
        except:
            # No response from server
            logging.error('=' * 20)
            logging.error('Attempt %s of %s' % (attempts, retries))
            logging.error('Server %s is unreachable' % smt_ip)

    return cert


# ----------------------------------------------------------------------------
def get_smt_from_store(smt_store_file_path):
    """Create an SMTinstance from the stored data."""
    if not os.path.exists(smt_store_file_path):
        return None

    smt_file = open(smt_store_file_path, 'r')
    u = pickle.Unpickler(smt_file)
    try:
        smt = u.load()
    except:
        smt_file.close()
        return None

    smt_file.close()

    return smt


# ----------------------------------------------------------------------------
def get_zypper_command():
    """Returns the command line for zypper if zypper is running"""
    zypper_pid = get_zypper_pid()
    zypper_cmd = None
    if zypper_pid:
        zypper_cmd = open('/proc/%s/cmdline' % zypper_pid, 'r').read()
        zypper_cmd = zypper_cmd.replace('\x00', ' ')

    return zypper_cmd


# ----------------------------------------------------------------------------
def get_zypper_pid():
    """Return the PID of zypper if it is running"""
    zyppPIDCmd = ['ps', '-C', 'zypper', '-o', 'pid=']
    zyppPID = subprocess.Popen(zyppPIDCmd, stdout=subprocess.PIPE)
    pidData = zyppPID.communicate()

    return pidData[0].strip()


# ----------------------------------------------------------------------------
def has_credentials():
    """Check if a credentials file exists."""
    if (
            os.path.exists('/etc/zypp/credentials.d/NCCcredentials') or
            os.path.exists('/etc/zypp/credentials.d/SCCcredentials')):
        return 1

    return None


# ----------------------------------------------------------------------------
def has_repos(smt_server_name):
    """Check if repositories exist."""
    repo_name = smt_server_name.replace('.', '_')
    if (glob.glob('/etc/zypp/repos.d/*%s*' % repo_name)):
        return 1

    return None


# ----------------------------------------------------------------------------
def import_smtcert_11(smtCA_request):
    """Import the SMT certificate on SLES 11"""
    key_chain = '/etc/ssl/certs'
    if not write_cert(key_chain, smtCA_request):
        return 0
    if not update_ca_chain(['c_rehash', key_chain]):
        return 0

    return 1


# ----------------------------------------------------------------------------
def import_smtcert_12(smtCA_request):
    """Import the SMT certificate on SLES 12"""
    key_chain = '/usr/share/pki/trust/anchors'
    if not write_cert(key_chain, smtCA_request):
        return 0
    if not update_ca_chain(['update-ca-certificates']):
        return 0

    return 1


# ----------------------------------------------------------------------------
def import_smt_cert(smt):
    """Import the SMT certificate for the given server"""
    smtCA_request = get_smt_cert(smt.get_FQDN())
    if not smtCA_request:
        return None
    if not is_x509_fingerprint_valid(smtCA_request, smt):
        logging.error('SMT certificate fingerprint verification failed')
        return None
    import_result = None
    if is_sles11():
        import_result = import_smtcert_11(smtCA_request)
    else:
        import_result = import_smtcert_12(smtCA_request)
    if not import_result:
        logging.error('SMT certificate import failed')
        return None

    return 1


# ----------------------------------------------------------------------------
def is_registered(smt):
    """Firgure out if any of the servers is known and this instan"""
    if check_registration(smt.get_FQDN()):
        return 1

    return None


# ----------------------------------------------------------------------------
def is_sles11():
    """Return true if this is SLES 11"""
    if os.path.exists('/etc/SuSE-release'):
        content = open('/etc/SuSE-release', 'r').readlines()
        for ln in content:
            if 'SUSE Linux Enterprise Server 11' in ln:
                return True

    return False


# ----------------------------------------------------------------------------
def is_x509_fingerprint_valid(smtCA_request, smt):
    """Check if the fingerprint from the certificate in the request
       is the same as the fingerprint of the given SMT server."""
    try:
        x509 = X509.load_cert_string(str(smtCA_request.text))
        x509_fingerprint = x509.get_fingerprint('sha1')
    except:
        errMsg = 'Could not read X509 fingerprint from cert'
        logging.error(errMsg)
        return None
    if x509_fingerprint != smt.get_fingerprint().replace(':', ''):
        errMsg = 'Fingerprint could not be verified'
        logging.error(errMsg)
        return None

    return 1


# ----------------------------------------------------------------------------
def remove_credentials():
    """Remove the server generated credentials"""
    ncc_credentials = '/etc/zypp/credentials.d/NCCcredentials'
    scc_credentials = '/etc/zypp/credentials.d/SCCcredentials'
    if os.path.exists(ncc_credentials):
        logging.info('Removing credentials: %s' % ncc_credentials)
        os.unlink(ncc_credentials)
    if os.path.exists(scc_credentials):
        logging.info('Removing credentials: %s' % scc_credentials)
        os.unlink(scc_credentials)

    return 1


# ----------------------------------------------------------------------------
def remove_service(smt_server_name):
    """Remove the service for the given SMT server"""
    repo_service_name = smt_server_name.replace('.', '_')
    zypp_services = glob.glob('/etc/zypp/services.d/*%s*' % repo_service_name)
    for srv in zypp_services:
        logging.info('Removing service: %s' % srv)
        os.unlink(srv)

    return 1


# ----------------------------------------------------------------------------
def remove_registration_data(smt_servers):
    """Reset the instance to an unregistered state"""
    smt_data_file = get_registered_smt_file_path()
    if os.path.exists(smt_data_file):
        os.unlink(smt_data_file)
    for smt in smt_servers:
        server_name = smt.get_FQDN()
        domain_name = smt.get_domain_name()
        clean_hosts_file(domain_name)
        remove_repos(server_name)
        remove_credentials()
        remove_service(server_name)


# ----------------------------------------------------------------------------
def remove_repos(smt_server_name):
    """Remove the repositories for the given server"""
    repo_name = smt_server_name.replace('.', '_')
    repos = glob.glob('/etc/zypp/repos.d/*%s*' % repo_name)
    for repo in repos:
        logging.info('Removing repo: %s' % repo)
        os.unlink(repo)

    return 1


# ----------------------------------------------------------------------------
def replace_hosts_entry(current_smt, new_smt):
    """Replace the information of the SMT server in /etc/hosts"""
    known_hosts = open('/etc/hosts', 'r').readlines()
    new_hosts = ''
    current_smt_ip = current_smt.get_ip()
    for entry in known_hosts:
        if current_smt_ip in entry:
            new_hosts += '%s\t%s\t%s\n' % (new_smt.get_ip(),
                                           new_smt.get_FQDN(),
                                           new_smt.get_name())
            continue
        newHosts += entry

    hosts = open('/etc/hosts', 'w')
    hosts.write(new_hosts)
    hosts.close()


# ----------------------------------------------------------------------------
def start_logging():
    """Set up logging"""
    log_filename = '/var/log/cloudregister'
    try:
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
    except IOError:
        print 'Could not open log file ', logFile, ' for writing.'
        sys.exit(1)


# ----------------------------------------------------------------------------
def store_smt_data(smt_data_file_path, smt):
    """Store the given SMT server information to the given file"""
    smt_data = open(smt_data_file_path, 'w')
    os.fchmod(smt_data.fileno(), stat.S_IREAD | stat.S_IWRITE)
    p = pickle.Pickler(smt_data)
    p.dump(smt)
    smt_data.close()


# ----------------------------------------------------------------------------
def update_ca_chain(cmd_w_args_lst):
    """Update the CA chain using the given command with arguments"""
    logging.info('Updating CA certificates: %s' % cmd_w_args_lst[0])
    if not exec_subprocess(cmd_w_args_lst):
        errMsg = 'Certificate update failed'
        logging.error(errMsg)
        return 0

    return 1


# ----------------------------------------------------------------------------
def write_cert(target_dir, smtCA_request):
    """Write the certificat to the given location"""
    logging.info('Writing SMT rootCA: %s' % target_dir)
    ca_file_path = target_dir + '/registration_server.pem'
    try:
        smt_ca_file = open(ca_file_path, 'w')
        smt_ca_file.write(smtCA_request.text)
        smt_ca_file.close()
    except IOError:
        errMsg = 'Could not store SMT certificate'
        logging.error(errMsg)
        return 0
