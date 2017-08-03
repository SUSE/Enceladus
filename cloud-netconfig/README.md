cloud-netconfig
===============

**cloud-netconfig** is a collection of scripts for automatically configuring
network interfaces in cloud frameworks. Currently support are Amazon EC2 and
Microsoft Azure. It requires netconfig (package **sysconfig-netconfig** on
openSUSE and SUSE Linux Enterprise distributions).

### Installation

If you are installing from source, run as root `make install-ec2` to install on
EC2 or `make install-azure` to install on Azure. Then reload the udev rules by
running `udevadm control -R`. Afterwards add **cloud-netconfig** to the
variable **NETCONFIG__MODULES__ORDER** in `/etc/sysconfig/network/config` and
restart networking (`systemctl restart wicked.serice` on SLE 12 or recent
openSUSE distributions).

### Mode of Operation

With **cloud-netconfig** installed and enabled, for any network interface
detected that does not have a configuration in `/etc/sysconfig/network`, a
configuration will be generated with DHCP (v4 and v6) enabled. Additionally,
for all interfaces including the primary one, **cloud-netconfig** looks up
secondary IPv4 addresses from the metadata server and configures them on the
interface, if any. Secondary IPv6 addresses are delivered via DHCP. For any
seconday interface, routing policies for each IP address will be created to
ensure packets from those get routed via the corresponding network interface.
For IPv6 addresses on the primary interface, routing policies will also be
created to ensure correct routing.

Interface configurations will be checked periodically on each DHCP lease
renewal, and in case the configuration in the cloud framework changed, the
interface will be reconfigured accordingly.

### Configuration

**cloud-netconfig** does not require any configuration, but it should be noted
that it will not overwrite existing interface configurations. This allows to
use specific interface configurations. **cloud-netconfig** will still set up
secondary IP addresses and routing policies. If you do not want that, set the
variable **CLOUD__NETCONFIG__MANAGE** to **no** in the `ifcfg` file in
`/etc/sysconfig/network`.
