# ec2publishimg

A command line utility to control the visibility of an image in AWS EC2.
The tool supports setting an image to public or private.

## Description

Sets the visibility of an AMI to allow others to use the
image or to make the image private, i.e. only available to the account
owner.

## Installation

### openSUSE and SUSE Linux Enterprise

```
zypper in python-ec2publishimg
```

## Usage

```
ec2publishimg --account example --image-name-match production-v2 --share-with all
```

See the [man page](man/man1/ec2publishimg.1) for more information.

```
man ec2publishimg
```
