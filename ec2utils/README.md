ec2utils
========

A collection of utilities that makes managing images in Amazon EC2 easier.
All utilities utilize the same configuration file, ~/.ec2utils.conf that
contains account and region configuration options.

# ec2deprecateimg

A tool to deprecate images. Images are tagged with:
- Deprecated on     -> today's date in YYYYMMDD format
- Removal date      -> today's date plus the deprecation period specified
- Replacement image -> The AMI ID and name of the replacement image

# ec2publishimg

A tool to set an image to public or private

# ec2uploadimg

A tool to upload a compressed raw file and create an ECS back AMI
