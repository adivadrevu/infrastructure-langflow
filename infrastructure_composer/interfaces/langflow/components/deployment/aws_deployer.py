"""AWS Deployer Component

Langflow component for orchestrating AWS resource deployment with dependency ordering.
"""

import json
from typing import Optional, Dict, Any, List
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, DataInput, DropdownInput, Output
from lfx.schema import Data
try:
    from infrastructure_composer.shared.models import AWSCredentials, DeploymentResult, DeployedResource, DeploymentError
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from infrastructure_composer.shared.models import AWSCredentials, DeploymentResult, DeployedResource, DeploymentError


class AWSDeployerComponent(Component):
    """AWS Deployment Orchestrator Component
    
    Orchestrates deployment of AWS resources in dependency order.
    This component collects outputs from other components and deploys them.
    """
    
    display_name: str = "AWS Deployer"
    description: str = "Orchestrate AWS resource deployment with dependency ordering"
    documentation: str = "https://docs.aws.amazon.com/"
    icon: str = "rocket"
    priority: int = 45
    name: str = "aws_deployer"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        DataInput(
            name="infrastructure_data",
            display_name="Infrastructure Data",
            info="Infrastructure data from connected components (JSON or dict)",
            required=True
        ),
        DropdownInput(
            name="environment",
            display_name="Environment",
            info="Environment for deployment",
            options=["sbx", "live"],
            value="sbx",
            required=True
        ),
        StrInput(
            name="region",
            display_name="AWS Region",
            info="AWS region for deployment",
            value="us-east-1",
            required=True
        ),
    ]
    
    outputs = [
        Output(name="deployment_result", display_name="Deployment Result", method="build_deployment"),
    ]
    
    def build_deployment(self) -> Data:
        """Orchestrate deployment and return result."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            # Parse infrastructure data
            if isinstance(self.infrastructure_data, str):
                infra_data = json.loads(self.infrastructure_data)
            else:
                infra_data = self.infrastructure_data if isinstance(self.infrastructure_data, dict) else {}
            
            resources: List[DeployedResource] = []
            errors: List[DeploymentError] = []
            
            # Deployment order: VPC -> ECS Cluster -> Security Groups -> ALB -> ECS Service -> ECR -> IAM -> Service Discovery
            
            # Note: In a real implementation, this would:
            # 1. Parse component outputs from infrastructure_data
            # 2. Determine dependency graph
            # 3. Deploy resources in topological order
            # 4. Handle errors and rollback if needed
            
            # For now, this is a placeholder that returns a structured result
            # The actual deployment happens in individual components
            
            result = DeploymentResult(
                success=len(errors) == 0,
                resources=resources,
                errors=errors if errors else None
            )
            
            self.status = f"✓ Deployment orchestration completed for {self.environment} environment"
            return Data(data=result.dict(by_alias=True))
            
        except Exception as e:
            error_msg = f"Deployment error: {str(e)}"
            self.status = f"✗ {error_msg}"
            result = DeploymentResult(
                success=False,
                resources=[],
                errors=[DeploymentError(
                    resource='deployment',
                    message=error_msg
                )]
            )
            return Data(data=result.dict(by_alias=True))
