"""Application Load Balancer Component

Langflow component for creating AWS Application Load Balancers.
"""

import json
from typing import Optional, Dict, Any, List
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, IntInput, DataInput, DropdownInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
from ..utils.models import AWSCredentials
from ..utils.aws_client import create_elbv2_client


class ALBComponent(Component):
    """Application Load Balancer Creation Component
    
    Creates an Application Load Balancer with listeners and target groups.
    """
    
    display_name: str = "Application Load Balancer"
    description: str = "Create AWS Application Load Balancer (ALB) with listeners and target groups"
    documentation: str = "https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html"
    icon: str = "LoadBalancer"
    priority: int = 75
    name: str = "alb"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        DataInput(
            name="vpc_output",
            display_name="VPC Output",
            info="Output from VPC component",
            required=True
        ),
        StrInput(
            name="name",
            display_name="Load Balancer Name",
            info="Name for the load balancer",
            required=True
        ),
        DropdownInput(
            name="scheme",
            display_name="Scheme",
            info="Load balancer scheme",
            options=["internet-facing", "internal"],
            value="internet-facing",
            required=True
        ),
        StrInput(
            name="subnet_ids_json",
            display_name="Subnet IDs (JSON Array)",
            info='JSON array of subnet IDs from VPC: ["subnet-xxx", "subnet-yyy"]',
            value="[]",
            required=True
        ),
        StrInput(
            name="security_group_ids_json",
            display_name="Security Group IDs (JSON Array)",
            info='JSON array of security group IDs: ["sg-xxx"]',
            value="[]",
            required=True
        ),
        IntInput(
            name="listener_port",
            display_name="Listener Port",
            info="Port for the default listener",
            value=80,
            required=True
        ),
        DropdownInput(
            name="listener_protocol",
            display_name="Listener Protocol",
            info="Protocol for the default listener",
            options=["HTTP", "HTTPS"],
            value="HTTP",
            required=True
        ),
        StrInput(
            name="target_group_name",
            display_name="Target Group Name",
            info="Name for the default target group",
            required=True
        ),
        IntInput(
            name="target_group_port",
            display_name="Target Group Port",
            info="Port for targets",
            value=4000,
            required=True
        ),
        DropdownInput(
            name="target_group_protocol",
            display_name="Target Group Protocol",
            info="Protocol for targets",
            options=["HTTP", "HTTPS"],
            value="HTTP",
            required=True
        ),
        StrInput(
            name="health_check_path",
            display_name="Health Check Path",
            info="Path for health checks",
            value="/",
            required=False
        ),
        StrInput(
            name="certificate_arns_json",
            display_name="Certificate ARNs (JSON Array)",
            info='JSON array of ACM certificate ARNs for HTTPS: ["arn:aws:acm:..."]',
            value="[]",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="alb_output", display_name="ALB Output", method="build_alb"),
    ]
    
    def build_alb(self) -> Data:
        """Create ALB with target group and listener, return output."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            elbv2_client = create_elbv2_client(creds)
            
            # Get VPC ID from VPC output
            if isinstance(self.vpc_output, dict):
                vpc_id = self.vpc_output.get('vpc_id', '')
            else:
                vpc_data = json.loads(str(self.vpc_output)) if isinstance(self.vpc_output, str) else self.vpc_output
                vpc_id = vpc_data.get('vpc_id', '') if isinstance(vpc_data, dict) else ''
            
            if not vpc_id:
                raise ValueError("VPC ID not found in vpc_output")
            
            # Parse subnet and security group IDs
            subnet_ids = json.loads(self.subnet_ids_json) if self.subnet_ids_json else []
            security_group_ids = json.loads(self.security_group_ids_json) if self.security_group_ids_json else []
            
            if not subnet_ids:
                raise ValueError("At least one subnet ID is required")
            if not security_group_ids:
                raise ValueError("At least one security group ID is required")
            
            # Create load balancer
            lb_response = elbv2_client.create_load_balancer(
                Name=self.name,
                Subnets=subnet_ids,
                SecurityGroups=security_group_ids,
                Scheme=self.scheme,
                Type='application',
                Tags=[
                    {'Key': 'Name', 'Value': self.name},
                    {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                ]
            )
            
            lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
            lb_dns = lb_response['LoadBalancers'][0]['DNSName']
            
            # Create target group
            tg_response = elbv2_client.create_target_group(
                Name=self.target_group_name,
                Protocol=self.target_group_protocol,
                Port=self.target_group_port,
                VpcId=vpc_id,
                HealthCheckProtocol=self.target_group_protocol,
                HealthCheckPath=self.health_check_path,
                HealthCheckIntervalSeconds=30,
                HealthCheckTimeoutSeconds=5,
                HealthyThresholdCount=2,
                UnhealthyThresholdCount=2,
                TargetType='ip',
                Tags=[
                    {'Key': 'Name', 'Value': self.target_group_name},
                    {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                ]
            )
            
            tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
            
            # Create listener
            listener_kwargs = {
                'LoadBalancerArn': lb_arn,
                'Protocol': self.listener_protocol,
                'Port': self.listener_port,
                'DefaultActions': [{
                    'Type': 'forward',
                    'TargetGroupArn': tg_arn
                }]
            }
            
            # Add certificates for HTTPS
            if self.listener_protocol == 'HTTPS':
                cert_arns = json.loads(self.certificate_arns_json) if self.certificate_arns_json else []
                if not cert_arns:
                    raise ValueError("Certificate ARNs required for HTTPS listener")
                listener_kwargs['Certificates'] = [{'CertificateArn': arn} for arn in cert_arns]
            
            listener_response = elbv2_client.create_listener(**listener_kwargs)
            listener_arn = listener_response['Listeners'][0]['ListenerArn']
            
            result = {
                'load_balancer_arn': lb_arn,
                'load_balancer_name': self.name,
                'dns_name': lb_dns,
                'target_group_arn': tg_arn,
                'target_group_name': self.target_group_name,
                'listener_arn': listener_arn,
                'scheme': self.scheme,
                'status': 'created'
            }
            
            self.status = f"✓ ALB '{self.name}' created successfully (DNS: {lb_dns})"
            return Data(data=result)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
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
