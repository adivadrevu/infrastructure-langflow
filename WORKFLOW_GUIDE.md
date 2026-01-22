# Step-by-Step Workflow Guide

This guide will walk you through creating your first AWS infrastructure workflow in Langflow.

## Prerequisites

- Langflow is running at `http://localhost:7860`
- You have AWS credentials (Access Key ID, Secret Access Key, Region)

## Step 1: Access Langflow UI

1. Open your browser and navigate to:
   ```
   http://localhost:7860
   ```

2. You should see the Langflow interface with:
   - **Left Sidebar**: Component palette
   - **Center Canvas**: Where you build workflows
   - **Right Sidebar**: Component properties (appears when you select a component)

## Step 2: Create a Simple Infrastructure Workflow

We'll create a basic workflow: **VPC → Security Group → ECS Cluster → ECS Service**

### Step 2.1: Add AWS Credentials Component

1. **Find the component**: In the left sidebar, search for "AWS Credentials" or scroll to find it
2. **Drag it onto the canvas**: Click and drag the "AWS Credentials" component to the center
3. **Configure it**:
   - Click on the component to select it
   - In the right sidebar, fill in:
     - **Access Key ID**: Your AWS Access Key ID
     - **Secret Access Key**: Your AWS Secret Access Key
     - **AWS Region**: e.g., `us-east-1`
     - **Session Token**: Leave empty (only for temporary credentials)

### Step 2.2: Add VPC Component

1. **Drag "VPC" component** onto the canvas (to the right of Credentials)
2. **Connect Credentials to VPC**:
   - Hover over the AWS Credentials component
   - You'll see output handles (small circles)
   - Click and drag from the "credentials" output to the VPC component's "credentials" input
3. **Configure VPC**:
   - Click on the VPC component
   - In the right sidebar, set:
     - **Name**: `my-vpc`
     - **CIDR Block**: `10.0.0.0/16`
     - **Enable DNS Hostnames**: `true` (checked)
     - **Enable DNS Support**: `true` (checked)
     - **Subnets (JSON)**: Leave as `[]` for now (or add subnets later)
     - **Create Internet Gateway**: `true`
     - **NAT Gateways (JSON)**: `[]`
     - **Route Tables (JSON)**: `[]`

### Step 2.3: Add Security Group Component

1. **Drag "Security Group" component** onto the canvas
2. **Connect components**:
   - Connect **AWS Credentials** output → Security Group credentials input
   - Connect **VPC** output → Security Group vpc_output input
3. **Configure Security Group**:
   - **Name**: `web-sg`
   - **Description**: `Security group for web traffic`
   - **Ingress Rules (JSON)**: 
     ```json
     [
       {
         "fromPort": 80,
         "toPort": 80,
         "protocol": "tcp",
         "cidrBlocks": ["0.0.0.0/0"],
         "description": "HTTP access"
       },
       {
         "fromPort": 443,
         "toPort": 443,
         "protocol": "tcp",
         "cidrBlocks": ["0.0.0.0/0"],
         "description": "HTTPS access"
       }
     ]
     ```
   - **Egress Rules (JSON)**: 
     ```json
     [
       {
         "fromPort": 0,
         "toPort": 65535,
         "protocol": "tcp",
         "cidrBlocks": ["0.0.0.0/0"],
         "description": "Allow all outbound"
       }
     ]
     ```

### Step 2.4: Add ECS Cluster Component

1. **Drag "ECS Cluster" component** onto the canvas
2. **Connect**:
   - **AWS Credentials** → ECS Cluster credentials input
3. **Configure ECS Cluster**:
   - **Name**: `my-ecs-cluster`
   - **Launch Type**: `FARGATE`
   - **Enable Container Insights**: `true` (checked)
   - **Tags (JSON)**: `{}` (empty object)

### Step 2.5: Add ECS Service Component

1. **Drag "ECS Service" component** onto the canvas
2. **Connect**:
   - **AWS Credentials** → ECS Service credentials input
   - **ECS Cluster** cluster_output → ECS Service cluster_output input
   - **VPC** vpc_output → ECS Service (we'll need subnet IDs)
   - **Security Group** security_group_output → ECS Service (we'll need security group IDs)
3. **Configure ECS Service**:
   - **Service Name**: `my-web-service`
   - **Task Family**: `my-web-task`
   - **Container Name**: `web-container`
   - **Container Image**: `nginx:latest` (or your image)
   - **CPU (units)**: `1024`
   - **Memory (MB)**: `2048`
   - **Container Port**: `80`
   - **Desired Count**: `1`
   - **Launch Type**: `FARGATE`
   - **Subnet IDs (JSON Array)**: 
     ```json
     ["subnet-xxx", "subnet-yyy"]
     ```
     *Note: You'll need to get these from the VPC output after creating the VPC*
   - **Security Group IDs (JSON Array)**: 
     ```json
     ["sg-xxx"]
     ```
     *Note: You'll need to get this from the Security Group output*
   - **Environment Variables (JSON)**: `{}`
   - **CloudWatch Log Group**: Leave empty (will default to `/ecs/my-web-service`)

## Step 3: Execute the Workflow

### Option A: Execute Components Individually (Recommended for First Time)

1. **Start with AWS Credentials**:
   - Click the "Run" or "Execute" button on the AWS Credentials component
   - Check the output - you should see validation results

2. **Execute VPC**:
   - Click "Run" on the VPC component
   - Wait for it to complete
   - Check the output for `vpc_id` and `subnet_ids`
   - **Copy the subnet IDs** - you'll need them for ECS Service

3. **Execute Security Group**:
   - Click "Run" on the Security Group component
   - Wait for completion
   - Check the output for `security_group_id`
   - **Copy the security group ID** - you'll need it for ECS Service

4. **Update ECS Service Configuration**:
   - Go back to ECS Service component
   - Update **Subnet IDs** with the actual subnet IDs from VPC output
   - Update **Security Group IDs** with the actual security group ID

5. **Execute ECS Cluster**:
   - Click "Run" on ECS Cluster component
   - Wait for completion

6. **Execute ECS Service**:
   - Click "Run" on ECS Service component
   - This will create the task definition and service

### Option B: Execute All at Once

- Some Langflow versions support "Run All" - look for a global run button
- Components will execute in dependency order automatically

## Step 4: Verify Deployment

1. **Check Component Status**:
   - Each component shows a status message (✓ for success, ✗ for error)
   - Green checkmarks indicate successful creation

2. **Check AWS Console**:
   - Log into AWS Console
   - Navigate to:
     - **VPC**: EC2 → VPCs
     - **Security Groups**: EC2 → Security Groups
     - **ECS Clusters**: ECS → Clusters
     - **ECS Services**: ECS → Clusters → Services

3. **View Outputs**:
   - Click on each component to see its output
   - Outputs contain ARNs, IDs, and other resource information

## Step 5: Advanced Workflow - Add ALB

### Add Application Load Balancer

1. **Drag "ALB" component** onto the canvas
2. **Connect**:
   - **AWS Credentials** → ALB credentials
   - **VPC** → ALB vpc_output
   - **Security Group** → ALB (for security group IDs)
3. **Configure ALB**:
   - **Name**: `my-alb`
   - **Scheme**: `internet-facing`
   - **Subnet IDs (JSON Array)**: Use subnet IDs from VPC output
   - **Security Group IDs (JSON Array)**: Use security group ID
   - **Listener Port**: `80`
   - **Listener Protocol**: `HTTP`
   - **Target Group Name**: `my-target-group`
   - **Target Group Port**: `80`
   - **Target Group Protocol**: `HTTP`
   - **Health Check Path**: `/`

4. **Connect ALB to ECS Service**:
   - After ALB is created, you can update ECS Service to use the target group
   - Or create a new ECS Service that connects to the ALB

## Step 6: Generate Terraform Code

1. **Drag "Terraform Generator" component** onto the canvas
2. **Connect all service components** to the Terraform Generator's infrastructure_data input
3. **Configure**:
   - **Environment**: `sbx` or `live`
   - **Region**: Your AWS region
4. **Execute** to generate Terraform code
5. **View outputs**:
   - `terraform_code` - main.tf content
   - `variables_tf` - variables.tf content
   - `outputs_tf` - outputs.tf content
   - `readme` - README.md content

## Step 7: Validate Infrastructure

1. **Drag "Infrastructure Validator" component** onto the canvas
2. **Connect all components** to the validator's infrastructure_data input
3. **Execute** to validate
4. **Check output** for:
   - `is_valid`: true/false
   - `errors`: Array of validation errors
   - `warnings`: Array of warnings

## Tips and Best Practices

### 1. Start Small
- Begin with just VPC + Security Group
- Test each component before adding more

### 2. Save Your Workflow
- Langflow auto-saves, but you can also:
  - Click "Save" button (if available)
  - Export the workflow JSON

### 3. Error Handling
- If a component fails:
  - Check the error message in the component output
  - Verify AWS credentials and permissions
  - Check AWS service quotas
  - Review component configuration

### 4. Resource Naming
- Use consistent naming: `{project}-{service}-{env}`
- Example: `myapp-vpc-sbx`, `myapp-ecs-cluster-sbx`

### 5. JSON Inputs
- For complex inputs (subnets, rules, policies), use proper JSON format
- Validate JSON before pasting (use a JSON validator online)
- Watch for trailing commas and proper escaping

### 6. Dependencies
- Always create resources in order:
  1. VPC (foundation)
  2. Security Groups (needed by other resources)
  3. ECS Cluster
  4. ECS Service (needs cluster and networking)
  5. ALB (optional, for load balancing)

## Common Issues and Solutions

### Issue: Component not appearing in sidebar
**Solution**: 
- Restart Langflow
- Check that `LANGFLOW_COMPONENTS_PATH` is set correctly
- Verify component files are in the right directory

### Issue: Connection not working
**Solution**:
- Make sure output/input types match
- Check that source component has executed successfully
- Verify the connection is from output to input (not input to input)

### Issue: AWS Error
**Solution**:
- Verify credentials are correct
- Check IAM permissions
- Ensure region is correct
- Check AWS service quotas

### Issue: JSON Parse Error
**Solution**:
- Validate JSON syntax
- Remove trailing commas
- Escape special characters properly
- Use double quotes for strings

## Example: Complete Workflow JSON Structure

When connecting components, Langflow creates a workflow. Here's what a simple workflow looks like:

```
AWS Credentials
    ↓ (credentials output)
    ├─→ VPC (credentials input)
    ├─→ Security Group (credentials input)
    ├─→ ECS Cluster (credentials input)
    └─→ ECS Service (credentials input)

VPC (vpc_output)
    ↓
    ├─→ Security Group (vpc_output input)
    └─→ ECS Service (for subnet IDs)

Security Group (security_group_output)
    ↓
    └─→ ECS Service (for security group IDs)

ECS Cluster (cluster_output)
    ↓
    └─→ ECS Service (cluster_output input)
```

## Next Steps

1. **Experiment**: Try different configurations
2. **Add More Services**: ECR, IAM Roles, Service Discovery
3. **Use Terraform Generator**: Export your infrastructure as code
4. **Validate First**: Always validate before deploying
5. **Clean Up**: Delete test resources in AWS Console when done

## Quick Reference: Component Inputs

### AWS Credentials
- Access Key ID, Secret Access Key, Region

### VPC
- Name, CIDR Block, DNS settings, Subnets (JSON), IGW, NAT Gateways (JSON)

### Security Group
- Name, Description, VPC, Ingress Rules (JSON), Egress Rules (JSON)

### ECS Cluster
- Name, Launch Type, Container Insights, Tags (JSON)

### ECS Service
- Service Name, Cluster, Task Family, Container Config, CPU, Memory, Port, Subnets, Security Groups

### ALB
- Name, Scheme, Subnets, Security Groups, Listener Config, Target Group Config

---

**Happy Building!** 🚀

For more details, see the main [README.md](README.md).
