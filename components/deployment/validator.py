"""Infrastructure Validator Component

Langflow component for validating infrastructure design before deployment.
"""

import json
import re
from typing import Optional, Dict, Any, List
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema import Data


class ValidatorComponent(Component):
    """Infrastructure Validator Component
    
    Validates infrastructure design for errors and warnings before deployment.
    """
    
    display_name: str = "Infrastructure Validator"
    description: str = "Validate infrastructure design for errors and warnings"
    documentation: str = "https://docs.aws.amazon.com/"
    icon: str = "CheckCircle"
    priority: int = 40
    name: str = "validator"
    
    inputs = [
        DataInput(
            name="infrastructure_data",
            display_name="Infrastructure Data",
            info="Infrastructure data from connected components (JSON or dict)",
            required=True
        ),
    ]
    
    outputs = [
        Output(name="validation_result", display_name="Validation Result", method="build_validation"),
    ]
    
    def build_validation(self) -> Data:
        """Validate infrastructure and return validation result."""
        try:
            # Parse infrastructure data
            if isinstance(self.infrastructure_data, str):
                infra_data = json.loads(self.infrastructure_data)
            else:
                infra_data = self.infrastructure_data if isinstance(self.infrastructure_data, dict) else {}
            
            errors: List[Dict[str, Any]] = []
            warnings: List[Dict[str, Any]] = []
            
            # Check for empty infrastructure
            if not infra_data:
                errors.append({
                    'severity': 'error',
                    'message': 'Infrastructure data is empty',
                    'node_id': None
                })
                self.status = "✗ Validation failed: Empty infrastructure"
                return Data(data={
                    'is_valid': False,
                    'errors': errors,
                    'warnings': warnings
                })
            
            # Validate VPC
            if infra_data.get('vpc'):
                vpc_errors = self._validate_vpc(infra_data.get('vpc'))
                errors.extend(vpc_errors)
            
            # Validate ECS Cluster
            if infra_data.get('clusters'):
                for cluster in infra_data.get('clusters', []):
                    cluster_errors = self._validate_ecs_cluster(cluster)
                    errors.extend(cluster_errors)
            
            # Validate ECS Service
            if infra_data.get('services'):
                for service in infra_data.get('services', []):
                    service_errors = self._validate_ecs_service(service)
                    errors.extend(service_errors)
                    
                    # Check if service has cluster
                    if not infra_data.get('clusters'):
                        errors.append({
                            'severity': 'error',
                            'message': f"ECS Service '{service.get('name', 'unknown')}' requires an ECS Cluster",
                            'node_id': service.get('id')
                        })
            
            # Validate ALB
            if infra_data.get('load_balancers'):
                for alb in infra_data.get('load_balancers', []):
                    alb_errors = self._validate_alb(alb)
                    errors.extend(alb_errors)
            
            # Validate Security Groups
            if infra_data.get('security_groups'):
                for sg in infra_data.get('security_groups', []):
                    sg_errors = self._validate_security_group(sg)
                    errors.extend(sg_errors)
            
            is_valid = len([e for e in errors if e.get('severity') == 'error']) == 0
            
            if is_valid:
                self.status = f"✓ Validation passed ({len(warnings)} warnings)"
            else:
                self.status = f"✗ Validation failed: {len(errors)} errors, {len(warnings)} warnings"
            
            return Data(data={
                'is_valid': is_valid,
                'errors': errors,
                'warnings': warnings
            })
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data(data={
                'is_valid': False,
                'errors': [{
                    'severity': 'error',
                    'message': error_msg,
                    'node_id': None
                }],
                'warnings': []
            })
    
    def _validate_vpc(self, vpc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate VPC configuration."""
        errors = []
        
        if not vpc.get('cidr_block'):
            errors.append({
                'severity': 'error',
                'message': 'VPC: CIDR block is required',
                'node_id': vpc.get('id')
            })
        elif not self._is_valid_cidr(vpc.get('cidr_block')):
            errors.append({
                'severity': 'error',
                'message': 'VPC: Valid CIDR block is required (e.g., 10.0.0.0/16)',
                'node_id': vpc.get('id')
            })
        
        return errors
    
    def _validate_ecs_cluster(self, cluster: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate ECS Cluster configuration."""
        errors = []
        
        if not cluster.get('name'):
            errors.append({
                'severity': 'error',
                'message': 'ECS Cluster: Name is required',
                'node_id': cluster.get('id')
            })
        
        return errors
    
    def _validate_ecs_service(self, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate ECS Service configuration."""
        errors = []
        
        if not service.get('name'):
            errors.append({
                'severity': 'error',
                'message': 'ECS Service: Name is required',
                'node_id': service.get('id')
            })
        
        task_def = service.get('task_definition', {})
        if not task_def.get('cpu') or not task_def.get('memory'):
            errors.append({
                'severity': 'error',
                'message': 'ECS Service: CPU and Memory are required',
                'node_id': service.get('id')
            })
        
        container_defs = task_def.get('container_definitions', [])
        if container_defs:
            for container in container_defs:
                port_mappings = container.get('port_mappings', [])
                if port_mappings:
                    for pm in port_mappings:
                        port = pm.get('container_port')
                        if not port or port < 1 or port > 65535:
                            errors.append({
                                'severity': 'error',
                                'message': f"ECS Service: Valid port number is required (1-65535), got {port}",
                                'node_id': service.get('id')
                            })
        
        return errors
    
    def _validate_alb(self, alb: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate ALB configuration."""
        errors = []
        
        if not alb.get('scheme'):
            errors.append({
                'severity': 'error',
                'message': 'ALB: Scheme is required',
                'node_id': alb.get('id')
            })
        
        if not alb.get('subnets'):
            errors.append({
                'severity': 'error',
                'message': 'ALB: At least one subnet is required',
                'node_id': alb.get('id')
            })
        
        return errors
    
    def _validate_security_group(self, sg: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Security Group configuration."""
        errors = []
        
        if not sg.get('name'):
            errors.append({
                'severity': 'error',
                'message': 'Security Group: Name is required',
                'node_id': sg.get('id')
            })
        
        if not sg.get('vpc_id'):
            errors.append({
                'severity': 'error',
                'message': 'Security Group: VPC ID is required',
                'node_id': sg.get('id')
            })
        
        return errors
    
    def _is_valid_cidr(self, cidr: str) -> bool:
        """Validate CIDR block format."""
        cidr_regex = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        if not re.match(cidr_regex, cidr):
            return False
        
        try:
            ip, prefix = cidr.split('/')
            prefix_num = int(prefix)
            if prefix_num < 0 or prefix_num > 32:
                return False
            
            parts = [int(p) for p in ip.split('.')]
            return all(0 <= p <= 255 for p in parts)
        except:
            return False
