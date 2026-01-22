"""AWS Client Factory

Utility functions for creating boto3 clients with credentials.
"""

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import Dict, Any, Optional
from .models import AWSCredentials


def create_ec2_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create EC2 client for VPC and Security Group operations."""
    return boto3.client(
        'ec2',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def create_ecs_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create ECS client for ECS operations."""
    return boto3.client(
        'ecs',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def create_elbv2_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create ELBv2 client for ALB operations."""
    return boto3.client(
        'elbv2',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def create_ecr_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create ECR client for ECR operations."""
    return boto3.client(
        'ecr',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def create_iam_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create IAM client for IAM operations."""
    return boto3.client(
        'iam',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def create_servicediscovery_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create ServiceDiscovery client for Service Discovery operations."""
    return boto3.client(
        'servicediscovery',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def create_sts_client(credentials: AWSCredentials, region: Optional[str] = None) -> boto3.client:
    """Create STS client for credential validation."""
    return boto3.client(
        'sts',
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region or credentials.region
    )


def validate_credentials(credentials: AWSCredentials, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate AWS credentials using STS GetCallerIdentity.
    
    Returns:
        dict: {
            'valid': bool,
            'account_id': str (if valid),
            'user_arn': str (if valid),
            'error': str (if invalid)
        }
    """
    try:
        sts_client = create_sts_client(credentials, region)
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
