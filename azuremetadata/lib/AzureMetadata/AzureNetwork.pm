#Copyright (C) 2015 SUSE LLC
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

package AzureNetwork;

use strict;
use XML::LibXML;
use FileHandle;

our @ISA    = qw (Exporter);
our @EXPORT_OK = qw (
    get_cloudservice_name
    import_config
    read_internal_ip
    read_external_ip
);

sub get_cloudservice_name {
    my $xml = shift;
    my @services = $xml->getElementsByTagName('Service');
    my $serviceName = $services[0]->getAttribute('name');
    $serviceName .= '.cloudapp.net';
    return $serviceName;
}

sub import_config {
    my $config_file = shift;
    if (! $config_file) {
        $config_file = '/var/lib/waagent/SharedConfig.xml';
    }
    my $handle = FileHandle->new();
    if (! $handle->open($config_file)) {
        die "Can't open file $config_file: $!";
    }
    binmode $handle;
    my $libxml = XML::LibXML->new();
    return $libxml->parse_fh($handle);
}

sub read_internal_ip {
    my $xml = shift;
    my $metadata = __read_instance_node($xml);
    if (! $metadata) {
        return;
    }
    return $metadata->getAttribute('address');
}

sub read_external_ip {
    my $xml = shift;
    my $metadata = __read_instance_node($xml);
    my $endpoints = $metadata->getElementsByTagName('Endpoint');
    my $address;
    for (my $i=1;$i<= $endpoints->size();$i++) {
        my $endpoint = $endpoints->get_node($i);
        my $name = $endpoint->getAttribute('name');
        if ($name eq 'SSH') {
            $address = $endpoint->getAttribute('loadBalancedPublicAddress');
            if ($address =~ /(.*):.*/) {
                $address = $1;
            }
            return $address;
        }
    }
    return $address;
}

sub __read_instance_node {
    my $xml = shift;
    my $instances = $xml->getElementsByTagName('Instance');
    return $instances->get_node(1);
}

1;
