# Copyright (c) 2018 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of ec2utilsbase.
#
# ec2utilsbase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ec2utilsbase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ec2utilsbase.  If not, see <http://www.gnu.org/licenses/>.

"""
Service that returns SMT server information based on a region hint or the
IP address of the requesting client.

The service works with two configuration files, the configuration for
the service itself, /etc/regionService/regionInfo.cfg by default or
specified with -f on the command line; and the configuration for the
region SMT server data, /etc/regionService/regionData.cfg, or as configured.

The regionInfo.cfg file is in ini format containing a [server] section
with the logFile and regionConfig options.

[server]
logFile = PATH_TO_LOGFILE_INCLUDING_LOGNAME
regionConfig = PATH_TO_REGION_DATA_FILE_INCLUDING_FILENAME

The region data configuration file is also in ini format. Each section
defines a region and contains options for public-ips, smt-server-ip,
smt-server-name, and smt-fingerprint. It is assumed that there is no DNS
resolution of the name, thus both fields -ip and -name are expected.

[region]
public-ips = COMMA_SEPARATED_LIST_OF_IP_ADDRESSES_WITH_MASK_POSTFIX
smt-server-ip = IP_OF_SMT_SERVER_FOR_THIS_REGION
smt-server-name = HOSTNAME_OF_SMT_SERVER_FOR_THIS_REGION
smt-fingerprint = SMT_CERT_FINGERPRINT
"""

import configparser
import getopt
import ipaddress
import logging
import os
import random
import sys

from flask import Flask
from flask import request


# ============================================================================
def create_smt_region_map(conf):
    """Create two mappings:
         ip_to_smt_data_map:
             maps all IP ranges to their respctive SMT server info
         region_name_to_smt_data_map:
             maps all region names to their respective SMT server info"""
    ip_range_to_smt_data_map = {}
    region_name_to_smt_data_map = {}
    region_data_cfg = configparser.RawConfigParser()
    try:
        parsed = region_data_cfg.read(conf)
    except Exception:
        logging.error('Could not parse configuration file %s' % conf)
        type, value, tb = sys.exc_info()
        logging.error(value.message)
        return
    if not parsed:
        logging.error('Error parsing config file: %s' % conf)
        return

    for section in region_data_cfg.sections():
        try:
            region_public_ip_ranges = region_data_cfg.get(
                section,
                'public-ips'
            )
        except Exception:
            logging.error('Missing public-ips data in section %s' % section)
            sys.exit(1)
        try:
            region_smt_ips = region_data_cfg.get(section, 'smt-server-ip')
        except Exception:
            logging.error('Missing smt-server-ip data in section %s' % section)
            sys.exit(1)
        try:
            region_smt_names = region_data_cfg.get(section, 'smt-server-name')
        except Exception:
            logging.error(
                'Missing smt-server-name data in section %s' % section
            )
            sys.exit(1)
        try:
            region_smt_cert_fingerprints = region_data_cfg.get(
                section,
                'smt-fingerprint'
            )
        except Exception:
            logging.error(
                'Missing smt-fingerprint data in section %s' % section
            )
            sys.exit(1)
        smt_ips = region_smt_ips.split(',')
        if len(smt_ips) > 1:
            smt_names = region_smt_names.split(',')
            if len(smt_names) > 1 and len(smt_names) != len(smt_ips):
                logging.error(
                    'Ambiguous SMT name and SMT IP pairings %s' % section
                )
                sys.exit(1)
            smt_cert_fingerprints = region_smt_cert_fingerprints.split(',')
            if (
                    len(smt_cert_fingerprints) > 1 and
                    len(smt_cert_fingerprints) != len(smt_ips)
            ):
                logging.error(
                    'Ambiguous SMT name and finger print pairings %s' % section
                )
                sys.exit(1)
        smtInfo = (
            region_smt_ips,
            region_smt_names,
            region_smt_cert_fingerprints
        )
        region_name_to_smt_data_map[section] = smtInfo
        for ip_range in region_public_ip_ranges.split(','):
            try:
                ipaddress.ip_network(ip_range)
            except ValueError:
                msg = 'Could not proces range, improper format: %s'
                logging.error(msg % ip_range)
                continue
            ip_range_to_smt_data_map[ip_range] = smtInfo

    return ip_range_to_smt_data_map, region_name_to_smt_data_map


# ============================================================================
def find_longest_prefix_ipv4(requester, ip_range_map):
    """Find IP ranges for IPv4 adresses that are likely to contain the
       requester address"""
    potential_ranges = {
        1: [],
        2: [],
        3: []
    }
    results_map = {}
    requester_parts = requester.split('.')
    for ip_range in ip_range_map.keys():
        ip_range_parts = ip_range.split('.')
        match_cnt = 0
        for i in range(3):
            if requester_parts[i] == ip_range_parts[i]:
                match_cnt += 1
        if match_cnt:
            potential_ranges[match_cnt].append(ip_range)
    for match_len in [3, 2, 1]:
        if not potential_ranges[match_len]:
            continue
        for ip_range in potential_ranges[match_len]:
            results_map[ip_range] = ip_range_map[ip_range]
        return results_map


# ============================================================================
def usage():
    """Print a usage message"""
    msg = '-f, --file       -> specify the service configuration file\n'
    msg += '-h, --help       -> print this message\n'
    msg += '-l, --log        -> specify the log file\n'
    msg += '-r, --regiondata -> specify the region data configuration file\n'
    print(msg)


# ============================================================================
# Process the command line options
try:
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'f:hl:r:',
                                   ['file=', 'help', 'log=', 'regiondata='])
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(1)

region_info_config_name = '/etc/regionService/regionInfo.cfg'
region_data_config_name = None
log_name = None
for option, option_value in cmd_opts:
    if option in ('-f', '--file'):
        region_info_config_name = option_value
        if not os.path.isfile(region_info_config_name):
            msg = 'Could not find specified configuration file "%s"'
            print(msg % region_info_config_name)
            sys.exit(1)
    elif option in ('-h', '--help'):
        usage()
        sys.exit(0)
    elif option in ('-l', '--log'):
        log_name = option_value
        log_dir = os.path.dirname(os.path.abspath(log_name))
        if not os.access(log_dir, os.W_OK):
            print('Log directory "%s" is not writable' % log_dir)
            sys.exit(1)
    elif option in ('-r', '--regiondata'):
        region_data_config_name = option_value
        if not os.path.isfile(region_data_config_name):
            msg = 'Could not find specified configuration file "%s"'
            print(msg % region_data_config_name)
            sys.exit(1)

srvConfig = configparser.RawConfigParser()
try:
    parsed = srvConfig.read(region_info_config_name)
except Exception:
    msg = 'Could not parse configuration file "%s"'
    print(msg % region_info_config_name)
    type, value, tb = sys.exc_info()
    print(value.message)
    sys.exit(1)

if not parsed:
    print('Error parsing configuration file "%s"' % region_info_config_name)
    sys.exit(1)

# Assign default log file if not provided
if not log_name:
    log_name = srvConfig.get('server', 'logFile')

# Assign default region data config if not provided
if not region_data_config_name:
    region_data_config_name = srvConfig.get('server', 'regionConfig')
    if not os.path.isfile(region_data_config_name):
        msg = 'Default configuration file "%s" not found'
        print(msg % region_data_config_name)
        sys.exit(1)

# Set up logging
try:
    logging.basicConfig(
        filename=log_name,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
except IOError:
    print('Could not open log file "%s" for writing.' % log_name)
    sys.exit(1)


# Build the map initially
ip_range_to_smt_data_map, region_name_to_smt_data_map = create_smt_region_map(
    region_data_config_name
)

# Implement the REST API
app = Flask(__name__)


@app.route('/regionInfo')
def index():
    """Provide the SMT server information based on the IP address
       region association. This path only suports IPv4"""
    requester = request.remote_addr
    logging.info('Data request from: %s' % requester)
    url = request.url
    region_hint = url.split('regionHint=')[-1]
    smt_server_data = None
    if region_hint != url:
        logging.info('\tRegion hint: %s' % region_hint)
        smt_server_data = region_name_to_smt_data_map.get(region_hint, None)
    if not smt_server_data:
        range_matches_map = find_longest_prefix_ipv4(
            requester,
            ip_range_to_smt_data_map
        )
        ip_addr = ipaddress.ip_address(requester)
        for ip_range, smt_data in range_matches_map.items():
            net = ipaddress.ip_network(ip_range)
            if ip_addr in net:
                smt_server_data = smt_data
                break
    if not smt_server_data:
        logging.info('\tDenied')
        return 'Not found', 404
    smt_ip_data, smt_name_data, smt_fingerprint_data = smt_server_data
    smt_ips = smt_ip_data.split(',')
    num_smt_ips = len(smt_ips)
    smt_names = smt_name_data.split(',')
    num_smt_names = len(smt_names)
    smt_cert_fingerprints = smt_fingerprint_data.split(',')
    num_smt_fingerprints = len(smt_cert_fingerprints)
    smt_info_xml = '<regionSMTdata>'
    # Randomize the order of the SMT server information provided to the client
    while num_smt_ips:
        entry = random.randint(0, num_smt_ips-1)
        smt_ip = smt_ips[entry]
        del(smt_ips[entry])
        if num_smt_names > 1:
            smt_name = smt_names[entry]
            del(smt_names[entry])
        else:
            smt_name = smt_names[0]
        if num_smt_fingerprints > 1:
            smt_fingerprint = smt_cert_fingerprints[entry]
            del(smt_cert_fingerprints[entry])
        else:
            smt_fingerprint = smt_cert_fingerprints[0]
        num_smt_ips -= 1
        smt_info_xml += '<smtInfo SMTserverIP="%s" ' % smt_ip
        smt_info_xml += 'SMTserverName="%s" ' % smt_name
        smt_info_xml += 'fingerprint="%s"/>' % smt_fingerprint
    smt_info_xml += '</regionSMTdata>'

    logging.info('Provided: %s' % smt_info_xml)
    return smt_info_xml, 200


# Run the service
if __name__ == '__main__':
    app.run(debug=True)
