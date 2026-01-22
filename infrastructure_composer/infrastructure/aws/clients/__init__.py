"""AWS Client Factories

Creates and manages AWS SDK clients.
"""

from .client_factory import AWSClientFactory, CredentialValidator

__all__ = ['AWSClientFactory', 'CredentialValidator']
