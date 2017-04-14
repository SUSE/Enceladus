# ec2utils

A collection of utilities that makes managing images in Amazon EC2 easier.
All utilities utilize the same configuration file, ~/.ec2utils.conf that
contains account and region configuration options.

## ec2deprecateimg

A command line utility to deprecate images in Amazon EC2. The platform does
not support a formal deprecation mechanism. The mechansim implemented by
this tool is a convention. Unfortunately the tags are not sticky, i.e. not
visible to others if the image is shared.

Images are tagged with:

- Deprecated on     -> today's date in YYYYMMDD format
- Removal date      -> today's date plus the deprecation period specified
- Replacement image -> The AMI ID and name of the replacement image

## ec2publishimg

A command line utility to control the visibility of an image in AWS EC2.
The tool supports setting an image to public or private.

## ec2uploadimg

A command line utility to upload a compressed raw image file, as created
by KIWI for example to Amazon EC2 and create a snapshot or register an EBS
backed AMI.
