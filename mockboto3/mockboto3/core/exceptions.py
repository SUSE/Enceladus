# -*- coding: utf-8 -*-

from botocore.exceptions import ClientError


class MockBoto3ClientError(ClientError):
    """Mock Client error."""


def client_error(operation, code, message):
    """Return mock client error instance."""
    parsed_response = {'Error': {'Code': code, 'Message': message}}
    return MockBoto3ClientError(parsed_response, operation)
