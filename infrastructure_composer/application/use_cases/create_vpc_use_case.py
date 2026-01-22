"""Create VPC Use Case

Application use case for creating AWS VPC.
"""

from typing import Dict, Any
from ...domain.value_objects.aws_credentials import AWSCredentials
from ...domain.repositories.aws_repository import AWSRepository


class CreateVPCUseCase:
    """Use case for creating AWS VPC.
    
    Orchestrates VPC creation using the repository pattern.
    """
    
    def __init__(self, vpc_repository: AWSRepository):
        """Initialize use case with VPC repository.
        
        Args:
            vpc_repository: Repository for VPC operations
        """
        self._repository = vpc_repository
    
    def execute(
        self,
        credentials: AWSCredentials,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute VPC creation.
        
        Args:
            credentials: AWS credentials
            config: VPC configuration
            
        Returns:
            Created VPC information
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If creation fails
        """
        # Validate configuration
        is_valid, error = self._repository.validate_config(config)
        if not is_valid:
            raise ValueError(f"Invalid configuration: {error}")
        
        # Create VPC
        result = self._repository.create(credentials, config)
        
        return {
            'success': True,
            'vpc': result,
            'message': f"VPC {result.get('id')} created successfully"
        }
