# Quick Reference - Finding Components in Langflow UI

## All 12 Components Available

### AWS Category (9 components)
These should appear in an **"aws"** category in the left sidebar:

1. **AWS Credentials** - Input and validate AWS credentials
2. **VPC** - Create Virtual Private Cloud
3. **ECS Cluster** - Create ECS cluster
4. **ECS Service** - Create ECS service with task definition
5. **Application Load Balancer** - Create ALB
6. **Security Group** - Create security groups
7. **ECR Repository** - Create container registry
8. **IAM Role** - Create IAM roles
9. **Service Discovery** - Create Cloud Map services

### Deployment Category (3 components)
These appear in the **"deployment"** category:

1. **Terraform Generator** - Generate Terraform code
2. **AWS Deployer** - Deploy infrastructure
3. **Infrastructure Validator** - Validate infrastructure

## How to Find Components

### Method 1: Expand Categories
1. Look in the left sidebar for category folders
2. Find the **"aws"** category (might be collapsed)
3. Click the **">"** arrow to expand it
4. You'll see all 9 AWS components

### Method 2: Use Search Bar
1. Click in the search box at the top of Components sidebar
2. Type any component name:
   - "VPC"
   - "ECS"
   - "AWS Credentials"
   - "ALB"
   - "Security Group"
   - etc.
3. Components will appear in search results

### Method 3: Check All Categories
Scroll through all categories in the sidebar:
- Input & Output
- Data Sources
- Models & Agents
- **aws** ← Look here!
- **deployment** ← You already see this
- Utilities
- etc.

## If Components Still Don't Appear

1. **Restart Langflow**:
   ```bash
   ./start-langflow.sh
   ```

2. **Check Terminal Output**:
   - Look for any import errors
   - Should see component loading messages

3. **Verify Path**:
   ```bash
   echo $LANGFLOW_COMPONENTS_PATH
   # Should show: /home/ubuntu/aditya/infrastructure-composer-langflow/components
   ```

4. **Run Verification**:
   ```bash
   python3 verify-components.py
   ```

## Component Locations

All components are in:
```
/home/ubuntu/aditya/infrastructure-composer-langflow/components/
├── aws/          (9 components)
└── deployment/   (3 components)
```

## Quick Start Workflow

1. Drag **AWS Credentials** → Enter credentials
2. Drag **VPC** → Connect to credentials → Configure
3. Drag **Security Group** → Connect VPC + credentials → Configure
4. Drag **ECS Cluster** → Connect credentials → Configure
5. Drag **ECS Service** → Connect cluster + VPC + security group → Configure

See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for detailed steps.
