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

AVAILABLE_SMT_SERVER_DATA_FILE_NAME = 'availableSMTInfo_%d.obj'
HOSTSFILE_PATH = '/etc/hosts'
REGISTRATION_DATA_DIR = '/var/lib/cloudregister/'
REGISTERED_SMT_SERVER_DATA_FILE_NAME = 'currentSMTInfo.obj'


# ----------------------------------------------------------------------------
def check_registration(smt_server_name):
    """Check if the instance is already registerd"""
    if has_repos(smt_server_name) and __has_credentials(smt_server_name):
        return 1

    return None


# ----------------------------------------------------------------------------
def clean_hosts_file(domain_name):
    """Remove the smt server entry from the /etc/hosts file"""
    new_hosts_content = []
    content = open(HOSTSFILE_PATH, 'r').readlines()
    smt_announce_found = None
    for entry in content:
        if '# Added by SMT' in entry:
            smt_announce_found = True
            continue
        if smt_announce_found and domain_name in entry:
            smt_announce_found = False
            continue
        new_hosts_content.append(entry)

    with open(HOSTSFILE_PATH, 'w') as hosts_file:
        for entry in new_hosts_content:
            hosts_file.write(entry)


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
def find_equivalent_smt_server(configured_smt, known_smt_servers):
    """Find an SMT server that is equivalent to the currently configured
       SMT server, only consider responsive servers"""
    for smt in known_smt_servers:
        if smt.get_ip() == configured_smt.get_ip():
            continue
        if smt.is_equivalent(configured_smt) and smt.is_responsive():
            return smt

    return None


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
    return get_smt_from_store(__get_registered_smt_file_path())


# ----------------------------------------------------------------------------
def get_smt_from_store(smt_store_file_path):
    """Create an SMTinstance from the stored data."""
    if not os.path.exists(smt_store_file_path):
        return None

    smt = None
    with open(smt_store_file_path, 'r') as smt_file:
        u = pickle.Unpickler(smt_file)
        try:
            smt = u.load()
        except:
            pass

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
def has_repos(smt_server_name):
    """Check if repositories exist."""
    repo_files = glob.glob('/etc/zypp/repos.d/*')
    for repo_file in repo_files:
        content = open(repo_file, 'r').readlines()
        for ln in content:
            if 'baseurl' in ln and smt_server_name in ln:
                return 1

    return None


# ----------------------------------------------------------------------------
def import_smtcert_11(smt):
    """Import the SMT certificate on SLES 11"""
    key_chain = '/etc/ssl/certs'
    if not smt.write_cert(key_chain):
        return 0
    if not update_ca_chain(['c_rehash', key_chain]):
        return 0

    return 1


# ----------------------------------------------------------------------------
def import_smtcert_12(smt):
    """Import the SMT certificate on SLES 12"""
    key_chain = '/usr/share/pki/trust/anchors'
    if not smt.write_cert(key_chain):
        return 0
    if not update_ca_chain(['update-ca-certificates']):
        return 0

    return 1


# ----------------------------------------------------------------------------
def import_smt_cert(smt):
    """Import the SMT certificate for the given server"""
    import_result = None
    if is_sles11():
        import_result = import_smtcert_11(smt)
    else:
        import_result = import_smtcert_12(smt)
    if not import_result:
        logging.error('SMT certificate import failed')
        return None

    return 1


# ----------------------------------------------------------------------------
def is_registered(smt):
    """Figure out if any of the servers is known"""
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
def set_as_current_smt(smt):
    """Store the given SMT as the current SMT server."""
    if not os.path.exists(REGISTRATION_DATA_DIR):
        os.system('mkdir -p %s' % REGISTRATION_DATA_DIR)
    store_smt_data(__get_registered_smt_file_path(), smt)


# ----------------------------------------------------------------------------
def set_proxy():
    """Set up proxy environment if applicable"""
    proxy_config_file = '/etc/sysconfig/proxy'
    if not os.path.exists(proxy_config_file):
        return False
    existing_http_proxy = os.environ.get('http_proxy')
    existing_https_proxy = os.environ.get('https_proxy')
    if (existing_http_proxy and existing_https_proxy):
        # If the environment variables exist all external functions used
        # by the registration code will honor them, thus we can tell the
        # client that we didn't do anything, which also happens to be true
        logging.info('Using proxy settings from execution environment')
        logging.info('\thttp_proxy: %s' % existing_http_proxy)
        logging.info('\thttps_proxy: %s' % existing_https_proxy)
        return False
    proxy_config = open(proxy_config_file, 'r').readlines()
    http_proxy = ''
    https_proxy = ''
    for entry in proxy_config:
        if 'PROXY_ENABLED' in entry and 'no' in entry:
            return False
        if 'HTTP_PROXY' in entry:
            http_proxy = entry.split('"')[1]
        if 'HTTPS_PROXY' in entry:
            https_proxy = entry.split('"')[1]
    os.environ['http_proxy'] = http_proxy
    os.environ['https_proxy'] = https_proxy

    return True


# ----------------------------------------------------------------------------
def remove_registration_data(smt_servers):
    """Reset the instance to an unregistered state"""
    smt_data_file = __get_registered_smt_file_path()
    if os.path.exists(smt_data_file):
        os.unlink(smt_data_file)
    for smt in smt_servers:
        server_name = smt.get_FQDN()
        domain_name = smt.get_domain_name()
        clean_hosts_file(domain_name)
        __remove_credentials(server_name)
        __remove_repos(server_name)
        __remove_service(server_name)


# ----------------------------------------------------------------------------
def replace_hosts_entry(current_smt, new_smt):
    """Replace the information of the SMT server in /etc/hosts"""
    known_hosts = open(HOSTSFILE_PATH, 'r').readlines()
    new_hosts = ''
    current_smt_ip = current_smt.get_ip()
    for entry in known_hosts:
        if current_smt_ip in entry:
            new_hosts += '%s\t%s\t%s\n' % (new_smt.get_ip(),
                                           new_smt.get_FQDN(),
                                           new_smt.get_name())
            continue
        new_hosts += entry

    with open(HOSTSFILE_PATH, 'w') as hosts_file:
        hosts_file.write(new_hosts)


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
def switch_smt_repos(smt):
    """Switch all the repositories pointing to the current SMT server to the
       given SMT server."""
    repo_files = glob.glob('/etc/zypp/repos.d/*.repo')
    __replace_url_target(repo_files, smt)


# ----------------------------------------------------------------------------
def switch_smt_service(smt):
    """Switch the existing service to the given SMT server"""
    service_files = glob.glob('/etc/zypp/services.d/*.service*')
    __replace_url_target(service_files, smt)


# ----------------------------------------------------------------------------
def update_ca_chain(cmd_w_args_lst):
    """Update the CA chain using the given command with arguments"""
    logging.info('Updating CA certificates: %s' % cmd_w_args_lst[0])
    if not exec_subprocess(cmd_w_args_lst):
        errMsg = 'Certificate update failed'
        logging.error(errMsg)
        return 0

    return 1


# Private
# ----------------------------------------------------------------------------
def __get_referenced_credentials(smt_server_name):
    """Return a list of credential names referenced by repositories"""
    repo_files = glob.glob('/etc/zypp/repos.d/*.repo')
    referenced_credentials = []
    for repo in repo_files:
        content = open(repo, 'r').readlines()
        for ln in content:
            if 'baseurl' in ln and smt_server_name in ln:
                line_parts = ln.split('?credentials=')
                if len(line_parts) > 1:
                    credentials_name = line_parts[-1].strip()
                    if credentials_name not in referenced_credentials:
                        referenced_credentials.append(credentials_name)

    return referenced_credentials


# ----------------------------------------------------------------------------
def __get_registered_smt_file_path():
    """Return the file path for the SMT infor stored for the registered
       server"""
    return REGISTRATION_DATA_DIR + REGISTERED_SMT_SERVER_DATA_FILE_NAME


# ----------------------------------------------------------------------------
def __has_credentials(smt_server_name):
    """Check if a credentials file exists."""
    referenced_credentials = __get_referenced_credentials(smt_server_name)
    credential_files = glob.glob('/etc/zypp/credentials.d/*')
    for credential_file in credential_files:
        name = os.path.basename(credential_file)
        if name in referenced_credentials:
            return 1

    return None


# ----------------------------------------------------------------------------
def __remove_credentials(smt_server_name):
    """Remove the server generated credentials"""
    referenced_credentials = __get_referenced_credentials(smt_server_name)
    base_credentials = ['NCCcredentials', 'SCCcredentials']
    for credential_name in base_credentials:
        if credential_name not in referenced_credentials:
            referenced_credentials.append(credential_name)
    credential_path = '/etc/zypp/credentials.d/'
    for credential_name in referenced_credentials:
        credential_file_path = credential_path + credential_name
        if os.path.exists(credential_file_path):
            logging.info('Removing credentials: %s' % credential_name)
            os.unlink(credential_file_path)

    return 1


# ----------------------------------------------------------------------------
def __remove_repos(smt_server_name):
    """Remove the repositories for the given server"""
    repo_files = glob.glob('/etc/zypp/repos.d/*')
    for repo_file in repo_files:
        content = open(repo_file, 'r').readlines()
        for ln in content:
            if 'baseurl' in ln and smt_server_name in ln:
                logging.info('Removing repo: %s' % os.path.basename(repo_file))
                os.unlink(repo_file)

    return 1


# ----------------------------------------------------------------------------
def __remove_service(smt_server_name):
    """Remove the service for the given SMT server"""
    service_files = glob.glob('/etc/zypp/services.d/*')
    for service_file in service_files:
        content = open(service_file, 'r').readlines()
        for ln in content:
            if 'url' in ln and smt_server_name in ln:
                logging.info('Removing service: %s'
                             % os.path.basename(service_file))
                os.unlink(service_file)

    return 1


# ----------------------------------------------------------------------------
def __replace_url_target(config_files, new_smt):
    """Switch the url of the current SMT server for the given SMT server"""
    current_smt = get_current_smt()
    current_service_server = current_smt.get_FQDN()
    for config_file in config_files:
        content = open(config_file, 'r').read()
        if current_service_server in content:
            new_config = open(config_file, 'w')
            new_config.write(content.replace(
                current_service_server,
                new_smt.get_FQDN()))
            new_config.close()
