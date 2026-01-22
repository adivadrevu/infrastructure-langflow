"""Environment Value Object

Represents deployment environment (sbx/live).
"""

from enum import Enum
from typing import Literal


EnvironmentType = Literal['sbx', 'live']


class Environment(str, Enum):
    """Deployment Environment Enum
    
    Represents the deployment environment for infrastructure.
    """
    
    SANDBOX = 'sbx'
    LIVE = 'live'
    
    @classmethod
    def from_string(cls, value: str) -> "Environment":
        """Create Environment from string value."""
        value_lower = value.lower()
        if value_lower == 'sbx' or value_lower == 'sandbox':
            return cls.SANDBOX
        elif value_lower == 'live' or value_lower == 'prod' or value_lower == 'production':
            return cls.LIVE
        else:
            raise ValueError(f"Invalid environment: {value}. Must be 'sbx' or 'live'")
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
