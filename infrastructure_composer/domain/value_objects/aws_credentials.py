"""AWS Credentials Value Object

Immutable value object representing AWS credentials.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class AWSCredentials:
    """AWS Credentials Value Object
    
    Immutable representation of AWS access credentials.
    
    Attributes:
        access_key_id: AWS Access Key ID
        secret_access_key: AWS Secret Access Key
        region: AWS Region (e.g., 'us-east-1')
        session_token: Optional session token for temporary credentials
    """
    
    access_key_id: str
    secret_access_key: str
    region: str
    session_token: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate credentials after initialization."""
        if not self.access_key_id:
            raise ValueError("access_key_id cannot be empty")
        if not self.secret_access_key:
            raise ValueError("secret_access_key cannot be empty")
        if not self.region:
            raise ValueError("region cannot be empty")
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        result = {
            "accessKeyId": self.access_key_id,
            "secretAccessKey": self.secret_access_key,
            "region": self.region,
        }
        if self.session_token:
            result["sessionToken"] = self.session_token
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "AWSCredentials":
        """Create from dictionary format."""
        return cls(
            access_key_id=data.get("accessKeyId") or data.get("access_key_id", ""),
            secret_access_key=data.get("secretAccessKey") or data.get("secret_access_key", ""),
            region=data.get("region", ""),
            session_token=data.get("sessionToken") or data.get("session_token"),
        )
