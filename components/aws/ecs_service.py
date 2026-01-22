"""ECS Service Component

Langflow component for creating AWS ECS Services with Task Definitions.
"""

import json
from typing import Optional, Dict, Any, List
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, IntInput, DataInput, DropdownInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
from ..utils.models import AWSCredentials
from ..utils.aws_client import create_ecs_client


class ECSServiceComponent(Component):
    """ECS Service Creation Component
    
    Creates an ECS Service with Task Definition. Registers task definition first, then creates service.
    """
    
    display_name: str = "ECS Service"
    description: str = "Create AWS ECS Service with Task Definition"
    documentation: str = "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html"
    icon: str = "Container"
    priority: int = 80
    name: str = "ecs_service"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        DataInput(
            name="cluster_output",
            display_name="ECS Cluster Output",
            info="Output from ECS Cluster component",
            required=True
        ),
        StrInput(
            name="service_name",
            display_name="Service Name",
            info="Name for the ECS service",
            required=True
        ),
        StrInput(
            name="task_family",
            display_name="Task Definition Family",
            info="Family name for the task definition",
            required=True
        ),
        StrInput(
            name="container_name",
            display_name="Container Name",
            info="Name of the container",
            required=True
        ),
        StrInput(
            name="container_image",
            display_name="Container Image",
            info="Docker image URI (e.g., nginx:latest or ECR URI)",
            value="nginx:latest",
            required=True
        ),
        StrInput(
            name="cpu",
            display_name="CPU (units)",
            info="CPU units (e.g., 1024, 2048, 4096)",
            value="1024",
            required=True
        ),
        StrInput(
            name="memory",
            display_name="Memory (MB)",
            info="Memory in MB (e.g., 2048, 4096)",
            value="2048",
            required=True
        ),
        IntInput(
            name="container_port",
            display_name="Container Port",
            info="Port the container listens on",
            value=4000,
            required=True
        ),
        IntInput(
            name="desired_count",
            display_name="Desired Count",
            info="Number of tasks to run",
            value=1,
            required=True
        ),
        DropdownInput(
            name="launch_type",
            display_name="Launch Type",
            info="Launch type for the service",
            options=["FARGATE", "EC2"],
            value="FARGATE",
            required=True
        ),
        StrInput(
            name="subnet_ids_json",
            display_name="Subnet IDs (JSON Array)",
            info='JSON array of subnet IDs: ["subnet-xxx", "subnet-yyy"]',
            value="[]",
            required=False
        ),
        StrInput(
            name="security_group_ids_json",
            display_name="Security Group IDs (JSON Array)",
            info='JSON array of security group IDs: ["sg-xxx"]',
            value="[]",
            required=False
        ),
        StrInput(
            name="environment_vars_json",
            display_name="Environment Variables (JSON)",
            info='JSON object: {"VAR1": "value1", "VAR2": "value2"}',
            value="{}",
            required=False
        ),
        StrInput(
            name="log_group_name",
            display_name="CloudWatch Log Group",
            info="CloudWatch log group name (default: /ecs/{service_name})",
            value="",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="service_output", display_name="Service Output", method="build_service"),
    ]
    
    def build_service(self) -> Data:
        """Create ECS service with task definition and return output."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            ecs_client = create_ecs_client(creds)
            
            # Get cluster name from cluster output
            if isinstance(self.cluster_output, dict):
                cluster_name = self.cluster_output.get('cluster_name', '')
            else:
                cluster_data = json.loads(str(self.cluster_output)) if isinstance(self.cluster_output, str) else self.cluster_output
                cluster_name = cluster_data.get('cluster_name', '') if isinstance(cluster_data, dict) else ''
            
            if not cluster_name:
                raise ValueError("Cluster name not found in cluster_output")
            
            # Parse subnet and security group IDs
            subnet_ids = json.loads(self.subnet_ids_json) if self.subnet_ids_json else []
            security_group_ids = json.loads(self.security_group_ids_json) if self.security_group_ids_json else []
            
            # Parse environment variables
            env_vars = json.loads(self.environment_vars_json) if self.environment_vars_json else {}
            environment = [{'name': k, 'value': str(v)} for k, v in env_vars.items()]
            
            # Set log group name
            log_group = self.log_group_name if self.log_group_name else f"/ecs/{self.service_name}"
            
            # Prepare container definition
            container_def = {
                'name': self.container_name,
                'image': self.container_image,
                'essential': True,
                'portMappings': [{
                    'containerPort': self.container_port,
                    'protocol': 'tcp'
                }],
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': log_group,
                        'awslogs-region': creds.region,
                        'awslogs-stream-prefix': 'ecs'
                    }
                }
            }
            
            if environment:
                container_def['environment'] = environment
            
            # Register task definition
            task_def_response = ecs_client.register_task_definition(
                family=self.task_family,
                networkMode='awsvpc',
                requiresCompatibilities=[self.launch_type],
                cpu=self.cpu,
                memory=self.memory,
                containerDefinitions=[container_def]
            )
            
            task_def_arn = task_def_response['taskDefinition']['taskDefinitionArn']
            
            # Prepare network configuration
            network_config = {}
            if subnet_ids:
                network_config['awsvpcConfiguration'] = {
                    'subnets': subnet_ids,
                    'assignPublicIp': 'ENABLED' if self.launch_type == 'FARGATE' else 'DISABLED'
                }
                if security_group_ids:
                    network_config['awsvpcConfiguration']['securityGroups'] = security_group_ids
            
            # Create service
            service_response = ecs_client.create_service(
                cluster=cluster_name,
                serviceName=self.service_name,
                taskDefinition=task_def_arn,
                desiredCount=self.desired_count,
                launchType=self.launch_type,
                networkConfiguration=network_config if network_config else None,
                tags=[
                    {'key': 'Name', 'value': self.service_name},
                    {'key': 'ManagedBy', 'value': 'infrastructure-composer'}
                ]
            )
            
            service = service_response.get('service', {})
            service_arn = service.get('serviceArn', '')
            service_name = service.get('serviceName', self.service_name)
            
            result = {
                'service_name': service_name,
                'service_arn': service_arn,
                'task_definition_arn': task_def_arn,
                'cluster_name': cluster_name,
                'desired_count': self.desired_count,
                'launch_type': self.launch_type,
                'status': 'created'
            }
            
            self.status = f"✓ ECS Service '{service_name}' created successfully"
            return Data(result)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            
            # Handle case where service already exists
            if error_code == 'ServiceAlreadyExistsException':
                try:
                    describe_response = ecs_client.describe_services(
                        cluster=cluster_name,
                        services=[self.service_name]
                    )
                    if describe_response.get('services'):
                        service = describe_response['services'][0]
                        result = {
                            'service_name': service.get('serviceName', self.service_name),
                            'service_arn': service.get('serviceArn', ''),
                            'task_definition_arn': service.get('taskDefinition', ''),
                            'cluster_name': cluster_name,
                            'desired_count': service.get('desiredCount', self.desired_count),
                            'launch_type': self.launch_type,
                            'status': 'exists'
                        }
                        self.status = f"ℹ ECS Service '{self.service_name}' already exists"
                        return Data(result)
                except:
                    pass
            
            error_msg = f"AWS Error: {error_msg}"
            self.status = f"✗ {error_msg}"
            return Data({
                'error': error_msg,
                'status': 'failed'
            })
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data({
                'error': error_msg,
                'status': 'failed'
            })
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data({
                'error': error_msg,
                'status': 'failed'
            })
