SUSE SMT VPC Templates
======================

This directory contains example templates for creating new VPCs with or
configuring existing VPCs for access to SUSE SMT update infrastructure. 

### `configure_subnet_for_suse_smt.templ`

This template configures an existing subnet in a VPC for access to the SMT
servers. It takes the following parameters:

- VPCId: ID of existing VPC
- SMTSubnetId: ID of existing subnet in VPC to open up for SUSE SMT service
- PubSubnetId: ID of existing subnet to crate NAT gateway in
- UpdateInfraType: Update infrastructure type to open VPC up to (SLES or SMT)

### `configure_subnet_with_nat_for_suse_smt.templ`

Does the same as the template above, except that an existing NAT router is
used. It takes the following parameters:

- VPCId: ID of existing VPC
- SMTSubnetId: ID of existing subnet in VPC to open up for SUSE SMT service
- VPCNatGateway: ID of existing NAT gateway in VPC
- UpdateInfraType: Update infrastructure type to open VPC up to (SLES, SMT, or
  both)

### `create_subnet_for_suse_smt.templ`

This template can be used to create a new subnet in an existing VPC and
configures it for access to SUSE SMT servers. It uses an existing NAT gateway
for internet access. It takes the following parameters:

- VPCId: ID of existing VPC
- VPCNatGateway: ID of existing NAT gateway in VPC
- PrivateSubnetCidrBlock: IP block for the private subnet to create with SUSE
  SMT access
- UpdateInfraType: Update infrastructure type to open VPC up to (SLES, SMT, or
  both)

### `create_vpc_for_suse_smt.templ`

Creates a new VPC, and within the VPC a public subnet for the NAT gateway and
a private subnet with access to the SUSE SMT update infrastructure. It takes
the following parameters:

- VPCCidrBlock: IP block for the newly created VPC
- PublicSubnetCidrBlock: IP block for the public subnet
- PrivateSubnetCidrBlock: IP block for the private subnet
- UpdateInfraType: Update infrastructure type to open VPC up to (SLES, SMT, or
  both)

### `update_smt_mappings.sh`

This script reads any of the template files and updates the `Mappings` block
with the IP addresses retrieved from SUSE Public Cloud Information service,
and writes the updated template to stdout.
