"""Pydantic models for AWS Infrastructure Composer

These models mirror the TypeScript interfaces from the Next.js app.
"""

from typing import Optional, List, Dict, Literal, Any
from pydantic import BaseModel, Field


# Environment and Service Types
Environment = Literal['sbx', 'live']
ServiceType = Literal['vpc', 'ecs-cluster', 'ecs-service', 'alb', 'security-group', 'ecr', 'iam-role', 'service-discovery']


# AWS Credentials
class AWSCredentials(BaseModel):
    access_key_id: str = Field(..., alias='accessKeyId')
    secret_access_key: str = Field(..., alias='secretAccessKey')
    region: str
    session_token: Optional[str] = Field(None, alias='sessionToken')

    class Config:
        allow_population_by_field_name = True


# Infrastructure Metadata
class InfrastructureMetadata(BaseModel):
    name: str
    environment: Environment
    region: str
    account_id: Optional[str] = Field(None, alias='accountId')

    class Config:
        allow_population_by_field_name = True


# VPC Configuration
class SubnetConfig(BaseModel):
    id: Optional[str] = None
    name: str
    cidr_block: str = Field(..., alias='cidrBlock')
    availability_zone: str = Field(..., alias='availabilityZone')
    type: Literal['public', 'private']
    map_public_ip_on_launch: Optional[bool] = Field(None, alias='mapPublicIpOnLaunch')

    class Config:
        allow_population_by_field_name = True


class InternetGatewayConfig(BaseModel):
    id: Optional[str] = None
    name: str


class NATGatewayConfig(BaseModel):
    id: Optional[str] = None
    name: str
    subnet_id: str = Field(..., alias='subnetId')
    allocation_id: Optional[str] = Field(None, alias='allocationId')

    class Config:
        allow_population_by_field_name = True


class RouteConfig(BaseModel):
    destination_cidr_block: str = Field(..., alias='destinationCidrBlock')
    gateway_id: Optional[str] = Field(None, alias='gatewayId')
    nat_gateway_id: Optional[str] = Field(None, alias='natGatewayId')

    class Config:
        allow_population_by_field_name = True


class RouteTableConfig(BaseModel):
    id: Optional[str] = None
    name: str
    routes: List[RouteConfig]
    associations: List[str]  # subnet IDs


class VPCConfig(BaseModel):
    id: Optional[str] = None
    cidr_block: str = Field(..., alias='cidrBlock')
    enable_dns_hostnames: bool = Field(..., alias='enableDnsHostnames')
    enable_dns_support: bool = Field(..., alias='enableDnsSupport')
    subnets: List[SubnetConfig]
    internet_gateway: Optional[InternetGatewayConfig] = Field(None, alias='internetGateway')
    nat_gateways: List[NATGatewayConfig] = Field(..., alias='natGateways')
    route_tables: List[RouteTableConfig] = Field(..., alias='routeTables')

    class Config:
        allow_population_by_field_name = True


# ECS Configuration
class ECSClusterConfig(BaseModel):
    id: Optional[str] = None
    name: str
    launch_type: Literal['FARGATE', 'EC2'] = Field(..., alias='launchType')
    capacity_providers: Optional[List[str]] = Field(None, alias='capacityProviders')
    enable_container_insights: bool = Field(..., alias='enableContainerInsights')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


class PortMapping(BaseModel):
    container_port: int = Field(..., alias='containerPort')
    host_port: Optional[int] = Field(None, alias='hostPort')
    protocol: Literal['tcp', 'udp']

    class Config:
        allow_population_by_field_name = True


class EnvironmentVariable(BaseModel):
    name: str
    value: str


class Secret(BaseModel):
    name: str
    value_from: str = Field(..., alias='valueFrom')  # ARN

    class Config:
        allow_population_by_field_name = True


class LogConfiguration(BaseModel):
    log_driver: Literal['awslogs'] = Field(..., alias='logDriver')
    options: Dict[str, str]

    class Config:
        allow_population_by_field_name = True


class HealthCheck(BaseModel):
    command: List[str]
    interval: int
    timeout: int
    retries: int
    start_period: int = Field(..., alias='startPeriod')

    class Config:
        allow_population_by_field_name = True


class ResourceRequirement(BaseModel):
    type: Literal['GPU']
    value: str


class EFSVolumeConfiguration(BaseModel):
    file_system_id: str = Field(..., alias='fileSystemId')
    root_directory: str = Field(..., alias='rootDirectory')
    transit_encryption: Optional[Literal['ENABLED', 'DISABLED']] = Field(None, alias='transitEncryption')

    class Config:
        allow_population_by_field_name = True


class Volume(BaseModel):
    name: str
    efs_volume_configuration: Optional[EFSVolumeConfiguration] = Field(None, alias='efsVolumeConfiguration')

    class Config:
        allow_population_by_field_name = True


class ContainerDefinition(BaseModel):
    name: str
    image: str
    essential: bool
    port_mappings: List[PortMapping] = Field(..., alias='portMappings')
    environment: Optional[List[EnvironmentVariable]] = None
    secrets: Optional[List[Secret]] = None
    log_configuration: Optional[LogConfiguration] = Field(None, alias='logConfiguration')
    health_check: Optional[HealthCheck] = Field(None, alias='healthCheck')
    resource_requirements: Optional[List[ResourceRequirement]] = Field(None, alias='resourceRequirements')

    class Config:
        allow_population_by_field_name = True


class TaskDefinitionConfig(BaseModel):
    family: str
    cpu: str
    memory: str
    network_mode: Literal['awsvpc'] = Field(..., alias='networkMode')
    requires_compatibilities: List[Literal['FARGATE', 'EC2']] = Field(..., alias='requiresCompatibilities')
    execution_role_arn: Optional[str] = Field(None, alias='executionRoleArn')
    task_role_arn: Optional[str] = Field(None, alias='taskRoleArn')
    container_definitions: List[ContainerDefinition] = Field(..., alias='containerDefinitions')
    volumes: Optional[List[Volume]] = None

    class Config:
        allow_population_by_field_name = True


class LoadBalancerConfig(BaseModel):
    target_group_arn: Optional[str] = Field(None, alias='targetGroupArn')
    target_group_name: str = Field(..., alias='targetGroupName')
    container_name: str = Field(..., alias='containerName')
    container_port: int = Field(..., alias='containerPort')

    class Config:
        allow_population_by_field_name = True


class ScalingPolicy(BaseModel):
    target_value: float = Field(..., alias='targetValue')
    scale_in_cooldown: Optional[int] = Field(None, alias='scaleInCooldown')
    scale_out_cooldown: Optional[int] = Field(None, alias='scaleOutCooldown')
    metric_type: Literal['CPUUtilization', 'MemoryUtilization', 'ApproximateNumberOfMessagesVisible'] = Field(..., alias='metricType')

    class Config:
        allow_population_by_field_name = True


class AutoscalingConfig(BaseModel):
    min_capacity: int = Field(..., alias='minCapacity')
    max_capacity: int = Field(..., alias='maxCapacity')
    target_tracking_scaling_policies: List[ScalingPolicy] = Field(..., alias='targetTrackingScalingPolicies')

    class Config:
        allow_population_by_field_name = True


class DeploymentConfiguration(BaseModel):
    maximum_percent: int = Field(..., alias='maximumPercent')
    minimum_healthy_percent: int = Field(..., alias='minimumHealthyPercent')
    deployment_circuit_breaker: Optional[Dict[str, bool]] = Field(None, alias='deploymentCircuitBreaker')

    class Config:
        allow_population_by_field_name = True


class ECSServiceConfig(BaseModel):
    id: Optional[str] = None
    name: str
    cluster_name: str = Field(..., alias='clusterName')
    task_definition: TaskDefinitionConfig = Field(..., alias='taskDefinition')
    desired_count: int = Field(..., alias='desiredCount')
    launch_type: Literal['FARGATE', 'EC2'] = Field(..., alias='launchType')
    load_balancer: Optional[LoadBalancerConfig] = Field(None, alias='loadBalancer')
    service_discovery: Optional[Dict[str, Any]] = Field(None, alias='serviceDiscovery')
    autoscaling: Optional[AutoscalingConfig] = None
    deployment_configuration: Optional[DeploymentConfiguration] = Field(None, alias='deploymentConfiguration')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


# ALB Configuration
class ListenerAction(BaseModel):
    type: Literal['forward']
    target_group_arn: Optional[str] = Field(None, alias='targetGroupArn')
    target_group_name: Optional[str] = Field(None, alias='targetGroupName')

    class Config:
        allow_population_by_field_name = True


class ListenerConfig(BaseModel):
    port: int
    protocol: Literal['HTTP', 'HTTPS']
    default_actions: List[ListenerAction] = Field(..., alias='defaultActions')
    certificates: Optional[List[str]] = None

    class Config:
        allow_population_by_field_name = True


class HealthCheckConfig(BaseModel):
    enabled: bool
    path: str
    protocol: Literal['HTTP', 'HTTPS']
    port: int
    interval_seconds: int = Field(..., alias='intervalSeconds')
    timeout_seconds: int = Field(..., alias='timeoutSeconds')
    healthy_threshold_count: int = Field(..., alias='healthyThresholdCount')
    unhealthy_threshold_count: int = Field(..., alias='unhealthyThresholdCount')
    matcher: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


class TargetGroupConfig(BaseModel):
    id: Optional[str] = None
    name: str
    target_type: Literal['ip', 'instance'] = Field(..., alias='targetType')
    protocol: Literal['HTTP', 'HTTPS']
    port: int
    vpc_id: str = Field(..., alias='vpcId')
    health_check: HealthCheckConfig = Field(..., alias='healthCheck')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


class ALBConfig(BaseModel):
    id: Optional[str] = None
    name: str
    scheme: Literal['internet-facing', 'internal']
    type: Literal['application']
    subnets: List[str]  # subnet IDs
    security_groups: List[str] = Field(..., alias='securityGroups')  # security group IDs
    listeners: List[ListenerConfig]
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


# Security Group Configuration
class SecurityGroupRule(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    from_port: Optional[int] = Field(None, alias='fromPort')
    to_port: Optional[int] = Field(None, alias='toPort')
    protocol: Literal['tcp', 'udp', 'icmp', '-1']
    cidr_blocks: Optional[List[str]] = Field(None, alias='cidrBlocks')
    source_security_group_id: Optional[str] = Field(None, alias='sourceSecurityGroupId')
    destination_security_group_id: Optional[str] = Field(None, alias='destinationSecurityGroupId')

    class Config:
        allow_population_by_field_name = True


class SecurityGroupConfig(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    vpc_id: str = Field(..., alias='vpcId')
    ingress_rules: List[SecurityGroupRule] = Field(..., alias='ingressRules')
    egress_rules: List[SecurityGroupRule] = Field(..., alias='egressRules')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


# ECR Configuration
class EncryptionConfiguration(BaseModel):
    encryption_type: Literal['AES256', 'KMS'] = Field(..., alias='encryptionType')
    kms_key: Optional[str] = Field(None, alias='kmsKey')

    class Config:
        allow_population_by_field_name = True


class ECRConfig(BaseModel):
    id: Optional[str] = None
    name: str
    image_tag_mutability: Literal['MUTABLE', 'IMMUTABLE'] = Field(..., alias='imageTagMutability')
    image_scanning_configuration: Optional[Dict[str, bool]] = Field(None, alias='imageScanningConfiguration')
    encryption_configurations: Optional[List[EncryptionConfiguration]] = Field(None, alias='encryptionConfigurations')
    lifecycle_policy: Optional[str] = Field(None, alias='lifecyclePolicy')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


# IAM Configuration
class IAMPolicy(BaseModel):
    name: str
    policy_document: str = Field(..., alias='policyDocument')  # JSON string

    class Config:
        allow_population_by_field_name = True


class IAMRoleConfig(BaseModel):
    id: Optional[str] = None
    name: str
    assume_role_policy_document: str = Field(..., alias='assumeRolePolicyDocument')  # JSON string
    policies: List[IAMPolicy]
    managed_policy_arns: Optional[List[str]] = Field(None, alias='managedPolicyArns')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


# Service Discovery Configuration
class DNSRecord(BaseModel):
    type: Literal['A', 'AAAA', 'SRV']
    ttl: int


class ServiceDiscoveryConfig(BaseModel):
    id: Optional[str] = None
    namespace: str
    service_name: str = Field(..., alias='serviceName')
    dns_config: Dict[str, Any] = Field(..., alias='dnsConfig')
    health_check_config: Optional[Dict[str, Any]] = Field(None, alias='healthCheckConfig')
    tags: Optional[Dict[str, str]] = None

    class Config:
        allow_population_by_field_name = True


# Connection and Infrastructure
class Connection(BaseModel):
    id: str
    source: str  # service/node ID
    target: str  # service/node ID
    type: Literal['routes-to', 'depends-on', 'uses']
    label: Optional[str] = None


class Infrastructure(BaseModel):
    metadata: InfrastructureMetadata
    vpc: Optional[VPCConfig] = None
    clusters: List[ECSClusterConfig]
    services: List[ECSServiceConfig]
    load_balancers: List[ALBConfig]
    target_groups: List[TargetGroupConfig] = Field(..., alias='targetGroups')
    security_groups: List[SecurityGroupConfig] = Field(..., alias='securityGroups')
    iam_roles: List[IAMRoleConfig] = Field(..., alias='iamRoles')
    service_discovery: Optional[Dict[str, Any]] = Field(None, alias='serviceDiscovery')
    ecr_repositories: List[ECRConfig] = Field(..., alias='ecrRepositories')
    connections: List[Connection]

    class Config:
        allow_population_by_field_name = True


# Deployment Results
class DeployedResource(BaseModel):
    type: str
    id: str
    arn: Optional[str] = None
    name: str


class DeploymentError(BaseModel):
    resource: str
    message: str
    code: Optional[str] = None


class DeploymentResult(BaseModel):
    success: bool
    resources: List[DeployedResource]
    errors: Optional[List[DeploymentError]] = None
    terraform_state: Optional[str] = Field(None, alias='terraformState')

    class Config:
        allow_population_by_field_name = True
