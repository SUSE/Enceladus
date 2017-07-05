SUSE Manager 3.1 Templates
==========================

This directory contains example templates for creating SUSE Manager 3.1 Server
and SUSE Manager 3.1 Proxy instances.

### `suse_manager_base_storage_setup.templ`

Sample template for bootstrapping a SUSE Manager 3.1 Server instance with
external EBS storage, which gets prepared on instance initialization for SUSE
Manager use.

### `suse_manager.templ`

This template can be used to fully bootstrap a SUSE Manager 3.1 Server instance
including EBS storage setup, product registration for updates, certificate
creation, registration with SCC for SUSE Manager entitlements, activation key
creation, bootstrap script generation, and optionally synchronizing channels
and creating bootstrap repositories. Most configuration parameters in the
script should be self-explanatory. The parameter `ProductList` may hold a comma
separated list of channels to sync. The values `sles12sp2`, `sles12sp1`,
`sles12`, and `sles11sp4` have a special meaning. They will be expanded to the
corresponding pool, updates, manager-tools pool, and manager-tools updates
channels (`x86_64`). If you set the parameter to an empty string, no channels
will be synchronized.

Please note that setting up SUSE Manager 3.1 Server takes a while, especially
synchronizing channels. You can inspect `/var/log/cloud-init-output.log` on the
server to see whether SUSE Manager Server initialization has been completed,
and if you configured any channels to be synchronized, you will find the
according log in `/var/log/populate_channels.log`.

### `suse_manager_proxy.templ`

This template can be used to bootstrap a SUSE Manager 3.1 Proxy instance. This
template also sets up external EBS storage and creates an SSL certificate. It
accepts the host name of the parent server (either a SUSE Manager Server or
another proxy), and it uses this information to generate an answer file that
can be used with the `configure-proxy.sh` script. It tries to fetch and run
`/pub/boostrap/bootstrap-proxy.sh` from the parent server to register itself,
assuimg that you have generated a bootstrap-proxy.sh on the server, using an
activation key that enables at least provisioning support. If there is no
suitable `bootstrap-proxy.sh` this step will fail and you will have to manually
register your SUSE Manager 3.1 Proxy instance with the server. Please note that
at the time of writing, SUSE Manager 3.1 Proxy does not support to be managed
as a salt minion, so bootstrap-proxy.sh needs to be generated using the
`--traditional` parameter when calling `mgr-bootstrap`.

Regardless of this, the template does not fully bootstrap the SUSE Manager
Proxy instance. To finalize the setup, you need to  peform the following manual
steps:

1. Log into the SUSE Manager Proxy instance and become root (e.g. `sudo su -`).
2. If necessary (see above), run the bootstrap script from the SUSE Manager
   Server (e.g. `curl -Sks
   https://MY_SUSE_MANAGER_SERVER/pub/bootstrap/bootstrap-proxy.sh | /bin/bash`).
3. Copy the certificate files from the SUSE Manager Server (e.g. `cd /root;
   mkdir ssl-build;
   scp MY_SUSE_MANAGER_SERVER:/root/ssl-build/{RHN-ORG-PRIVATE-SSL-KEY,RHN-ORG-TRUSTED-SSL-CERT,rhn-ca-openssl.cnf} ssl-build`)
4. Run `configure-proxy.sh --answer-file /root/proxy-conf` (this will ask you
   for a certificate password; this is the one from the server certificate).
 
Your SUSE Manager 3.1 Proxy instance should now be ready. You may want to
create bootstrap scripts using `mgr-bootstrap` to allow clients to bootstrap
from your SUSE Manager 3.1 Proxy.

### `example_create_suma_instance.sh`

Example command line script to create a SUSE Manager 3.1 Server CloudFormation
stack. Adjust the configuration parameters to your needs and the template body
file location, if necessary.

### `example_create_suma_proxy_instance.sh`

Ditto for SUSE Manager 3.1 Proxy.

### `manager_populate_channels.sh`

This script is used by `suse_manager_full_bootstrap.templ` to synchronize
channels. It is available from an S3 bucket where the template will try to
fetch it from, so unless you want to change channel synchronization, you don't
need this file.
