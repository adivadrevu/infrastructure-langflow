"""Validate Credentials Use Case

Application use case for validating AWS credentials.
"""

from typing import Dict, Any
from ...domain.value_objects.aws_credentials import AWSCredentials
from ...infrastructure.aws.clients import CredentialValidator, AWSClientFactory


class ValidateCredentialsUseCase:
    """Use case for validating AWS credentials.
    
    Orchestrates the validation of AWS credentials using
    the credential validator service.
    """
    
    def __init__(self, credential_validator: CredentialValidator):
        """Initialize use case with credential validator.
        
        Args:
            credential_validator: Service for validating credentials
        """
        self._validator = credential_validator
    
    def execute(self, credentials: AWSCredentials) -> Dict[str, Any]:
        """Execute credential validation.
        
        Args:
            credentials: AWS credentials to validate
            
        Returns:
            Validation result dictionary with 'valid', 'account_id', etc.
        """
        return self._validator.validate(credentials)
    
    @classmethod
    def create(cls) -> "ValidateCredentialsUseCase":
        """Factory method to create use case with dependencies.
        
        Returns:
            Configured ValidateCredentialsUseCase instance
        """
        client_factory = AWSClientFactory()
        validator = CredentialValidator(client_factory)
        return cls(validator)
