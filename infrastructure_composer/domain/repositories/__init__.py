"""Repository Interfaces (Ports)

Abstract interfaces for data access. Implementations live in infrastructure layer.
"""

from .aws_repository import AWSRepository

__all__ = ['AWSRepository']
