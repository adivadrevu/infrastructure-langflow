"""Import helper for components to handle both relative and absolute imports.

This allows components to work when imported directly by Langflow
or when imported as part of the components package.
"""

import sys
import os

def get_utils_imports():
    """Get utils imports that work in both scenarios."""
    try:
        # Try relative import first (when imported as components.aws)
        from .models import AWSCredentials
        from .aws_client import (
            create_ec2_client, create_ecs_client, create_elbv2_client,
            create_ecr_client, create_iam_client, create_servicediscovery_client,
            validate_credentials
        )
        return {
            'AWSCredentials': AWSCredentials,
            'create_ec2_client': create_ec2_client,
            'create_ecs_client': create_ecs_client,
            'create_elbv2_client': create_elbv2_client,
            'create_ecr_client': create_ecr_client,
            'create_iam_client': create_iam_client,
            'create_servicediscovery_client': create_servicediscovery_client,
            'validate_credentials': validate_credentials,
        }
    except ImportError:
        # Fallback: try absolute import (when imported directly by Langflow)
        # Add components directory to path if needed
        current_file = os.path.abspath(__file__)
        components_dir = os.path.dirname(os.path.dirname(current_file))
        if components_dir not in sys.path:
            sys.path.insert(0, components_dir)
        
        from utils.models import AWSCredentials
        from utils.aws_client import (
            create_ec2_client, create_ecs_client, create_elbv2_client,
            create_ecr_client, create_iam_client, create_servicediscovery_client,
            validate_credentials
        )
        return {
            'AWSCredentials': AWSCredentials,
            'create_ec2_client': create_ec2_client,
            'create_ecs_client': create_ecs_client,
            'create_elbv2_client': create_elbv2_client,
            'create_ecr_client': create_ecr_client,
            'create_iam_client': create_iam_client,
            'create_servicediscovery_client': create_servicediscovery_client,
            'validate_credentials': validate_credentials,
        }

# Pre-load imports
_utils = get_utils_imports()
AWSCredentials = _utils['AWSCredentials']
create_ec2_client = _utils['create_ec2_client']
create_ecs_client = _utils['create_ecs_client']
create_elbv2_client = _utils['create_elbv2_client']
create_ecr_client = _utils['create_ecr_client']
create_iam_client = _utils['create_iam_client']
create_servicediscovery_client = _utils['create_servicediscovery_client']
validate_credentials = _utils['validate_credentials']
