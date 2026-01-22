"""VPC Component Adapter

Adapts VPC use case to Langflow component interface.
This is the bridge between Langflow and our clean architecture.
"""

from typing import Dict, Any
from lfx.schema import Data

from ....application.use_cases.create_vpc_use_case import CreateVPCUseCase
from ....domain.value_objects.aws_credentials import AWSCredentials
from ....infrastructure.aws.clients import AWSClientFactory
from ....infrastructure.aws.repositories.vpc_repository import VPCRepository


class VPCComponentAdapter:
    """Adapter for VPC Langflow component.
    
    Adapts Langflow component interface to application use cases.
    """
    
    def __init__(self):
        """Initialize adapter with dependencies."""
        client_factory = AWSClientFactory()
        vpc_repository = VPCRepository(client_factory)
        self._use_case = CreateVPCUseCase(vpc_repository)
    
    def create_vpc(
        self,
        credentials_data: Dict[str, Any],
        vpc_config: Dict[str, Any]
    ) -> Data:
        """Create VPC using use case.
        
        Args:
            credentials_data: AWS credentials dictionary
            vpc_config: VPC configuration dictionary
            
        Returns:
            Langflow Data object with result
        """
        # Convert credentials to value object
        credentials = AWSCredentials.from_dict(credentials_data)
        
        # Execute use case
        result = self._use_case.execute(credentials, vpc_config)
        
        return Data(data=result)
    
    @classmethod
    def create(cls) -> "VPCComponentAdapter":
        """Factory method to create adapter.
        
        Returns:
            Configured VPCComponentAdapter instance
        """
        return cls()
