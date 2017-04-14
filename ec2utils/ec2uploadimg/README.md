# ec2uploadimg

A command line utility to upload a compressed raw image file, as created by
KIWI for example to Amazon EC2 and create a snapshot or register an EBS
backed AMI.

## Description

Uploads a compressed raw image to Amazon EC2 using an
existing EC2 AMI and creates a snapshot or registers a new AMI from the
image. The apparent size of the raw image is recommended to be 10 GB or
less. It is expected that the raw image has 1 partition, i.e. the root
partition is _/dev/sda1._ The process of creating the image is as
follows:

* Start an instance
* Create a storage volume and attach it to the running instance
* Create volume that will be the new root and attach it to the running 
  instance
* Upload the image
* Unpack the image and dump it to the new root volume
* Detach the new root volume and create a snapshot
* Register a new AMI
* Clean up

## Installation

### openSUSE and SUSE Linux Enterprise

```
zypper in python-ec2uploadimg
```

## Usage

```
ec2uploadimg --account example -d "My first image" -m x86_64 -n my_linux_image -r us-east-1 PATH_TO_COMPRESSED_FILE
```

See the [man page](man/man1/ec2uploadimg.1) for more information.

```
man ec2uploadimg
```
