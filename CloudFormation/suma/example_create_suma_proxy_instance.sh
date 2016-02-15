#!/bin/sh 

REGION="eu-west-1"
STACK_NAME="suma-proxy"
CONFIG='
[
{
  "ParameterKey": "KeyName",
  "ParameterValue": "MY_AWS_KEY"
},
{
  "ParameterKey": "SecurityGroups",
  "ParameterValue": "MY_SECURITY_GROUP"
},
{
  "ParameterKey": "ServerInstanceType",
  "ParameterValue": "t2.medium"
},
{
  "ParameterKey": "VolumeSize",
  "ParameterValue": "15"
},
{
  "ParameterKey": "TracebackEMail",
  "ParameterValue": "MY_EMAIL"
},
{
  "ParameterKey": "ParentServer",
  "ParameterValue": "MY_SUSE_MANAGER_SERVER"
},
{
  "ParameterKey": "CertOrg",
  "ParameterValue": "MY_ORGANIZATION"
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
  "ParameterValue": "MY_CERTIFICATE_EMAIL"
},
{
  "ParameterKey": "CertPassword",
  "ParameterValue": "MY_CERTIFICATE_PASSWORD"
}
]'


aws --region $REGION cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://$HOME/Enceladus/CloudFormation/suma/suse_manager_proxy.templ \
  --parameters "$CONFIG"
