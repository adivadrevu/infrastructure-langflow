"""AWS Repository Interface

Abstract interface for AWS resource operations.
Follows Repository pattern for clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from ..value_objects.aws_credentials import AWSCredentials


class AWSRepository(ABC):
    """Abstract base class for AWS resource repositories.
    
    Defines the contract for AWS resource operations.
    Implementations should be in infrastructure layer.
    """
    
    @abstractmethod
    def create(self, credentials: AWSCredentials, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an AWS resource.
        
        Args:
            credentials: AWS credentials for authentication
            config: Resource configuration dictionary
            
        Returns:
            Dictionary containing created resource information
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If resource creation fails
        """
        pass
    
    @abstractmethod
    def get(self, credentials: AWSCredentials, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get an AWS resource by ID.
        
        Args:
            credentials: AWS credentials for authentication
            resource_id: AWS resource identifier
            
        Returns:
            Resource information dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def list(self, credentials: AWSCredentials, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List AWS resources.
        
        Args:
            credentials: AWS credentials for authentication
            filters: Optional filters for listing
            
        Returns:
            List of resource information dictionaries
        """
        pass
    
    @abstractmethod
    def delete(self, credentials: AWSCredentials, resource_id: str) -> bool:
        """Delete an AWS resource.
        
        Args:
            credentials: AWS credentials for authentication
            resource_id: AWS resource identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate resource configuration.
        
        Args:
            config: Resource configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
