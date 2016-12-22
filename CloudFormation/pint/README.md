Pint templates
==============

### `sles12sp2.templ`

Sample template for creating a SLES12 SP2 instance based on the latest version
as advertised by SUSE Public Cloud Information service. This template only
works in AWS regions that support Lambda. Please note that creating a stack
based on this template requires the capability `AWS::IAM::Role`. When using the
aws cli, add parameter `--capabilites CAPABILITY_IAM` to the `create-stack`
command line.

