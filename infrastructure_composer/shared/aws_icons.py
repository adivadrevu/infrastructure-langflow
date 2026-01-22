"""AWS Icon Utilities

Provides AWS icon paths using aws-arch (AWS PDK).
Note: Langflow uses Lucide icons by default. For AWS-branded icons,
you would need to create a Langflow bundle with custom icon components.
"""

try:
    from aws_pdk.aws_arch import AwsArchitecture
    
    # Map component names to CloudFormation resource types
    COMPONENT_TO_CFN = {
        "vpc": "AWS::EC2::VPC",
        "ecs_cluster": "AWS::ECS::Cluster",
        "ecs_service": "AWS::ECS::Service", 
        "alb": "AWS::ElasticLoadBalancingV2::LoadBalancer",
        "ecr": "AWS::ECR::Repository",
        "iam_role": "AWS::IAM::Role",
        "security_group": "AWS::EC2::SecurityGroup",
        "service_discovery": "AWS::ServiceDiscovery::Service",
        "aws_credentials": None,  # No CFN type for credentials
    }
    
    def get_aws_icon_path(component_name: str, format: str = "svg") -> str:
        """Get AWS icon path for a component.
        
        Args:
            component_name: Component name (e.g., 'vpc', 'ecs_cluster')
            format: Icon format ('svg' or 'png')
            
        Returns:
            Relative icon path or None if not found
        """
        cfn_type = COMPONENT_TO_CFN.get(component_name)
        if not cfn_type:
            return None
            
        try:
            resource = AwsArchitecture.get_resource(cfn_type)
            return resource.icon(format)
        except Exception:
            return None
    
    def get_aws_icon_absolute_path(component_name: str, format: str = "svg") -> str:
        """Get absolute path to AWS icon file.
        
        Args:
            component_name: Component name
            format: Icon format ('svg' or 'png')
            
        Returns:
            Absolute file path or None if not found
        """
        icon_path = get_aws_icon_path(component_name, format)
        if not icon_path:
            return None
            
        try:
            return AwsArchitecture.resolve_asset_path(icon_path)
        except Exception:
            return None

except ImportError:
    # aws-pdk not installed, provide fallback
    def get_aws_icon_path(component_name: str, format: str = "svg") -> str:
        return None
    
    def get_aws_icon_absolute_path(component_name: str, format: str = "svg") -> str:
        return None

