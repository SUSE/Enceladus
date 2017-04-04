# -*- coding: utf-8 -*-

""""Mocked endpoints."""

from functools import wraps
from unittest.mock import patch

from mockboto3.core.exceptions import client_error
from mockboto3.core.utils import inflection

from mockboto3.iam import responses
from mockboto3.iam.models import AccessKey, Group, Policy, User
from mockboto3.iam.utils import get_value_from_arn


class MockIAM(object):
    """Class for mocking IAM endpoints."""

    def __init__(self):
        """Initialize class."""
        super(MockIAM, self).__init__()
        self.access_keys = {}
        self.groups = {}
        self.users = {}
        self.policies = {}

    def mock_make_api_call(self, operation_name, kwargs):
        """Entry point for mocking AWS endpoints.

        Calls the mocked AWS operation and returns a parsed
        response.

        If the AWS endpoint is not mocked raise a client error.
        """
        try:
            return getattr(self, inflection(operation_name))(kwargs)
        except AttributeError:
            raise client_error(operation_name,
                               'NoSuchMethod',
                               'Operation not mocked.')

    @staticmethod
    def _access_key_not_found(access_key_id, method):
        raise client_error(method,
                           'NoSuchEntity',
                           'The Access Key with id %s cannot be found.'
                           % access_key_id)

    def _check_group_exists(self, group, method):
        try:
            self.groups[group]
        except KeyError:
            raise client_error(method,
                               'NoSuchEntity',
                               'The group with name %s cannot be found.'
                               % group)

    @staticmethod
    def _check_login_profile_exists(user, method):
        if not user.login_profile:
            raise client_error(method,
                               'NoSuchEntity',
                               'LoginProfile for user with name %s'
                               ' cannot be found.' % user.username)

    def _check_policy_exists(self, policy_name, method):
        try:
            policy = self.policies[policy_name]
        except KeyError:
            raise client_error(method,
                               'NoSuchEntity',
                               'The policy with name %s '
                               'cannot be found.' % policy_name)

        return policy

    def _check_signing_certificate_exists(self, user, cert_id, method):
        try:
            self.users[user].signing_certs[cert_id]
        except KeyError:
            raise client_error(method,
                               'NoSuchEntity',
                               'The signing certificate with certificate id '
                               '%s cannot be found.' % cert_id)

    def _check_user_exists(self, user, method):
        try:
            self.users[user]
        except KeyError:
            raise client_error(method,
                               'NoSuchEntity',
                               'The user with name %s cannot be found.'
                               % user)

    @staticmethod
    def _check_user_has_policy(policy, user, method):
        if policy not in user.attached_policies:
            raise client_error(method,
                               'NoSuchEntity',
                               'The policy with name %s '
                               'is not attached to the user with name '
                               '%s.' % (policy, user.username))

    def add_user_to_group(self, kwargs):
        """Add user to the group if user and group exist."""
        self._check_user_exists(kwargs['UserName'], 'AddUserToGroup')
        self._check_group_exists(kwargs['GroupName'], 'AddUserToGroup')

        user = self.users[kwargs['UserName']]
        group = self.groups[kwargs['GroupName']]

        group.add_user(user.username)
        user.add_group(group.name)
        return responses.user_group_response()

    def attach_user_policy(self, kwargs):
        self._check_user_exists(kwargs['UserName'], 'AttachUserPolicy')
        user = self.users[kwargs['UserName']]

        policy_name = get_value_from_arn(kwargs['PolicyArn'])
        policy = self._check_policy_exists(policy_name, 'AttachUserPolicy')

        user.attach_policy(policy_name)
        policy.attach_user(user.username)
        return responses.generic_response()

    def create_access_key(self, kwargs):
        """Create access key for user if user exists."""
        self._check_user_exists(kwargs['UserName'], 'CreateAccessKey')

        access_key = AccessKey(kwargs['UserName'])
        self.access_keys[access_key.id] = access_key
        return responses.access_key_response(access_key)

    def create_group(self, kwargs):
        """Create group if it does not exist."""
        if kwargs['GroupName'] in self.groups:
            raise client_error('CreateGroup',
                               'EntityAlreadyExists',
                               'Group with name %s already exists.'
                               % kwargs['GroupName'])

        group = Group(kwargs['GroupName'])
        self.groups[group.name] = group
        return responses.group_response(group)

    def create_login_profile(self, kwargs):
        """Create login profile for user if user has no password."""
        self._check_user_exists(kwargs['UserName'], 'CreateLoginProfile')

        user = self.users[kwargs['UserName']]
        if user.login_profile:
            raise client_error('CreateLoginProfile',
                               'EntityAlreadyExists',
                               'LoginProfile for user with name %s '
                               'already exists.' % user.username)

        reset_required = kwargs.get('PasswordResetRequired', None)
        user.create_login_profile(kwargs['Password'],
                                  reset_required=reset_required)
        return responses.login_profile_response(user, create=True)

    def create_policy(self, kwargs):
        """Create policy given policy document."""
        if kwargs['PolicyName'] in self.policies:
            raise client_error('CreatePolicy',
                               'EntityAlreadyExists',
                               'Policy with name %s already'
                               'exists.' % kwargs['PolicyName'])

        policy = Policy(kwargs.get('PolicyName'),
                        kwargs.get('PolicyDocument'),
                        kwargs.get('Description', None),
                        kwargs.get('Path', None))
        self.policies[policy.name] = policy
        return responses.create_policy_response(policy)

    def create_user(self, kwargs):
        """Create user if user does not exist."""
        if kwargs['UserName'] in self.users:
            raise client_error('CreateUser',
                               'EntityAlreadyExists',
                               'User with name %s already exists.'
                               % kwargs['UserName'])

        self.users[kwargs['UserName']] = User(kwargs['UserName'])
        return responses.user_response(kwargs['UserName'])

    def enable_mfa_device(self, kwargs):
        """Enable MFA Device for user."""
        self._check_user_exists(kwargs['UserName'], 'EnableMFADevice')

        user = self.users[kwargs['UserName']]
        if kwargs['SerialNumber'] in user.mfa_devices:
            raise client_error('EnableMFADevice',
                               'EntityAlreadyExists',
                               'Device with serial number %s already '
                               'exists.' % kwargs['SerialNumber'])

        user.enable_mfa_device(kwargs['SerialNumber'])
        return responses.generic_response()

    def deactivate_mfa_device(self, kwargs):
        """Deactivate and detach MFA Device from user if device exists."""
        self._check_user_exists(kwargs['UserName'], 'DeactivateMFADevice')

        user = self.users[kwargs['UserName']]
        if kwargs['SerialNumber'] not in user.mfa_devices:
            raise client_error('DeactivateMFADevice',
                               'NoSuchEntity',
                               'Device with serial number %s cannot '
                               'be found.' % kwargs['SerialNumber'])

        user.deactivate_mfa_device(kwargs['SerialNumber'])
        return responses.generic_response()

    def delete_access_key(self, kwargs):
        """Delete access key if access key exists."""
        try:
            self.access_keys.pop(kwargs['AccessKeyId'])
        except KeyError:
            self._access_key_not_found(kwargs['AccessKeyId'],
                                       'DeleteAccessKey')

        return responses.generic_response()

    def delete_group(self, kwargs):
        """Delete group if group exists."""
        self._check_group_exists(kwargs['GroupName'], 'DeleteGroup')

        for key, user in self.users.items():
            if kwargs['GroupName'] in user.groups:
                user.remove_group(kwargs['GroupName'])

        self.groups.pop(kwargs['GroupName'], None)
        return responses.generic_response()

    def delete_login_profile(self, kwargs):
        """Delete login profile (password) from user if users has password."""
        self._check_user_exists(kwargs['UserName'], 'DeleteLoginProfile')

        user = self.users[kwargs['UserName']]
        self._check_login_profile_exists(user, 'DeleteLoginProfile')

        user.delete_login_profile()
        return responses.generic_response()

    def delete_signing_certificate(self, kwargs):
        """Delete signing cert if cert exists."""
        self._check_user_exists(kwargs['UserName'], 'DeleteSigningCertificate')
        self._check_signing_certificate_exists(kwargs['UserName'],
                                               kwargs['CertificateId'],
                                               'DeleteSigningCertificate')

        user = self.users[kwargs['UserName']]
        user.delete_signing_certificate(kwargs['CertificateId'])
        return responses.generic_response()

    def delete_user(self, kwargs):
        """Delete user if user exists."""
        self._check_user_exists(kwargs['UserName'], 'DeleteUser')

        for group in self.groups:
            if kwargs['UserName'] in group.users:
                group.remove_user(kwargs['UserName'])

        self.users.pop(kwargs['UserName'], None)
        return responses.generic_response()

    def detach_user_policy(self, kwargs):
        """Detach user policy if policy exists."""
        self._check_user_exists(kwargs['UserName'], 'DetachUserPolicy')
        user = self.users[kwargs['UserName']]

        policy_name = get_value_from_arn(kwargs['PolicyArn'])
        self._check_user_has_policy(policy_name, user, 'DetachUserPolicy')
        policy = self._check_policy_exists(policy_name, 'DetachUserPolicy')

        user.detach_policy(policy_name)
        policy.detach_user(user.username)
        return responses.generic_response()

    def get_access_key_last_used(self, kwargs):
        try:
            access_key = self.access_keys.get(kwargs['AccessKeyId'])
        except KeyError:
            self._access_key_not_found(kwargs['AccessKeyId'],
                                       'GetAccessKeyLastUsed')

        return responses.access_key_last_used_response(access_key)

    def get_login_profile(self, kwargs):
        """Get login profile (password) for user if users has password."""
        self._check_user_exists(kwargs['UserName'], 'GetLoginProfile')

        user = self.users[kwargs['UserName']]
        self._check_login_profile_exists(user, 'GetLoginProfile')

        return responses.login_profile_response(user)

    def get_user(self, kwargs):
        """Get user if user exists."""
        self._check_user_exists(kwargs['UserName'], 'GetUser')

        return responses.user_response(kwargs['UserName'])

    def get_user_policy(self, kwargs):
        """Get attached policy for user."""
        self._check_user_exists(kwargs['UserName'], 'GetUserPolicy')
        user = self.users[kwargs['UserName']]

        policy_name = get_value_from_arn(kwargs['PolicyArn'])
        self._check_user_has_policy(policy_name, user, 'GetUserPolicy')
        policy = self._check_policy_exists(policy_name, 'GetUserPolicy')

        return responses.get_user_policy_response(policy, user.username)

    def list_access_keys(self, kwargs):
        """List all of the users access keys if user exists."""
        self._check_user_exists(kwargs['UserName'], 'ListAccessKeys')

        keys = dict((access_key.id, access_key) for key, access_key
                    in self.access_keys.items()
                    if access_key.username == kwargs['UserName'])
        return responses.list_access_keys_response(keys)

    def list_attached_user_policies(self, kwargs):
        """List all of the users attached policies if user exists."""
        self._check_user_exists(kwargs['UserName'], 'ListAttachedUserPolicies')

        policy_names = self.users[kwargs['UserName']].attached_policies
        policies = [self.policies[name] for name in policy_names]
        return responses.list_attached_user_policies_response(policies)

    def list_groups(self, kwargs):
        """List all groups"""
        return responses.list_groups_response(self.groups)

    def list_groups_for_user(self, kwargs):
        """List all of the users groups if user exists."""
        self._check_user_exists(kwargs['UserName'], 'ListGroupsForUser')

        groups = [self.groups[name] for name in
                  self.users[kwargs['UserName']].groups]
        return responses.list_groups_for_user_response(groups)

    def list_mfa_devices(self, kwargs):
        """List all of the users MFA devices if user exists."""
        self._check_user_exists(kwargs['UserName'], 'ListMFADevices')

        devices = self.users[kwargs['UserName']].mfa_devices
        return responses.list_mfa_devices_response(kwargs['UserName'], devices)

    def list_signing_certificates(self, kwargs):
        """List all of the users signing certs if the user exists."""
        self._check_user_exists(kwargs['UserName'], 'ListSigningCertificates')

        certs = self.users[kwargs['UserName']].signing_certs
        return responses.list_signing_certs_response(kwargs['UserName'], certs)

    def list_users(self, kwargs):
        """List all users."""
        return responses.list_users_response(self.users)

    def remove_user_from_group(self, kwargs):
        """Remove user from group if user exists."""
        self._check_user_exists(kwargs['UserName'], 'RemoveUserFromGroup')
        self._check_group_exists(kwargs['GroupName'], 'RemoveUserFromGroup')

        group = self.groups[kwargs['GroupName']]
        user = self.users[kwargs['UserName']]

        group.remove_user(kwargs['UserName'])
        user.remove_group(kwargs['GroupName'])
        return responses.generic_response()

    def update_access_key(self, kwargs):
        try:
            access_key = self.access_keys.get(kwargs['AccessKeyId'])
        except KeyError:
            self._access_key_not_found(kwargs['AccessKeyId'],
                                       'UpdateAccessKey')

        access_key.status = kwargs['Status']
        return responses.generic_response()

    def update_login_profile(self, kwargs):
        """Update login profile for user."""
        self._check_user_exists(kwargs['UserName'], 'UpdateLoginProfile')

        user = self.users[kwargs['UserName']]
        self._check_login_profile_exists(user, 'UpdateLoginProfile')

        reset_required = kwargs.get('PasswordResetRequired', None)
        password = kwargs.get('Password', None)
        user.update_login_profile(password=password,
                                  reset_required=reset_required)
        return responses.generic_response()

    def update_signing_certificate(self, kwargs):
        """Update signing certificate status."""
        self._check_user_exists(kwargs['UserName'], 'UpdateSigningCertificate')
        self._check_signing_certificate_exists(kwargs['UserName'],
                                               kwargs['CertificateId'],
                                               'UpdateSigningCertificate')

        user = self.users[kwargs['UserName']]
        user.update_signing_certificate(kwargs['CertificateId'],
                                        kwargs['Status'])
        return responses.generic_response()

    def upload_signing_certificate(self, kwargs):
        self._check_user_exists(kwargs['UserName'], 'UploadSigningCertificate')

        user = self.users[kwargs['UserName']]
        for key, cert in user.signing_certs.items():
            if kwargs['CertificateBody'] == cert.body:
                raise client_error('UploadSigningCertificate',
                                   'DuplicateCertificate',
                                   'A duplicate certificate already exists.')

        cert = user.upload_signing_certificate(kwargs['CertificateBody'])
        return responses.upload_signing_certificate_response(
            kwargs['UserName'],
            cert
        )


def mock_iam(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        mocker = MockIAM()
        with patch('botocore.client.BaseClient._make_api_call',
                   new=mocker.mock_make_api_call):
            test(*args, **kwargs)
    return wrapper
