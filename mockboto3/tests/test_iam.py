#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import pytest

from mockboto3.core.exceptions import MockBoto3ClientError
from mockboto3.core.utils import inflection
from mockboto3.iam.constants import policy_document, signing_cert
from mockboto3.iam.endpoints import MockIam, mock_iam


class TestIam:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')

    def test_unmocked_operation(self):
        """Test operation not mocked error is returned."""
        msg = 'An error occurred (NoSuchMethod) when calling the ' \
              'CreateGecko operation: Operation not mocked.'

        try:
            mocker = MockIam()
            mocker.mock_make_api_call('CreateGecko',
                                      {'Name': 'gecko'})

        except MockBoto3ClientError as e:
            assert msg == str(e)


class TestExceptions:
    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'

    @mock_iam
    @pytest.mark.parametrize("method",
                             [('AddUserToGroup'),
                              ('CreateAccessKey'),
                              ('DeleteUser'),
                              ('GetUser'),
                              ('ListAccessKeys'),
                              ('ListAttachedUserPolicies'),
                              ('ListGroupsForUser'),
                              ('ListMFADevices'),
                              ('ListSigningCertificates'),
                              ('RemoveUserFromGroup')])
    def test_user_exception(self, method):
        """Test non existent user raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the %s' \
              ' operation: The user with name John cannot be found.' % method

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert non existent user exception
            getattr(self.client, inflection(method))(UserName=self.user)

        assert msg == str(e.value)


class TestUserGroup:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'
        cls.group = 'Admins'

    @mock_iam
    def test_delete_group_exception(self):
        """Test delete non existent group raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the' \
              ' DeleteGroup operation: The group with name Admins' \
              ' cannot be found.'

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert delete non existent user exception
            self.client.delete_group(GroupName=self.group)

        assert msg == str(e.value)

    @mock_iam
    def test_user_group(self):
        """Test user and group endpoints."""
        # Create user and attempt to add user to group
        self.client.create_user(UserName=self.user)

        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'AddUserToGroup operation: The group with name ' \
              'Admins cannot be found.'

        with pytest.raises(MockBoto3ClientError) as e:
            self.client.add_user_to_group(GroupName=self.group,
                                          UserName=self.user)

        assert msg == str(e.value)

        # Create group and add user to group
        self.client.create_group(GroupName=self.group)
        self.client.add_user_to_group(GroupName=self.group,
                                      UserName=self.user)

        # Assert user and group exist and assert user in group
        assert self.client.list_users()['Users'][0]['UserName'] == self.user
        assert self.client.list_groups()['Groups'][0]['GroupName'] == \
                self.group
        assert self.group == self.client.list_groups_for_user(
            UserName=self.user
        )['Groups'][0]['GroupName']

        msg = 'An error occurred (EntityAlreadyExists) when calling the ' \
              'CreateGroup operation: Group with name Admins already exists.'

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert create group exists raises exception
            self.client.create_group(GroupName=self.group)

        assert msg == str(e.value)

        msg = 'An error occurred (EntityAlreadyExists) when calling the ' \
              'CreateUser operation: User with name John already exists.'

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert create user exists raises exception
            self.client.create_user(UserName=self.user)

        assert msg == str(e.value)

        # Get user response
        response = self.client.get_user(UserName=self.user)
        assert response['User']['UserName'] == self.user

        # List groups for user response
        response = self.client.list_groups_for_user(
            GroupName=self.group,
            UserName=self.user)

        assert response['Groups'][0]['GroupName'] == self.group
        assert 1 == len(response['Groups'])

        # Remove user from group
        self.client.remove_user_from_group(GroupName=self.group,
                                           UserName=self.user)
        assert 0 == len(self.client.list_groups_for_user(
            UserName=self.user)['Groups'])

        # Delete group
        self.client.delete_group(GroupName=self.group)
        assert 0 == len(self.client.list_groups()['Groups'])

        # Delete user
        self.client.delete_user(UserName=self.user)
        assert 0 == len(self.client.list_users()['Users'])


class TestAccessKey:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'

    @mock_iam
    def test_delete_access_key_exception(self):
        """Test delete non existent access key raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'DeleteAccessKey operation: The Access Key with id' \
              ' key1234567891234 cannot be found.'

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert delete non existent access key exception
            self.client.delete_access_key(AccessKeyId='key1234567891234')

        assert msg == str(e.value)

    @mock_iam
    def test_access_key(self):
        """Test access key endpoints."""
        self.client.create_user(UserName=self.user)
        response = self.client.create_access_key(
            UserName=self.user
        )

        # Get created key id
        key_id = response['AccessKey']['AccessKeyId']

        # Get user access keys
        response = self.client.list_access_keys(UserName=self.user)

        # Assert id's are equal and keys length is 1
        assert 1 == len(response['AccessKeyMetadata'])
        assert key_id == response['AccessKeyMetadata'][0]['AccessKeyId']

        # Test GetAccessKeyLastUsed
        last_used = self.client.get_access_key_last_used(
            AccessKeyId=key_id
        )['AccessKeyLastUsed']
        assert 'us-west-1' == last_used['Region']
        assert 'iam' == last_used['ServiceName']
        assert last_used['LastUsedDate'] is not None

        # Test UpdateAccessKey
        self.client.update_access_key(AccessKeyId=key_id, Status='Inactive')
        response = self.client.list_access_keys(UserName=self.user)

        assert 'Inactive' == response['AccessKeyMetadata'][0]['Status']

        # Delete access key
        self.client.delete_access_key(AccessKeyId=key_id)

        # Confirm deletion
        response = self.client.list_access_keys(UserName=self.user)
        assert 0 == len(response['AccessKeyMetadata'])


class TestLoginProfile:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.password = 'password'
        cls.user = 'John'

    @mock_iam
    def test_create_login_profile_exception(self):
        """Test create login profile already exists raises exception."""
        msg = 'An error occurred (EntityAlreadyExists) when calling the ' \
              'CreateLoginProfile operation: LoginProfile for user with ' \
              'name John already exists.'

        self.client.create_user(UserName=self.user)

        # Create login profile
        self.client.create_login_profile(UserName=self.user,
                                         Password=self.password)

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert create login profile already exists exception
            self.client.create_login_profile(UserName=self.user,
                                             Password=self.password)
        assert msg == str(e.value)

    @mock_iam
    def test_login_profile(self):
        """Test login profile endpoints."""
        self.client.create_user(UserName=self.user)

        # Create login profile
        response = self.client.create_login_profile(
            UserName=self.user,
            Password=self.password
        )

        assert self.user == response['LoginProfile']['UserName']

        # Get login profile
        response = self.client.get_login_profile(UserName=self.user)
        assert response['LoginProfile']['CreateDate'] is not None

        # Update login profile
        self.client.update_login_profile(UserName=self.user,
                                         PasswordResetRequired=True)

        # Delete profile
        self.client.delete_login_profile(UserName=self.user)

        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'GetLoginProfile operation: LoginProfile for user ' \
              'with name John cannot be found.'

        with pytest.raises(MockBoto3ClientError) as e:
            self.client.get_login_profile(UserName=self.user)

        assert msg == str(e.value)


class TestMfaDevice:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.serial_number = '44324234213'
        cls.user = 'John'

    @mock_iam
    def test_deactivate_mfa_device_exception(self):
        """Test deactivate non existent mfa device raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'DeactivateMFADevice operation: Device with serial ' \
              'number 44324234213 cannot be found.'

        self.client.create_user(UserName=self.user)

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert deactivate non existent mfa device exception
            self.client.deactivate_mfa_device(UserName=self.user,
                                              SerialNumber=self.serial_number)

        assert msg == str(e.value)

    @mock_iam
    def test_mfa_device(self):
        """Test mfa device endpoints."""
        self.client.create_user(UserName=self.user)

        # Enable mfa device
        self.client.enable_mfa_device(UserName=self.user,
                                      SerialNumber=self.serial_number,
                                      AuthenticationCode1='123456',
                                      AuthenticationCode2='654321')

        # List mfa devices
        response = self.client.list_mfa_devices(UserName=self.user)

        assert self.serial_number == response['MFADevices'][0]['SerialNumber']
        assert 1 == len(response['MFADevices'])

        # Deactivate mfa device
        self.client.deactivate_mfa_device(UserName=self.user,
                                          SerialNumber=self.serial_number)

        # Confirm deactivation
        response = self.client.list_mfa_devices(UserName=self.user)
        assert 0 == len(response['MFADevices'])


class TestSigningCertificates:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.user = 'John'

    @mock_iam
    def test_delete_signing_cert_exception(self):
        """Test delete non existent signing cert raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'DeleteSigningCertificate operation: The signing certificate' \
              ' with certificate id 44324234213 cannot be found.'

        self.client.create_user(UserName=self.user)

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert delete non existent signing certificate exception
            self.client.delete_signing_certificate(
                UserName=self.user,
                CertificateId='44324234213'
            )

        assert msg == str(e.value)

    @mock_iam
    def test_signing_certificate(self):
        """Test signing certificate endpoints."""
        self.client.create_user(UserName=self.user)

        # Add signing cert
        response = self.client.upload_signing_certificate(
            UserName=self.user,
            CertificateBody=signing_cert
        )

        # Get cert id
        cert_id = response['Certificate']['CertificateId']

        # Lists signing certs for user
        response = self.client.list_signing_certificates(UserName=self.user)

        assert cert_id == response['Certificates'][0]['CertificateId']
        assert 1 == len(response['Certificates'])

        # Update certificate status
        self.client.update_signing_certificate(UserName=self.user,
                                               CertificateId=cert_id,
                                               Status='Inactive')
        response = self.client.list_signing_certificates(UserName=self.user)

        assert 'Inactive' == response['Certificates'][0]['Status']

        # Delete signing cert
        self.client.delete_signing_certificate(UserName=self.user,
                                               CertificateId=cert_id)

        # Confirm deletion
        response = self.client.list_signing_certificates(UserName=self.user)
        assert 0 == len(response['Certificates'])


class TestUserPolicy:

    @classmethod
    def setup_class(cls):
        cls.client = boto3.client('iam')
        cls.policy = 'arn:aws:iam::aws:policy/Admins'
        cls.user = 'John'

    @mock_iam
    def test_detach_user_policy_exception(self):
        """Test detach non existent user policy raises exception."""
        msg = 'An error occurred (NoSuchEntity) when calling the ' \
              'DetachUserPolicy operation: The policy with' \
              ' name Admins is not attached to the user with name John.'

        self.client.create_user(UserName=self.user)

        with pytest.raises(MockBoto3ClientError) as e:
            # Assert detach non existent user policy exception
            self.client.detach_user_policy(UserName=self.user,
                                           PolicyArn=self.policy)

        assert msg == str(e.value)

    @mock_iam
    def test_user_policy(self):
        """Test user policy endpoints."""
        self.client.create_user(UserName=self.user)

        # Attach user policy
        self.client.create_policy(PolicyName='Admins',
                                  PolicyDocument=policy_document)
        self.client.attach_user_policy(UserName=self.user,
                                       PolicyArn=self.policy)

        # Lists attached user policies
        response = self.client.list_attached_user_policies(
            UserName=self.user
        )

        assert 'Admins' == response['AttachedPolicies'][0]['PolicyName']
        assert 1 == len(response['AttachedPolicies'])

        # Detach attached policy
        self.client.detach_user_policy(UserName=self.user,
                                       PolicyArn=self.policy)

        # Confirm policy detached
        response = self.client.list_attached_user_policies(
            UserName=self.user
        )
        assert 0 == len(response['AttachedPolicies'])

