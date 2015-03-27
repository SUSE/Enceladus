ec2metadata
===========

Introduction
------------

ec2metadata is a command line utility to collect meta data available in an
Amazon Web Services Elastic Compute Cloud (EC2). The meta data is provided
via http API at the "magic" 169.254.169.254 IP address. Available data is
documented by Amazon (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html). The command line utility gets the requested
information and by default writes the data to standard output. The data can
optionally be represented as XML snippets.

Installation
------------

Use the standard "python setup.py install" process.

Background
----------

This project is a fork of the project originated by Alon Swartz at TurnKey
Linux. After waiting a sufficient time (4 weeks or more) for comments on,
or acceptance of my pull request to the original project I decided that there
was no interest to move the project forward and include the changes I needed.
Therefore, I decided to "ignore" the original upstream project and use this
fork as the master.
