ec2metadata
===========

Introduction
------------

ec2metadata is a command line utility to collect meta data available in an
Amazon Web Services Elastic Compute Cloud (EC2) guest instance. The meta
data is provided via http API at the "magic" 169.254.169.254 IP address.
Available data is documented by Amazon (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html). The command line utility gets
the requested information and by default writes the data to standard output.
The data can optionally be represented as XML snippets and/or be written to
a file.

Installation
------------

Use the standard "python setup.py install" process.

Background
----------

The code base was merged into this project from a fork that originated
from a project started by Alon Swartz at TurnKey. The original
[upstream project](https://github.com/turnkeylinux/ec2metadata) did not
respond to, or accept pull requests. Therefore, it was assumed that the
maintainer had no interest in moving the code base forward to meet other
needs.

The initial fork was maintained in https://github.com/rjschwei but has been
removed as the code base will now be maintained as part of this project.


Note
----

Must remain Python 2 based until EOL of SLES 11 in March 2019
