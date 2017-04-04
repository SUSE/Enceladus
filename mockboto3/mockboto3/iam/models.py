# -*- coding: utf-8 -*-

""""IAM Classes."""

from datetime import datetime, timezone

from mockboto3.core.utils import get_random_string
from mockboto3.iam.utils import get_arn


class AccessKey(object):
    """Access Key class used for mocking AWS backend"""

    def __init__(self, user_name):
        super(AccessKey, self).__init__()
        self.id = get_random_string(length=20)
        self.create_date = datetime.now(timezone.utc)
        self.key = get_random_string(length=40)
        self.last_used = AccessKeyLastUsed()
        self.status = "Active"
        self.username = user_name


class AccessKeyLastUsed(object):
    """Access Key Last Used for tracking how and when a key was used."""

    def __init__(self):
        super(AccessKeyLastUsed, self).__init__()
        self.date = datetime.now(timezone.utc)
        self.region = 'us-west-1'
        self.service_name = 'iam'


class Group(object):
    """Group class used for mocking AWS backend group objects"""

    def __init__(self, name, path="/"):
        super(Group, self).__init__()
        self.id = get_random_string(length=10)
        self.attached_policies = []
        self.create_date = datetime.now(timezone.utc)
        self.name = name
        self.path = path
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    @property
    def arn(self):
        return get_arn("group", self.name)

    def attach_policy(self, policy):
        self.attached_policies.append(policy)

    def detach_policy(self, policy):
        self.attached_policies.remove(policy)

    def remove_user(self, user):
        self.users.remove(user)


class LoginProfile(object):
    """Login profile (password) for AWS User."""

    def __init__(self, password, reset_required=False):
        super(LoginProfile, self).__init__()
        self.password = password
        self.create_date = datetime.now(timezone.utc)
        self.reset_required = reset_required


class MFADevice(object):
    """MFA Device class."""

    def __init__(self, serial_number):
        super(MFADevice, self).__init__()
        self.enable_date = datetime.now(timezone.utc)
        self.serial_number = serial_number


class Policy(object):
    """Policy documents."""

    def __init__(self, name, document, description="", path="/"):
        super(Policy, self).__init__()
        self.id = get_random_string(length=16)
        self.attachment_count = 0
        self.create_date = datetime.now(timezone.utc)
        self.default_version_id = "v1"
        self.description = description
        self.groups = []
        self.is_attachable = True
        self.name = name
        self.path = path
        self.update_date = self.create_date
        self.users = []
        self.versions = []

        # Create initial version of policy (v1)
        self.create_new_version(document)

    @property
    def arn(self):
        return get_arn("policy", self.name)

    def attach_group(self, group):
        self.groups.append(group)
        self.attachment_count += 1

    def attach_user(self, user):
        self.users.append(user)
        self.attachment_count += 1

    def create_new_version(self, document):
        self.versions.append(
            PolicyVersion(document, len(self.versions) + 1)
        )

    def detach_group(self, group):
        self.groups.remove(group)
        self.attachment_count -= 1

    def detach_user(self, user):
        self.users.remove(user)
        self.attachment_count -= 1

    @property
    def document(self):
        return self.versions[self.default_version_id[1] - 1].document

    def set_default_version(self, version_id):
        self.default_version_id = version_id


class PolicyVersion(object):
    """Versions of a policy object."""

    def __init__(self, document, version):
        super(PolicyVersion, self).__init__()
        self.create_date = datetime.now(timezone.utc)
        self.document = document
        self.is_default_version = True if version == 1 else False
        self.version_number = version

    @property
    def version(self):
        return "v{version}".format(version=self.version_number)


class SigningCertificate(object):
    """Signing certificate class."""

    def __init__(self, body):
        super(SigningCertificate, self).__init__()
        self.id = get_random_string(length=24)
        self.body = body
        self.status = 'Active'
        self.upload_date = datetime.now(timezone.utc)


class User(object):
    """User class used for mocking AWS backend user objects."""

    def __init__(self, user_name):
        super(User, self).__init__()
        self.id = get_random_string(length=10)
        self.attached_policies = []
        self.create_date = datetime.now(timezone.utc)
        self.groups = []
        self.login_profile = None
        self.mfa_devices = {}
        self.password_last_used = None
        self.signing_certs = {}
        self.username = user_name

    def add_group(self, group):
        self.groups.append(group)

    def attach_policy(self, policy):
        self.attached_policies.append(policy)

    def create_login_profile(self, password, reset_required=False):
        self.login_profile = LoginProfile(password, reset_required)

    def deactivate_mfa_device(self, serial_number):
        self.mfa_devices.pop(serial_number)

    def delete_login_profile(self):
        self.login_profile = None

    def delete_signing_certificate(self, cert_id):
        self.signing_certs.pop(cert_id)

    def detach_policy(self, policy):
        self.attached_policies.remove(policy)

    def enable_mfa_device(self, serial_number):
        self.mfa_devices[serial_number] = MFADevice(serial_number)

    def remove_group(self, group):
        self.groups.remove(group)

    def update_login_profile(self, password=None, reset_required=None):
        if password:
            self.login_profile.password = password
        if reset_required is not None:
            self.login_profile.reset_required = reset_required

    def update_signing_certificate(self, cert_id, status):
        self.signing_certs.get(cert_id).status = status

    def upload_signing_certificate(self, body):
        certificate = SigningCertificate(body)
        self.signing_certs[certificate.id] = certificate
        return certificate
