azure-bond-autoconf
===================

**azure-bond-autoconf** is a colllection of scripts for automatically setting
up interface bonding in Microsoft Azure on SUSE Linux Enterprise or openSUSE
virtual machines that use Accelerated Networking. Accelerated Networking in
Azure enables single root I/O virtualization, which improves network
performance.

Accelerated Network interfaces in Azure show up in pairs in the virtual
machine. One is the single root I/O interface, the other one a standard virtual
network interface. Those can be bonded together, using the accelerated one as
the active slave, and the standard one as backup.

### Installation

If installing from source, just run `make install` as root.
After that, **azure-bond-autoconf** will automatically set up bonding for
Accelerated Network interfaces when the system is booted.

### Configuration

**azure-bond-autoconf** does not require any configuration. It automatically
creates a bonding configuration for any suitable interface it detects. The
configuration uses DHCP and has support enabled for **cloud-netconfig**, a
different set of scripts that can apply secondary IP addresses to interfaces
and add routing policies automatically. You can modify the bonding master
configuration `/etc/sysconfig/network/ifcfg-bondX` (replace `X` accordingly) if
you require a different configuration. Set the variable
**AZURE__BOND__AUTOCONF** to **no** in that case, otherwise the configuration
will be overwritten at boot time.
