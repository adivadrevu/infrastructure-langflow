"""AWS Client Factory

Factory for creating AWS SDK clients with proper credential management.
Follows Factory pattern for clean dependency injection.
"""

from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from ....domain.value_objects.aws_credentials import AWSCredentials


class AWSClientFactory:
    """Factory for creating AWS SDK clients.
    
    Encapsulates boto3 client creation logic and provides
    a clean interface for dependency injection.
    """
    
    @staticmethod
    def create_ec2_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create EC2 client for VPC and Security Group operations.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured EC2 boto3 client
        """
        return boto3.client(
            'ec2',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )
    
    @staticmethod
    def create_ecs_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create ECS client for ECS operations.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured ECS boto3 client
        """
        return boto3.client(
            'ecs',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )
    
    @staticmethod
    def create_elbv2_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create ELBv2 client for ALB operations.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured ELBv2 boto3 client
        """
        return boto3.client(
            'elbv2',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )
    
    @staticmethod
    def create_ecr_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create ECR client for ECR operations.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured ECR boto3 client
        """
        return boto3.client(
            'ecr',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )
    
    @staticmethod
    def create_iam_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create IAM client for IAM operations.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured IAM boto3 client
        """
        return boto3.client(
            'iam',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )
    
    @staticmethod
    def create_servicediscovery_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create ServiceDiscovery client for Service Discovery operations.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured ServiceDiscovery boto3 client
        """
        return boto3.client(
            'servicediscovery',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )
    
    @staticmethod
    def create_sts_client(
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> boto3.client:
        """Create STS client for credential validation.
        
        Args:
            credentials: AWS credentials
            region: Optional region override
            
        Returns:
            Configured STS boto3 client
        """
        return boto3.client(
            'sts',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=region or credentials.region
        )


class CredentialValidator:
    """Service for validating AWS credentials."""
    
    def __init__(self, client_factory: AWSClientFactory):
        """Initialize with client factory.
        
        Args:
            client_factory: Factory for creating AWS clients
        """
        self._client_factory = client_factory
    
    def validate(
        self,
        credentials: AWSCredentials,
        region: Optional[str] = None
    ) -> dict:
        """
        Validate AWS credentials using STS GetCallerIdentity.
        
        Args:
            credentials: AWS credentials to validate
            region: Optional region override
            
        Returns:
            dict: {
                'valid': bool,
                'account_id': str (if valid),
                'user_arn': str (if valid),
                'error': str (if invalid)
            }
        """
        try:
            sts_client = self._client_factory.create_sts_client(credentials, region)
            response = sts_client.get_caller_identity()
            
            return {
                'valid': True,
                'account_id': response.get('Account'),
                'user_arn': response.get('Arn'),
                'user_id': response.get('UserId')
            }
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            return {
                'valid': False,
                'error': f"{error_code}: {error_message}"
            }
        except BotoCoreError as e:
            return {
                'valid': False,
                'error': f"BotoCoreError: {str(e)}"
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f"Unexpected error: {str(e)}"
            }
