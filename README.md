Enceladus
=========

A collection of code and documentation related to Public Cloud. Some of
the code is SUSE specific while other code is generic and useful for anyone.
Each directory represents a "project" onto it's own containing a README file
explaining the details of the code developed in that directory.

# azuremetadata

A tool to collect metadata in a Microsoft Azure instance

# ec2utils

A collection of utilities useful for interacting with Amazon EC2

# gcemetadata

A tool to collect metadata in a Google Compute Engine instance

# monitoring

Plugins for Nagios/Icinga used to monitor the SUSE update infrastructure
in the Public CLoud covering cases for which we could not find already
developed plugins

# regionServiceClient

The client for the SUSE Linux Enterprise Specific update infrastructure. The
client is used in all SUSE released on demand images and is recommended for
any Cloud Service Provider that is interested in providing SUSE Linux
Enterprise in their Public Cloud offering.

# susePublicCloudInfoClient

The client using the REST API of the SUSE Public Cloud Information Service.
The SUSE Public Cloud Information Service provides information about
images released by SUSE and servers operated and maintained by SUSE in the
Public Cloud.

## Contributing

With ssh keys being widely available and the increasing compute power available
to many people refactoring of SSH keys is in the range of possibilities.
Therefore SSH keys as used by GitHub as a "login/authentication" mechanism no
longer provide the security they once did. See
http://cryptosense.com/batch-gcding-github-ssh-keys/ and
https://blog.benjojo.co.uk/post/auditing-github-users-keys as reference. In an
effort to ensure the integrity of the repository and the code base patches
sent for inclusion must be GPG signed. Follow the instructions below to
let git sign your commits.

1. Create a key suitable for signing (its not recommended to use
   existing keys to not mix it up with your email environment etc):

$ gpg --gen-key

Choose a DSA key (3) with a keysize of 2048 bits (default) and
a validation of 3 years (3y). Enter your name/email and gpg
will generate a DSA key for you:

[...]
pub   2048D/11223344 2014-08-04 [expires: 2017-08-04]
      Key fingerprint = 1234 5678 9abc 1234 5678  9abc 1234 5678 1234 5678
uid                  Joe Developer <developer@foo.bar>



You can also choose to use an empty passphrase, despite GPG's warning,
because you are only going to sign your public git commits with it and
dont need it for protecting any of your secrets. That might ease later
use if you are not using an gpg-agent that caches your passphrase between
multiple signed git commits.

2. Add the key ID to your git config

In above case, the ID is 11223344 so you add it to either your global
~/.gitconfig or even better to your .git/config inside your repo:

...
[user]
       name = Joe Developer
       email = developer@foo.bar
       signingkey = 11223344

and thats basically it.

3. Signing your commits

In future when committing something, just use "git commit -S -a" rather
than "git commit -a". The signatures created by this can later be
verified using "git log --show-signature".
