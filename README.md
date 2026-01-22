# AWS Infrastructure Composer - Langflow

A visual drag-and-drop tool for designing and deploying AWS infrastructure using Langflow. Build infrastructure workflows visually with components for VPC, ECS, ALB, Security Groups, ECR, IAM Roles, and Service Discovery.

## Features

- **Visual Workflow Builder**: Design infrastructure using Langflow's intuitive drag-and-drop interface
- **AWS Service Components**: Pre-built components for all major AWS services
- **Direct Deployment**: Deploy infrastructure directly to AWS using boto3
- **Terraform Generation**: Export infrastructure as Terraform HCL code
- **Infrastructure Validation**: Validate your infrastructure design before deployment
- **Multi-Environment Support**: Support for sandbox (sbx) and live (prod) environments

## Supported AWS Services

- **Networking**: VPC, Subnets, Internet Gateway, NAT Gateway, Route Tables
- **Compute**: ECS Cluster, ECS Service, Task Definitions
- **Load Balancing**: Application Load Balancer (ALB), Target Groups, Listeners
- **Security**: Security Groups, IAM Roles, IAM Policies
- **Container Registry**: ECR Repositories
- **Service Discovery**: AWS Cloud Map

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS Account with appropriate IAM permissions
- Langflow installed

### Setup

1. **Clone or navigate to the project directory:**
```bash
cd infrastructure-composer-langflow
```

2. **Install dependencies:**
```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended, faster)
uv pip install -r requirements.txt
```

**Note on Dependencies:** 
- `langflow` will install ~500+ packages as it includes many optional integrations (LLM providers, vector databases, langchain integrations, etc.). This is **expected behavior** for the full Langflow framework.
- Our components only require: `langflow`, `boto3`, `pydantic` (and `jinja2` optionally)
- The large dependency tree comes from Langflow's optional features, not our code

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and set LANGFLOW_COMPONENTS_PATH
```

4. **Start Langflow with custom components:**
```bash
langflow run --components-path ./components
```

5. **Access Langflow UI:**
Open your browser to `http://localhost:7860`

## Quick Start Guide

**New to Langflow?** See the detailed [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for step-by-step instructions.

### Quick Steps:
1. Open `http://localhost:7860` in your browser
2. Drag **AWS Credentials** component → Enter your AWS credentials
3. Drag **VPC** component → Connect credentials → Configure (name, CIDR block)
4. Drag **Security Group** → Connect VPC and credentials → Configure rules
5. Drag **ECS Cluster** → Connect credentials → Configure
6. Drag **ECS Service** → Connect cluster, VPC, security group → Configure
7. Click **Run** on each component to deploy

## Usage

### 1. Configure AWS Credentials

- Drag the **AWS Credentials** component onto the canvas
- Enter your AWS Access Key ID, Secret Access Key, and Region
- Optionally validate credentials using the validation output

### 2. Design Infrastructure

- Drag AWS service components from the sidebar:
  - **VPC**: Create Virtual Private Cloud
  - **ECS Cluster**: Create ECS cluster
  - **ECS Service**: Create ECS service with task definition
  - **ALB**: Create Application Load Balancer
  - **Security Group**: Create security groups with rules
  - **ECR**: Create container registry
  - **IAM Role**: Create IAM roles with policies
  - **Service Discovery**: Create Cloud Map services

### 3. Connect Components

- Connect components using edges:
  - Credentials → All AWS service components
  - VPC → Security Group, ALB, ECS Service
  - ECS Cluster → ECS Service
  - ALB → ECS Service (for load balancing)

### 4. Configure Components

- Click on each component to configure:
  - Names, CIDR blocks, ports, resource sizes
  - JSON inputs for complex configurations (subnets, rules, policies)

### 5. Validate Infrastructure

- Connect components to the **Infrastructure Validator**
- Review validation results for errors and warnings

### 6. Generate Terraform

- Connect components to the **Terraform Generator**
- Specify environment (sbx/live) and region
- Get Terraform code outputs (main.tf, variables.tf, outputs.tf, README.md)

### 7. Deploy to AWS

- Components deploy resources directly when executed
- Or use the **AWS Deployer** component to orchestrate deployment
- Review deployment results for success/failure status

## Component Reference

### AWS Service Components

#### AWS Credentials
- **Inputs**: Access Key ID, Secret Access Key, Region, Session Token (optional)
- **Outputs**: Credentials object, Validation result

#### VPC
- **Inputs**: Name, CIDR Block, DNS settings, Subnets (JSON), Internet Gateway, NAT Gateways (JSON), Route Tables (JSON)
- **Outputs**: VPC ID, VPC ARN, Subnet IDs, Internet Gateway ID, NAT Gateway IDs

#### ECS Cluster
- **Inputs**: Name, Launch Type (FARGATE/EC2), Container Insights, Tags (JSON)
- **Outputs**: Cluster Name, Cluster ARN

#### ECS Service
- **Inputs**: Service Name, Cluster Output, Task Family, Container Config, CPU, Memory, Port, Desired Count, Subnet IDs, Security Group IDs
- **Outputs**: Service Name, Service ARN, Task Definition ARN

#### ALB
- **Inputs**: Name, Scheme, Subnet IDs, Security Group IDs, Listener Config, Target Group Config
- **Outputs**: Load Balancer ARN, DNS Name, Target Group ARN

#### Security Group
- **Inputs**: Name, Description, VPC Output, Ingress Rules (JSON), Egress Rules (JSON)
- **Outputs**: Security Group ID, Security Group ARN

#### ECR
- **Inputs**: Name, Image Tag Mutability, Scan on Push, Encryption Type, Lifecycle Policy (JSON)
- **Outputs**: Repository URI, Repository ARN

#### IAM Role
- **Inputs**: Name, Assume Role Policy (JSON), Inline Policies (JSON), Managed Policy ARNs (JSON)
- **Outputs**: Role ARN, Role Name

#### Service Discovery
- **Inputs**: Namespace Name, Service Name, DNS Config (JSON), Health Check Config (JSON)
- **Outputs**: Service ARN, Service ID, Namespace ID

### Deployment Components

#### Terraform Generator
- **Inputs**: Infrastructure Data, Environment, Region
- **Outputs**: Terraform Code (main.tf), Variables (variables.tf), Outputs (outputs.tf), README

#### AWS Deployer
- **Inputs**: Credentials, Infrastructure Data, Environment, Region
- **Outputs**: Deployment Result (success, resources, errors)

#### Infrastructure Validator
- **Inputs**: Infrastructure Data
- **Outputs**: Validation Result (is_valid, errors, warnings)

## JSON Input Formats

### Subnets
```json
[
  {
    "name": "public-subnet-1",
    "cidrBlock": "10.0.1.0/24",
    "availabilityZone": "us-east-1a",
    "type": "public"
  }
]
```

### Security Group Rules
```json
[
  {
    "fromPort": 80,
    "toPort": 80,
    "protocol": "tcp",
    "cidrBlocks": ["0.0.0.0/0"],
    "description": "HTTP access"
  }
]
```

### IAM Policies
```json
[
  {
    "name": "S3ReadPolicy",
    "policyDocument": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": ["s3:GetObject"],
          "Resource": ["arn:aws:s3:::bucket/*"]
        }
      ]
    }
  }
]
```

## Project Structure

```
infrastructure-composer-langflow/
├── components/
│   ├── aws/              # AWS service components
│   ├── deployment/        # Deployment and validation components
│   └── utils/             # Shared utilities and models
├── requirements.txt
├── README.md
├── SETUP.md
└── .env.example
```

## Security Notes

- **Never commit AWS credentials** to version control
- Use environment variables or Langflow's credential management
- Use IAM roles with least privilege principles
- Validate credentials before deploying resources
- Review generated Terraform code before applying

## Development

### Adding New Components

1. Create a new component file in `components/aws/` or `components/deployment/`
2. Inherit from `Component` class
3. Define `display_name`, `description`, `icon`, `name`
4. Define `inputs` and `outputs`
5. Implement build methods
6. Add error handling and status messages

### Testing Components

1. Start Langflow: `langflow run --components-path ./components`
2. Drag component onto canvas
3. Configure inputs
4. Execute and verify outputs
5. Test error cases

## Troubleshooting

### Components Not Appearing

- Verify `LANGFLOW_COMPONENTS_PATH` is set correctly
- Check that `__init__.py` files exist in component directories
- Restart Langflow after adding new components
- Check Langflow logs for import errors

### AWS Errors

- Verify credentials are valid using the credentials component
- Check IAM permissions for the AWS account
- Review AWS service quotas and limits
- Check region availability for services

### JSON Parse Errors

- Validate JSON syntax before pasting into components
- Use JSON validators for complex configurations
- Check for trailing commas and proper escaping

## License

This project is for personal use. Adapt as needed for your infrastructure needs.

## Contributing

This is a personal project. Feel free to fork and adapt for your own use.
