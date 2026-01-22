"""AWS Service Components

Components for creating and managing AWS resources:
- VPC, ECS Cluster, ECS Service
- ALB, Security Groups, ECR
- IAM Roles, Service Discovery
"""

from .credentials import AWSCredentialsComponent
from .vpc import VPCComponent
from .ecs_cluster import ECSClusterComponent
from .ecs_service import ECSServiceComponent
from .alb import ALBComponent
from .security_group import SecurityGroupComponent
from .ecr import ECRComponent
from .iam_role import IAMRoleComponent
from .service_discovery import ServiceDiscoveryComponent

__all__ = [
    "AWSCredentialsComponent",
    "VPCComponent",
    "ECSClusterComponent",
    "ECSServiceComponent",
    "ALBComponent",
    "SecurityGroupComponent",
    "ECRComponent",
    "IAMRoleComponent",
    "ServiceDiscoveryComponent",
]
