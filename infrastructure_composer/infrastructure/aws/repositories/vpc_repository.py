"""VPC Repository Implementation

AWS VPC repository implementation using boto3.
Implements the AWSRepository interface from domain layer.
"""

from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

from ...domain.repositories.aws_repository import AWSRepository
from ...domain.value_objects.aws_credentials import AWSCredentials
from ..clients import AWSClientFactory


class VPCRepository(AWSRepository):
    """Repository implementation for AWS VPC operations."""
    
    def __init__(self, client_factory: AWSClientFactory):
        """Initialize repository with client factory.
        
        Args:
            client_factory: Factory for creating AWS clients
        """
        self._client_factory = client_factory
    
    def create(self, credentials: AWSCredentials, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a VPC with subnets, gateways, and route tables.
        
        Args:
            credentials: AWS credentials
            config: VPC configuration dictionary
            
        Returns:
            Dictionary containing created VPC information
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If VPC creation fails
        """
        ec2_client = self._client_factory.create_ec2_client(credentials)
        
        # Validate configuration
        is_valid, error = self.validate_config(config)
        if not is_valid:
            raise ValueError(f"Invalid VPC configuration: {error}")
        
        try:
            # Create VPC
            vpc_response = ec2_client.create_vpc(
                CidrBlock=config['cidrBlock'],
                AmazonProvidedIpv6CidrBlock=False,
                InstanceTenancy='default',
                TagSpecifications=[{
                    'ResourceType': 'vpc',
                    'Tags': [{'Key': 'Name', 'Value': config.get('name', 'VPC')}]
                }]
            )
            vpc_id = vpc_response['Vpc']['VpcId']
            
            # Enable DNS
            if config.get('enableDnsHostnames'):
                ec2_client.modify_vpc_attribute(
                    VpcId=vpc_id,
                    EnableDnsHostnames={'Value': True}
                )
            
            if config.get('enableDnsSupport'):
                ec2_client.modify_vpc_attribute(
                    VpcId=vpc_id,
                    EnableDnsSupport={'Value': True}
                )
            
            # Create subnets, gateways, etc. (simplified for example)
            # Full implementation would handle all VPC components
            
            return {
                'id': vpc_id,
                'cidrBlock': config['cidrBlock'],
                'state': vpc_response['Vpc']['State'],
                'region': credentials.region
            }
            
        except ClientError as e:
            raise RuntimeError(f"Failed to create VPC: {str(e)}")
    
    def get(self, credentials: AWSCredentials, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get VPC by ID."""
        ec2_client = self._client_factory.create_ec2_client(credentials)
        try:
            response = ec2_client.describe_vpcs(VpcIds=[resource_id])
            if response['Vpcs']:
                vpc = response['Vpcs'][0]
                return {
                    'id': vpc['VpcId'],
                    'cidrBlock': vpc['CidrBlock'],
                    'state': vpc['State'],
                }
            return None
        except ClientError:
            return None
    
    def list(self, credentials: AWSCredentials, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List VPCs."""
        ec2_client = self._client_factory.create_ec2_client(credentials)
        try:
            response = ec2_client.describe_vpcs()
            return [
                {
                    'id': vpc['VpcId'],
                    'cidrBlock': vpc['CidrBlock'],
                    'state': vpc['State'],
                }
                for vpc in response.get('Vpcs', [])
            ]
        except ClientError:
            return []
    
    def delete(self, credentials: AWSCredentials, resource_id: str) -> bool:
        """Delete VPC."""
        ec2_client = self._client_factory.create_ec2_client(credentials)
        try:
            ec2_client.delete_vpc(VpcId=resource_id)
            return True
        except ClientError:
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate VPC configuration."""
        if 'cidrBlock' not in config:
            return False, "cidrBlock is required"
        
        # Basic CIDR validation
        cidr = config['cidrBlock']
        if not isinstance(cidr, str) or '/' not in cidr:
            return False, "cidrBlock must be a valid CIDR notation"
        
        return True, None
