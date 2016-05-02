Region Service
==============

The Region Service is a REST service that integrates with Apache. It will
provide information about SMT Servers in a cloud environment based on
region hint or the IP address of the client requesting the information.

The service is implemented in Python using the [Flask microframework](http://flask.pocoo.org).

The service works with 2 configuration files:

- the configuration file for the service itself
  `/etc/regionService/regionInfo.cfg`
- the configuration of the region SMT Server information
  `/etc/regionService/regionData.cfg`

Pretty much everything is configurable or changeable via command line options.

The service builds a large map of all possible IP addresses, thus it may
require a lot of memory, depending on the IP ranges that need to be serviced.

The SMT Server info is returned as an XML string.

To integrate the code into a cloud VM that serves as regionInfo server one
must substitude the _SUBSTITUTE_WITH_CLOUD_SPECIFIC_NAME_ string with the
real hostname or the static IP address in

`/etc/apache2/vhosts.d/regionsrv_vhost.conf`

which happens automatically when running the certificate generation code.


/usr/sbin/genRegionServerCert --help

provides information about the expected arguments. The service is intended to
be accessible via https only and thus a certificate needs to be created. Use
the .pem file generated in `/root/regionServCert` and add it in the client
(Cloud Guest VM) in `/var/lib/regionService/certs`. The
_genRegionServerCert_ generates a self signed certificate, thus the .pem file
must be included in the client or the client VM will not be able to connect.


The WSGI daemon process is restricted to not run as root, thus a regionsrv
user and group is assigned in the `regionsrv_vhost.conf` file for the process.

The service is generic and can be used for all cloud environments.

Notable::
The Wsgi application is not executed when Apache starts, execution of the
application occurs when the first request is received.

Tradeoffs::
I decided to use a large memory footprint, i.e. store all IP adresses in
a map rather than doing calculation on the fly when requests arrive. Caching
all IP addresses speeds up the response and reduces code complexity at
the expense of memory usage.
