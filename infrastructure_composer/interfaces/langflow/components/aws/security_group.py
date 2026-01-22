"""Security Group Component

Langflow component for creating AWS Security Groups with ingress and egress rules.
"""

import json
from typing import Optional, Dict, Any, List
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, DataInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
try:
    from infrastructure_composer.shared.models import AWSCredentials
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from infrastructure_composer.shared.models import AWSCredentials
try:
    from infrastructure_composer.shared.aws_client import create_ec2_client
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from infrastructure_composer.shared.aws_client import create_ec2_client


class SecurityGroupComponent(Component):
    """Security Group Creation Component
    
    Creates a Security Group with ingress and egress rules.
    """
    
    display_name: str = "Security Group"
    description: str = "Create AWS Security Group with firewall rules"
    documentation: str = "https://docs.aws.amazon.com/vpc/latest/userguide/security-groups.html"
    icon: str = "shield"
    priority: int = 70
    name: str = "security_group"
    
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
            display_name="Security Group Name",
            info="Name for the security group",
            required=True
        ),
        StrInput(
            name="description",
            display_name="Description",
            info="Description for the security group",
            required=True
        ),
        StrInput(
            name="ingress_rules_json",
            display_name="Ingress Rules (JSON Array)",
            info='JSON array of ingress rules: [{"fromPort": 80, "toPort": 80, "protocol": "tcp", "cidrBlocks": ["0.0.0.0/0"]}]',
            value="[]",
            required=False
        ),
        StrInput(
            name="egress_rules_json",
            display_name="Egress Rules (JSON Array)",
            info='JSON array of egress rules: [{"fromPort": 0, "toPort": 65535, "protocol": "tcp", "cidrBlocks": ["0.0.0.0/0"]}]',
            value="[]",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="security_group_output", display_name="Security Group Output", method="build_security_group"),
    ]
    
    def build_security_group(self) -> Data:
        """Create security group with rules and return output."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            ec2_client = create_ec2_client(creds)
            
            # Get VPC ID from VPC output
            if isinstance(self.vpc_output, dict):
                vpc_id = self.vpc_output.get('vpc_id', '')
            else:
                vpc_data = json.loads(str(self.vpc_output)) if isinstance(self.vpc_output, str) else self.vpc_output
                vpc_id = vpc_data.get('vpc_id', '') if isinstance(vpc_data, dict) else ''
            
            if not vpc_id:
                raise ValueError("VPC ID not found in vpc_output")
            
            # Create security group
            sg_response = ec2_client.create_security_group(
                GroupName=self.name,
                Description=self.description,
                VpcId=vpc_id,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [
                        {'Key': 'Name', 'Value': self.name},
                        {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                    ]
                }]
            )
            
            sg_id = sg_response['GroupId']
            sg_arn = f"arn:aws:ec2:{creds.region}:{creds.access_key_id.split(':')[0] if ':' in creds.access_key_id else 'account'}:security-group/{sg_id}"
            
            # Parse and add ingress rules
            ingress_rules = json.loads(self.ingress_rules_json) if self.ingress_rules_json else []
            if ingress_rules:
                ingress_permissions = []
                for rule in ingress_rules:
                    perm = {
                        'IpProtocol': rule.get('protocol', 'tcp'),
                    }
                    
                    if rule.get('fromPort') is not None:
                        perm['FromPort'] = rule.get('fromPort')
                    if rule.get('toPort') is not None:
                        perm['ToPort'] = rule.get('toPort')
                    
                    if rule.get('cidrBlocks'):
                        perm['IpRanges'] = [
                            {'CidrIp': cidr, 'Description': rule.get('description', '')}
                            for cidr in rule.get('cidrBlocks', [])
                        ]
                    
                    if rule.get('sourceSecurityGroupId'):
                        perm['UserIdGroupPairs'] = [{
                            'GroupId': rule.get('sourceSecurityGroupId'),
                            'Description': rule.get('description', '')
                        }]
                    
                    ingress_permissions.append(perm)
                
                if ingress_permissions:
                    ec2_client.authorize_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=ingress_permissions
                    )
            
            # Parse and add egress rules
            egress_rules = json.loads(self.egress_rules_json) if self.egress_rules_json else []
            if egress_rules:
                egress_permissions = []
                for rule in egress_rules:
                    perm = {
                        'IpProtocol': rule.get('protocol', 'tcp'),
                    }
                    
                    if rule.get('fromPort') is not None:
                        perm['FromPort'] = rule.get('fromPort')
                    if rule.get('toPort') is not None:
                        perm['ToPort'] = rule.get('toPort')
                    
                    if rule.get('cidrBlocks'):
                        perm['IpRanges'] = [
                            {'CidrIp': cidr, 'Description': rule.get('description', '')}
                            for cidr in rule.get('cidrBlocks', [])
                        ]
                    
                    if rule.get('destinationSecurityGroupId'):
                        perm['UserIdGroupPairs'] = [{
                            'GroupId': rule.get('destinationSecurityGroupId'),
                            'Description': rule.get('description', '')
                        }]
                    
                    egress_permissions.append(perm)
                
                if egress_permissions:
                    ec2_client.authorize_security_group_egress(
                        GroupId=sg_id,
                        IpPermissions=egress_permissions
                    )
            
            result = {
                'security_group_id': sg_id,
                'security_group_name': self.name,
                'security_group_arn': sg_arn,
                'vpc_id': vpc_id,
                'status': 'created'
            }
            
            self.status = f"✓ Security Group '{self.name}' created successfully (ID: {sg_id})"
            return Data(data=result)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            
            # Handle case where security group already exists
            if error_code == 'InvalidGroup.Duplicate':
                # Try to find existing security group
                try:
                    filters = [
                        {'Name': 'group-name', 'Values': [self.name]},
                        {'Name': 'vpc-id', 'Values': [vpc_id]}
                    ]
                    describe_response = ec2_client.describe_security_groups(Filters=filters)
                    if describe_response.get('SecurityGroups'):
                        sg = describe_response['SecurityGroups'][0]
                        result = {
                            'security_group_id': sg['GroupId'],
                            'security_group_name': self.name,
                            'security_group_arn': sg.get('GroupArn', ''),
                            'vpc_id': vpc_id,
                            'status': 'exists'
                        }
                        self.status = f"ℹ Security Group '{self.name}' already exists"
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
