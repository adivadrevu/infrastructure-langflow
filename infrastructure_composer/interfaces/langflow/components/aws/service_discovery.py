"""Service Discovery Component

Langflow component for creating AWS Service Discovery (Cloud Map) services.
"""

import json
from typing import Optional, Dict, Any
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
    from infrastructure_composer.shared.aws_client import create_servicediscovery_client
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from infrastructure_composer.shared.aws_client import create_servicediscovery_client


class ServiceDiscoveryComponent(Component):
    """Service Discovery Creation Component
    
    Creates a Service Discovery service in AWS Cloud Map.
    """
    
    display_name: str = "Service Discovery"
    description: str = "Create AWS Service Discovery (Cloud Map) service"
    documentation: str = "https://docs.aws.amazon.com/cloud-map/latest/dg/what-is-cloud-map.html"
    icon: str = "compass"
    priority: int = 55
    name: str = "service_discovery"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        StrInput(
            name="namespace_name",
            display_name="Namespace Name",
            info="Name of the Cloud Map namespace",
            required=True
        ),
        StrInput(
            name="service_name",
            display_name="Service Name",
            info="Name for the service discovery service",
            required=True
        ),
        StrInput(
            name="dns_config_json",
            display_name="DNS Config (JSON)",
            info='JSON object: {"namespaceId": "ns-xxx", "dnsRecords": [{"type": "A", "ttl": 60}], "routingPolicy": "MULTIVALUE"}',
            required=True
        ),
        StrInput(
            name="health_check_config_json",
            display_name="Health Check Config (JSON, Optional)",
            info='JSON object: {"type": "HTTP", "resourcePath": "/health", "failureThreshold": 2}',
            value="",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="service_discovery_output", display_name="Service Discovery Output", method="build_service_discovery"),
    ]
    
    def build_service_discovery(self) -> Data:
        """Create Service Discovery service and return output."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            sd_client = create_servicediscovery_client(creds)
            
            # Parse DNS config
            dns_config = json.loads(self.dns_config_json) if isinstance(self.dns_config_json, str) else self.dns_config_json
            
            # Prepare service creation parameters
            create_kwargs = {
                'Name': self.service_name,
                'DnsConfig': {
                    'NamespaceId': dns_config.get('namespaceId', ''),
                    'DnsRecords': dns_config.get('dnsRecords', [])
                }
            }
            
            if dns_config.get('routingPolicy'):
                create_kwargs['DnsConfig']['RoutingPolicy'] = dns_config.get('routingPolicy')
            
            # Add health check config if provided
            if self.health_check_config_json:
                health_check_config = json.loads(self.health_check_config_json) if isinstance(self.health_check_config_json, str) else self.health_check_config_json
                create_kwargs['HealthCheckConfig'] = {
                    'Type': health_check_config.get('type', 'HTTP'),
                    'ResourcePath': health_check_config.get('resourcePath', '/'),
                    'FailureThreshold': health_check_config.get('failureThreshold', 2)
                }
            
            # Create service
            response = sd_client.create_service(**create_kwargs)
            
            service = response.get('Service', {})
            service_arn = service.get('Arn', '')
            service_id = service.get('Id', '')
            namespace_id = dns_config.get('namespaceId', '')
            
            result = {
                'service_name': self.service_name,
                'service_arn': service_arn,
                'service_id': service_id,
                'namespace_id': namespace_id,
                'namespace_name': self.namespace_name,
                'status': 'created'
            }
            
            self.status = f"✓ Service Discovery service '{self.service_name}' created successfully"
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
