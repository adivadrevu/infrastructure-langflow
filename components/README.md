# Components Directory

This directory contains all Langflow custom components for AWS Infrastructure Composer.

## Directory Structure

```
components/
├── aws/                    # AWS Service Components
│   ├── credentials.py     # AWS Credentials input/validation
│   ├── vpc.py             # VPC creation
│   ├── ecs_cluster.py     # ECS Cluster
│   ├── ecs_service.py     # ECS Service with Task Definition
│   ├── alb.py             # Application Load Balancer
│   ├── security_group.py  # Security Groups
│   ├── ecr.py             # ECR Repository
│   ├── iam_role.py        # IAM Roles
│   └── service_discovery.py # Service Discovery (Cloud Map)
│
├── deployment/            # Deployment & Code Generation
│   ├── terraform_generator.py  # Generate Terraform HCL
│   ├── aws_deployer.py         # AWS SDK deployment orchestrator
│   └── validator.py            # Infrastructure validation
│
└── utils/                 # Shared utilities
    ├── aws_client.py      # boto3 client factory
    └── models.py          # Pydantic data models
```

## Component Categories in Langflow UI

Components will appear in Langflow UI under these categories:

- **aws** - All AWS service components (9 components)
- **deployment** - Deployment and code generation (3 components)

## All Available Components

### AWS Service Components (9)

1. **AWS Credentials** - Input and validate AWS credentials
2. **VPC** - Create Virtual Private Cloud with subnets, IGW, NAT Gateways
3. **ECS Cluster** - Create ECS clusters (Fargate/EC2)
4. **ECS Service** - Create ECS services with task definitions
5. **Application Load Balancer** - Create ALB with target groups and listeners
6. **Security Group** - Create security groups with ingress/egress rules
7. **ECR Repository** - Create container registries
8. **IAM Role** - Create IAM roles with policies
9. **Service Discovery** - Create Cloud Map services

### Deployment Components (3)

1. **Terraform Generator** - Generate Terraform HCL code
2. **AWS Deployer** - Orchestrate AWS resource deployment
3. **Infrastructure Validator** - Validate infrastructure design

## Making Components Visible

For components to appear in Langflow:

1. **Component files** must be in category folders (e.g., `aws/`, `deployment/`)
2. **`__init__.py`** files must import and export components using `__all__`
3. **Langflow** must be started with `--components-path ./components` or `LANGFLOW_COMPONENTS_PATH` set
4. **Restart Langflow** after adding new components

## Troubleshooting

If components don't appear:

1. Check `__init__.py` files have proper imports and `__all__` declarations
2. Verify `LANGFLOW_COMPONENTS_PATH` points to this directory
3. Restart Langflow server
4. Check Langflow logs for import errors
5. Verify component classes inherit from `Component` and have required attributes
