"""ECS Cluster Component

Langflow component for creating AWS ECS Clusters.
"""

import json
from typing import Optional, Dict, Any
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, BoolInput, DataInput, DropdownInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
try:
    from ..utils.models import AWSCredentials
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from utils.models import AWSCredentials
try:
    from ..utils.aws_client import create_ecs_client
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from utils.aws_client import create_ecs_client


class ECSClusterComponent(Component):
    """ECS Cluster Creation Component
    
    Creates an ECS Cluster with optional Container Insights.
    """
    
    display_name: str = "ECS Cluster"
    description: str = "Create AWS ECS (Elastic Container Service) Cluster"
    documentation: str = "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/clusters.html"
    icon: str = "server"
    priority: int = 85
    name: str = "ecs_cluster"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        StrInput(
            name="name",
            display_name="Cluster Name",
            info="Name for the ECS cluster",
            required=True
        ),
        DropdownInput(
            name="launch_type",
            display_name="Launch Type",
            info="Launch type for tasks in the cluster",
            options=["FARGATE", "EC2"],
            value="FARGATE",
            required=True
        ),
        BoolInput(
            name="enable_container_insights",
            display_name="Enable Container Insights",
            info="Enable CloudWatch Container Insights",
            value=True,
            required=False
        ),
        StrInput(
            name="tags_json",
            display_name="Tags (JSON)",
            info='JSON object of tags: {"Environment": "prod", "Team": "platform"}',
            value="{}",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="cluster_output", display_name="Cluster Output", method="build_cluster"),
    ]
    
    def build_cluster(self) -> Data:
        """Create ECS cluster and return output with cluster name and ARN."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            ecs_client = create_ecs_client(creds)
            
            # Prepare cluster settings
            settings = []
            if self.enable_container_insights:
                settings.append({
                    'name': 'containerInsights',
                    'value': 'enabled'
                })
            
            # Parse tags
            tags = []
            tags_data = json.loads(self.tags_json) if self.tags_json else {}
            tags.append({'key': 'Name', 'value': self.name})
            tags.append({'key': 'ManagedBy', 'value': 'infrastructure-composer'})
            for key, value in tags_data.items():
                tags.append({'key': key, 'value': str(value)})
            
            # Create cluster
            response = ecs_client.create_cluster(
                clusterName=self.name,
                settings=settings if settings else None,
                tags=tags if tags else None
            )
            
            cluster = response.get('cluster', {})
            cluster_arn = cluster.get('clusterArn', '')
            cluster_name = cluster.get('clusterName', self.name)
            
            result = {
                'cluster_name': cluster_name,
                'cluster_arn': cluster_arn,
                'launch_type': self.launch_type,
                'container_insights_enabled': self.enable_container_insights,
                'status': 'created'
            }
            
            self.status = f"✓ ECS Cluster '{cluster_name}' created successfully (ARN: {cluster_arn})"
            return Data(data=result)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            
            # Handle case where cluster already exists
            if error_code == 'ClusterAlreadyExistsException':
                # Try to describe the existing cluster
                try:
                    describe_response = ecs_client.describe_clusters(clusters=[self.name])
                    if describe_response.get('clusters'):
                        cluster = describe_response['clusters'][0]
                        result = {
                            'cluster_name': cluster.get('clusterName', self.name),
                            'cluster_arn': cluster.get('clusterArn', ''),
                            'launch_type': self.launch_type,
                            'container_insights_enabled': self.enable_container_insights,
                            'status': 'exists'
                        }
                        self.status = f"ℹ ECS Cluster '{self.name}' already exists"
                        return Data(data=result)
                except:
                    pass
            
            error_msg = f"AWS Error: {error_msg}"
            self.status = f"✗ {error_msg}"
            return Data(data={
                'error': error_msg,
                'status': 'failed'
            })
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data(data={
                'error': error_msg,
                'status': 'failed'
            })
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data(data={
                'error': error_msg,
                'status': 'failed'
            })
