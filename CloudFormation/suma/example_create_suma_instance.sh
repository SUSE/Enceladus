#!/bin/sh 

REGION="eu-west-1"
STACK_NAME="suma-test"
CONFIG='
[
{
  "ParameterKey": "KeyName",
  "ParameterValue": "MY_EU_WEST_KEY"
},
{
  "ParameterKey": "SecurityGroups",
  "ParameterValue": "MY_SECURITY_GROUP"
},
{
  "ParameterKey": "ServerInstanceType",
  "ParameterValue": "m4.large"
},
{
  "ParameterKey": "VolumeSize",
  "ParameterValue": "15"
},
{
  "ParameterKey": "ManagerPassword",
  "ParameterValue": "admin123"
},
{
  "ParameterKey": "ManagerAdminEMail",
  "ParameterValue": "MY_EMAIL_ADDRESS"
},
{
  "ParameterKey": "ManagerPassword",
  "ParameterValue": "admin123"
},
{
  "ParameterKey": "SCCUser",
  "ParameterValue": "MY_SCC_ACCOUNT"
},
{
  "ParameterKey": "SCCPassword",
  "ParameterValue": "MY_SCC_PASSWORD"
},
{
  "ParameterKey": "RegEMail",
  "ParameterValue": "MY_REGISTRATION_EMAIL"
},
{
  "ParameterKey": "RegCode",
  "ParameterValue": "MY_SUMA_REGISTRATION_CODE"
},
{
  "ParameterKey": "UpdateSystem",
  "ParameterValue": "1"
},
{
  "ParameterKey": "ProductList",
  "ParameterValue": "sles12sp1"
},
{
  "ParameterKey": "CertOrg",
  "ParameterValue": "MY_ORGANISATION"
},
{
  "ParameterKey": "CertOrgUnit",
  "ParameterValue": "MY_UNIT"
},
{
  "ParameterKey": "CertCity",
  "ParameterValue": "MY_CITY"
},
{
  "ParameterKey": "CertState",
  "ParameterValue": "MY_STATE"
},
{
  "ParameterKey": "CertCountry",
  "ParameterValue": "DE"
},
{
  "ParameterKey": "CertEMail",
  "ParameterValue": "MY_CERTFICATE_ADMIN_EMAIL"
},
{
  "ParameterKey": "CertPassword",
  "ParameterValue": "cert123"
},
{
  "ParameterKey": "ActivationKeyName",
  "ParameterValue": "1-test_key"
},
{
  "ParameterKey": "ActivationKeyDescription",
  "ParameterValue": "Test Key"
}
]'


aws --region $REGION cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://$HOME/Enceladus/CloudFormation/suma/suse_manager_full_bootstrap.templ \
  --parameters "$CONFIG"
