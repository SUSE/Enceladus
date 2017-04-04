# -*- coding: utf-8 -*-

""""Mocked responses for AWS endpoints."""

from datetime import datetime, timezone


def get_time_now():
    """Return the time as a datetime object and string."""
    now = datetime.now(timezone.utc)
    now_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return now, now_str


def response_metadata(now_str):
    """Return the default metadata response."""
    metadata = {
        'ResponseMetadata':
            {'RequestId': '2614a68d-ada7-11e6-8c37-b3baab09bf37',
             'HTTPStatusCode': 200,
             'RetryAttempts': 0,
             'HTTPHeaders':
                 {'content-length': '450',
                  'content-type': 'text/xml',
                  'date': now_str,
                  'x-amzn-requestid': '2614a68d-ada7-11e6-8c37-b3baab09bf37'
                  }
             }
    }
    return metadata


def access_key_response(access_key):
    """Response for create/get access key."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['AccessKey'] = {
        'Status': access_key.status,
        'AccessKeyId': access_key.id,
        'UserName': access_key.username,
        'SecretAccessKey': access_key.key
    }
    return parsed_response


def access_key_last_used_response(access_key):
    """Response for create/get access key."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['AccessKeyLastUsed'] = {
        'Region': access_key.last_used.region,
        'LastUsedDate': access_key.last_used.date,
        'ServiceName': access_key.last_used.service_name
    }
    parsed_response['UserName'] = access_key.username
    return parsed_response


def create_policy_response(policy):
    """Response for create policy."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['Policy'] = {
        'PolicyName': policy.name,
        'DefaultVersionId': policy.default_version_id,
        'PolicyId': policy.id,
        'Path': policy.path,
        'Arn': policy.arn,
        'AttachmentCount': policy.attachment_count,
        'CreateDate': policy.create_date,
        'UpdateDate': policy.update_date
    }
    return parsed_response


def generic_response():
    """Generic response for deletion endpoints."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    return parsed_response


def get_user_policy_response(policy, username):
    """Response for get attached policy for user endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['UserName'] = username
    parsed_response['PolicyName'] = policy.name
    parsed_response['PolicyDocument'] = policy.document
    return parsed_response


def group_response(group):
    """Response for create/get group."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['Group'] = {
        'GroupId': group.id,
        'GroupName': group.name,
        'Arn': group.arn,
        'Path': group.path
    }
    return parsed_response


def list_access_keys_response(keys):
    """Response for list user access keys endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    keys_response = [{'Status': access_key.status,
                      'AccessKeyId': access_key.id,
                      'UserName': access_key.username
                      } for key, access_key in keys.items()]
    parsed_response['AccessKeyMetadata'] = keys_response
    return parsed_response


def list_attached_user_policies_response(policies):
    """Response for list user attached policies endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    policies_response = [
        {'PolicyArn': policy.arn,
         'PolicyName': policy.name
         } for policy in policies]
    parsed_response['AttachedPolicies'] = policies_response
    return parsed_response


def list_groups_response(groups):
    """Response for list groups"""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    groups_response = [{
        'GroupId': group.id,
        'GroupName': group.name,
        'Arn': 'arn:aws:iam::123456789123:group/openbare/%s' % group.name,
        'Path': '/openbare/',
    } for key, group in groups.items()]
    parsed_response['Groups'] = groups_response
    return parsed_response


def list_groups_for_user_response(groups):
    """Response for list user groups."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    groups_response = [{'Path': '/openbare/',
                        'Arn': 'arn:aws:iam::123456789012:group/%s' % group.id,
                        'GroupName': group.name,
                        'GroupId': group.id} for group in groups]
    parsed_response['Groups'] = groups_response
    return parsed_response


def list_mfa_devices_response(username, devices):
    """Response for list user MFA Devices endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    devices_response = [
        {'SerialNumber': device.serial_number,
         'UserName': username
         } for key, device in devices.items()]
    parsed_response['MFADevices'] = devices_response
    return parsed_response


def list_signing_certs_response(username, certs):
    """Response for list user signing certificates."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    certs_response = [
        {'UserName': username,
         'CertificateId': cert.id,
         'CertificateBody': cert.body,
         'Status': cert.status
         } for key, cert in certs.items()]
    parsed_response['Certificates'] = certs_response
    return parsed_response


def list_users_response(users):
    """Response for list users"""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    users_response = [{
        'UserId': user.id,
        'CreateDate': user.create_date,
        'UserName': user.username,
        'Arn': 'arn:aws:iam::123456789123:user/openbare/%s' % user.username,
        'Path': '/openbare/',
        'PasswordLastUsed': user.password_last_used
    } for key, user in users.items()]
    parsed_response['Users'] = users_response
    return parsed_response


def login_profile_response(user, create=False):
    """Response for list user login profiles."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['LoginProfile'] = {
        'CreateDate': user.login_profile.create_date,
        'UserName': user.username
    }

    if create:
        parsed_response['LoginProfile']['PasswordResetRequired'] = \
            user.login_profile.reset_required
    return parsed_response


def upload_signing_certificate_response(username, cert):
    """Response for upload signing certificate."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['Certificate'] = {
        'UserName': username,
        'CertificateId': cert.id,
        'CertificateBody': cert.body,
        'Status': cert.status
    }
    return parsed_response


def user_response(username):
    """Response for create/get user."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['User'] = {
        'UserId': 'AIDAJKBPJ3KLDYBUV64DE',
        'CreateDate': now,
        'UserName': username,
        'Arn': 'arn:aws:iam::123456789123:user/openbare/%s' % username,
        'Path': '/openbare/'
    }
    return parsed_response


def user_group_response():
    """Response for add user to group."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    return parsed_response
