# Copyright (c) $2014, SUSE LLC, All rights reserved.
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

import logging
import requests

def generateRegionSrvArgs():
    """
    Generate arguments to be sent to the region server.
    """
    metaDataUrl = 'http://169.254.169.254/computeMetadata/v1/'
    zoneInfo = 'instance/zone'
    headers = { 'Metadata-Flavor' : 'Google' }

    zoneResp = requests.get(metaDataUrl + zoneInfo, headers=headers)

    if zoneResp.status_code == 200:
        try:
            country, region, zone = zoneResp.text.split('/')[-1].split('-')
        except:
            logging.warning('Unable to form region string from text: %s'
                            %zoneResp.text)
            return
    else:
        logging.warning('Unable to get zone metadata')
        logging.warning('\tReturn code: %d' %zoneResp.status_code)
        logging.warning('\tMessage: %s' %zoneResp.text)
        return

    return 'regionHint=' + country + '-' + region
