# serviceAccessConfig


## History

The origin of the project lies in the need for the SUSE operated update
infrastructure in the Public Cloud to be access restricted based on the
IP addresses a cloud frame work hands out. The CIDR blocks the frameworks
hand out is not static and thus having to edit many configuration files
is not a feasibility when one strives to have a always functioning service.

The code started out to be specialized to update an Apache configuration
file or an HAProxy configuration file and was maintained in a private
repository. While implementing changes to handle differences between
Apache 2.2 and 2.4 it was decided to generalize the code such that any
service that provides some method of restricting access via a configuration
file could be handled.

## Functionality

The implementation uses the /etc/serviceaccess/srvAccess.cfg file to
determine the configuration files to modify. The configuration is
in INI style as follows:

```
[accessservice]
logFile = /var/log/serviceAccess/srvAccess.log
ipdata = FILE_TO_MONITOR_IN_REGION_SRV_FORMAT

[SERVICE_NAME_MUST_MATCH_A_PLUGIN_IMPLEMENTATION]
request = URL_TO_MAKE_REQUEST_AFTER_SERVICE_RESTART
serviceConfig = CONFIG_FILE_TO_MODIFY
serviceName = THE_NAME_OF_THE_SERVICE_FOR_RESTART
updateInterval = UPDATE_INTERVAL_IN_MINUTES
```
The "accessservice" section specifies general configuration options.

* *logFile* => Specify the location of the log file
* *ipdata* => This file is also in INI format and is monitored for changes

Any additional sections specify configurations for specific services, such
as **apache** or **haproxy**. For each named section a plugin must be
implemented that knows how to handle the configuration file of the specific
service. For example a setup for **haproxy** would look as follows

```
[haproxy]
serviceConfig = /etc/haproxy.cfg
updateInterval = 5
```

The options considered have the following effect:

* *request* => If provided the given URL will be used to issue a request. This
             is useful if the service at the address needs to preload data and
             thus can shorten the time the first user has to wait when
             accessing the service.
* *serviceConfig* => The configuration file the service uses that should be
                   modified
* *serviceName* => The name of the service to be restarted, i.e. the sysVinit
                 script or the systemd unit file that starts/restarts the
                 service. If not specified the section name is assumed to be
                 the service name.
* *updateInterval* => The time in minutes when the file configured with the
                    *ipdata* option should be checked for changes


The file configured with the *ipdata* option is also in INI format as
follows:

```
[ANY_TO_YOU_MEANINGFUL_SECTION_NAME]
public-ips = A_COMMA_SEPARATED_LIST_OF_CIDR_BLOCKS
```

The code will collect all CIDR blocks in all sections and use the information
to generate the the access rules appropriate for the service being managed.

## Contributing

Any submissions need to be accompanied by a test.

Code needs to be pep8 clean

### Implementing plugins

Plugin names are linked by name to section names in the configuration file.
For example the plugin for Apache is named "apache.py" and the expected
section in the configuration file is named "[apache]". The class name of the
plugin is also linked to the section name in that the class name always starts
with "ServiceAccessGenerator" followed by the section name with a capitalized
first letter, i.e. for Apache the class names is "ServiceAccessGeneratorApache".
The generator class must inherit from "ServiceAccessGenerator" and must
implement the "_update_service_config()" method.

### Signing GIT Patches

With ssh keys being widely available and the increasing compute power available
to many people refactoring of SSH keys is in the range of possibilities.
Therefore SSH keys as used by GitHub as a 'login/authentication' mechanism no
longer provide the security they once did. See
[github ssh keys](http://cryptosense.com/batch-gcding-github-ssh-keys) and
[github users keys](https://blog.benjojo.co.uk/post/auditing-github-users-keys)
as reference. In an effort to ensure the integrity of the repository and the
code base patches sent for inclusion must be GPG signed. Follow the
instructions below to let git sign your commits.

1. Create a key suitable for signing (its not recommended to use
   existing keys to not mix it up with your email environment etc):

   ```
   $ gpg --gen-key
   ```

   Choose a DSA key (3) with a keysize of 2048 bits (default) and
   a validation of 3 years (3y). Enter your name/email and gpg
   will generate a DSA key for you:

   You can also choose to use an empty passphrase, despite GPG's warning,
   because you are only going to sign your public git commits with it and
   dont need it for protecting any of your secrets. That might ease later
   use if you are not using an gpg-agent that caches your passphrase between
   multiple signed git commits.

2. Add the key ID to your git config

   In above case, the ID is 11223344 so you add it to either your global
   __~/.gitconfig__ or even better to your __.git/config__ inside your
   repo:

   ```
   [user]
       name = Joe Developer
       email = developer@foo.bar
       signingkey = 11223344
   ```

   That's basically it.

3. Signing your commits

   Instead of 'git commit -a' use the following command to sign your commit

   ```
   $ git commit -S -a
   ```

4. Show signatures of the commit history

   The signatures created by this can later be verified using the following
   command:

   ```
   $ git log --show-signature
   ```

## Issues

We track issues (bugs and feature requests) in the GitHub Issue tracker.
