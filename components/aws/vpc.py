"""VPC Component

Langflow component for creating AWS VPC with subnets, Internet Gateway, NAT Gateways, and Route Tables.
"""

import json
from typing import Optional, Dict, Any
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, BoolInput, DataInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
from ..utils.models import AWSCredentials, VPCConfig
from ..utils.aws_client import create_ec2_client


class VPCComponent(Component):
    """VPC Creation Component
    
    Creates a VPC with subnets, Internet Gateway, NAT Gateways, and Route Tables.
    """
    
    display_name: str = "VPC"
    description: str = "Create AWS VPC (Virtual Private Cloud) with subnets, Internet Gateway, NAT Gateways, and Route Tables"
    documentation: str = "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html"
    icon: str = "Network"
    priority: int = 90
    name: str = "vpc"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        StrInput(
            name="name",
            display_name="VPC Name",
            info="Name for the VPC",
            required=True
        ),
        StrInput(
            name="cidr_block",
            display_name="CIDR Block",
            info="CIDR block for VPC (e.g., 10.0.0.0/16)",
            value="10.0.0.0/16",
            required=True
        ),
        BoolInput(
            name="enable_dns_hostnames",
            display_name="Enable DNS Hostnames",
            value=True,
            required=False
        ),
        BoolInput(
            name="enable_dns_support",
            display_name="Enable DNS Support",
            value=True,
            required=False
        ),
        StrInput(
            name="subnets_json",
            display_name="Subnets (JSON)",
            info='JSON array of subnets: [{"name": "subnet1", "cidrBlock": "10.0.1.0/24", "availabilityZone": "us-east-1a", "type": "public"}]',
            value="[]",
            required=False
        ),
        StrInput(
            name="create_internet_gateway",
            display_name="Create Internet Gateway",
            info="Whether to create an Internet Gateway",
            value="true",
            required=False
        ),
        StrInput(
            name="nat_gateways_json",
            display_name="NAT Gateways (JSON)",
            info='JSON array of NAT gateways: [{"name": "nat1", "subnetId": "subnet-xxx", "allocationId": "eipalloc-xxx"}]',
            value="[]",
            required=False
        ),
        StrInput(
            name="route_tables_json",
            display_name="Route Tables (JSON)",
            info='JSON array of route tables: [{"name": "rt1", "routes": [{"destinationCidrBlock": "0.0.0.0/0", "gatewayId": "igw-xxx"}], "associations": ["subnet-xxx"]}]',
            value="[]",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="vpc_output", display_name="VPC Output", method="build_vpc"),
    ]
    
    def build_vpc(self) -> Data:
        """Create VPC and return output with VPC ID, ARN, and subnet IDs."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            ec2_client = create_ec2_client(creds)
            
            # Create VPC
            vpc_response = ec2_client.create_vpc(
                CidrBlock=self.cidr_block,
                TagSpecifications=[{
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': self.name},
                        {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                    ]
                }]
            )
            
            vpc_id = vpc_response['Vpc']['VpcId']
            vpc_arn = vpc_response['Vpc']['VpcArn']
            
            # Enable DNS hostnames and support
            if self.enable_dns_hostnames:
                ec2_client.modify_vpc_attribute(
                    VpcId=vpc_id,
                    EnableDnsHostnames={'Value': True}
                )
            
            if self.enable_dns_support:
                ec2_client.modify_vpc_attribute(
                    VpcId=vpc_id,
                    EnableDnsSupport={'Value': True}
                )
            
            # Create subnets
            subnet_ids = []
            subnets_data = json.loads(self.subnets_json) if self.subnets_json else []
            
            for subnet_data in subnets_data:
                subnet_response = ec2_client.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=subnet_data.get('cidrBlock'),
                    AvailabilityZone=subnet_data.get('availabilityZone'),
                    TagSpecifications=[{
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': subnet_data.get('name', 'subnet')},
                            {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                        ]
                    }]
                )
                subnet_ids.append(subnet_response['Subnet']['SubnetId'])
            
            # Create Internet Gateway if requested
            internet_gateway_id = None
            if self.create_internet_gateway.lower() == 'true':
                igw_response = ec2_client.create_internet_gateway(
                    TagSpecifications=[{
                        'ResourceType': 'internet-gateway',
                        'Tags': [
                            {'Key': 'Name', 'Value': f"{self.name}-igw"},
                            {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                        ]
                    }]
                )
                internet_gateway_id = igw_response['InternetGateway']['InternetGatewayId']
                
                # Attach to VPC
                ec2_client.attach_internet_gateway(
                    InternetGatewayId=internet_gateway_id,
                    VpcId=vpc_id
                )
            
            # Create NAT Gateways
            nat_gateway_ids = []
            nat_gateways_data = json.loads(self.nat_gateways_json) if self.nat_gateways_json else []
            
            for nat_data in nat_gateways_data:
                nat_response = ec2_client.create_nat_gateway(
                    SubnetId=nat_data.get('subnetId'),
                    AllocationId=nat_data.get('allocationId'),
                    TagSpecifications=[{
                        'ResourceType': 'natgateway',
                        'Tags': [
                            {'Key': 'Name', 'Value': nat_data.get('name', 'nat')},
                            {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                        ]
                    }]
                )
                nat_gateway_ids.append(nat_response['NatGateway']['NatGatewayId'])
            
            # Create Route Tables
            route_table_ids = []
            route_tables_data = json.loads(self.route_tables_json) if self.route_tables_json else []
            
            for rt_data in route_tables_data:
                rt_response = ec2_client.create_route_table(
                    VpcId=vpc_id,
                    TagSpecifications=[{
                        'ResourceType': 'route-table',
                        'Tags': [
                            {'Key': 'Name', 'Value': rt_data.get('name', 'rt')},
                            {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                        ]
                    }]
                )
                route_table_id = rt_response['RouteTable']['RouteTableId']
                route_table_ids.append(route_table_id)
                
                # Create routes
                for route in rt_data.get('routes', []):
                    route_kwargs = {
                        'RouteTableId': route_table_id,
                        'DestinationCidrBlock': route.get('destinationCidrBlock')
                    }
                    if route.get('gatewayId'):
                        route_kwargs['GatewayId'] = route.get('gatewayId')
                    if route.get('natGatewayId'):
                        route_kwargs['NatGatewayId'] = route.get('natGatewayId')
                    
                    ec2_client.create_route(**route_kwargs)
                
                # Associate with subnets
                for subnet_id in rt_data.get('associations', []):
                    ec2_client.associate_route_table(
                        RouteTableId=route_table_id,
                        SubnetId=subnet_id
                    )
            
            result = {
                'vpc_id': vpc_id,
                'vpc_arn': vpc_arn,
                'vpc_name': self.name,
                'subnet_ids': subnet_ids,
                'internet_gateway_id': internet_gateway_id,
                'nat_gateway_ids': nat_gateway_ids,
                'route_table_ids': route_table_ids,
                'status': 'created'
            }
            
            self.status = f"✓ VPC '{self.name}' created successfully (ID: {vpc_id})"
            return Data(data=result)
            
        except ClientError as e:
            error_msg = f"AWS Error: {e.response.get('Error', {}).get('Message', str(e))}"
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
