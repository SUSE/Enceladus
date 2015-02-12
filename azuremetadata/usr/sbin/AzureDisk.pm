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
package AzureDisk;

use strict;
use warnings;

use POSIX;

our @ISA    = qw (Exporter);
our @EXPORT_OK = qw (
    getVHDDiskTag
);

sub getVHDDiskTag {
    my $file = shift;
    my $fh;
    my $read_bytes;
    my $junk;
    my $result;
    my $done;
    if (! sysopen($fh,$file, O_RDONLY)) {
        die "open file $file failed: $!"
    }
    # Read the tag at 64K boundary
    seek $fh,65536,0;
    $read_bytes = sysread ($fh, $done, 4);
    if ($read_bytes != 4) {
        die "sysread failed, want 4 bytes got $read_bytes"
    }
    $junk = unpack 'l',  $done;
    $junk = pack   'l>', $junk;
    $junk = unpack 'H*', $junk;
    $result = "$junk-";
    $read_bytes = sysread ($fh, $done, 2);
    if ($read_bytes != 2) {
        die "sysread failed, want 2 bytes got $read_bytes"
    }
    $junk = unpack 'S',  $done;
    $junk = pack   'S>', $junk;
    $junk = unpack 'H*', $junk;
    $result.= "$junk-";
    $read_bytes = sysread ($fh, $done, 2);
    if ($read_bytes != 2) {
        die "sysread failed, want 2 bytes got $read_bytes"
    }
    $junk = unpack 'S',  $done;
    $junk = pack   'S>', $junk;
    $junk = unpack 'H*', $junk;
    $result.= "$junk-";
    $read_bytes = sysread ($fh, $done, 2);
    if ($read_bytes != 2) {
        die "sysread failed, want 2 bytes got $read_bytes"
    }
    $junk = unpack 'H*', $done;
    $result.= "$junk-";
    $read_bytes = sysread ($fh, $done, 6);
    if ($read_bytes != 6) {
        die "sysread failed, want 6 bytes got $read_bytes"
    }
    $junk = unpack 'H*', $done;
    $result.= $junk;
    close $fh;
    return $result;
}

1;
