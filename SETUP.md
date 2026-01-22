# Setup Guide - AWS Infrastructure Composer (Langflow)

This guide will help you set up and run the AWS Infrastructure Composer with Langflow.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python3 --version
   ```

2. **pip** package manager
   ```bash
   pip3 --version
   ```

3. **AWS Account** with appropriate permissions
   - IAM permissions for: EC2, ECS, ELBv2, ECR, IAM, ServiceDiscovery, STS
   - AWS Access Key ID and Secret Access Key

4. **Langflow** installed (will be installed via requirements.txt)

## Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd infrastructure-composer-langflow
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langflow` - Langflow framework
- `boto3` - AWS SDK for Python
- `pydantic` - Data validation
- `jinja2` - Template engine

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
# Set to absolute path of components directory
LANGFLOW_COMPONENTS_PATH=/absolute/path/to/infrastructure-composer-langflow/components

# Optional: AWS credentials (can also be provided via UI)
# AWS_ACCESS_KEY_ID=your_access_key_id
# AWS_SECRET_ACCESS_KEY=your_secret_access_key
# AWS_REGION=us-east-1
```

**Important**: Replace `/absolute/path/to/` with your actual path. For example:
```bash
LANGFLOW_COMPONENTS_PATH=/home/user/infrastructure-composer-langflow/components
```

### Step 5: Verify Components Directory Structure

Ensure your directory structure looks like this:

```
infrastructure-composer-langflow/
├── components/
│   ├── __init__.py
│   ├── aws/
│   │   ├── __init__.py
│   │   ├── credentials.py
│   │   ├── vpc.py
│   │   ├── ecs_cluster.py
│   │   ├── ecs_service.py
│   │   ├── alb.py
│   │   ├── security_group.py
│   │   ├── ecr.py
│   │   ├── iam_role.py
│   │   └── service_discovery.py
│   ├── deployment/
│   │   ├── __init__.py
│   │   ├── terraform_generator.py
│   │   ├── aws_deployer.py
│   │   └── validator.py
│   └── utils/
│       ├── __init__.py
│       ├── aws_client.py
│       └── models.py
├── requirements.txt
├── README.md
├── SETUP.md
└── .env.example
```

### Step 6: Start Langflow

```bash
# Using environment variable
export LANGFLOW_COMPONENTS_PATH=$(pwd)/components
langflow run

# Or using command-line flag
langflow run --components-path ./components
```

### Step 7: Access Langflow UI

Open your browser and navigate to:
```
http://localhost:7860
```

You should see the Langflow interface with AWS Infrastructure Composer components in the sidebar.

## Verification

### Test AWS Credentials Component

1. Drag **AWS Credentials** component onto canvas
2. Enter your AWS credentials:
   - Access Key ID
   - Secret Access Key
   - Region (e.g., `us-east-1`)
3. Connect to **Validation Result** output
4. Execute the component
5. Verify credentials are valid

### Test VPC Component

1. Drag **VPC** component onto canvas
2. Connect **AWS Credentials** output to VPC input
3. Configure:
   - Name: `test-vpc`
   - CIDR Block: `10.0.0.0/16`
4. Execute (this will create a real VPC in AWS)
5. Check output for VPC ID

## Troubleshooting

### Issue: Components Not Appearing

**Solution:**
1. Verify `LANGFLOW_COMPONENTS_PATH` is set correctly
2. Check that all `__init__.py` files exist
3. Restart Langflow
4. Check Langflow console for import errors

### Issue: Import Errors

**Solution:**
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python3 --version` (should be 3.8+)
3. Verify virtual environment is activated

### Issue: AWS Authentication Errors

**Solution:**
1. Verify AWS credentials are correct
2. Check IAM permissions
3. Test credentials using AWS CLI: `aws sts get-caller-identity`
4. Ensure region is correct

### Issue: Port Already in Use

**Solution:**
```bash
# Use a different port
langflow run --port 7861
```

### Issue: Components Not Loading

**Solution:**
1. Check component file syntax (Python errors)
2. Verify all imports are correct
3. Check Langflow logs for specific error messages
4. Ensure component classes inherit from `Component`

## Next Steps

Once setup is complete:

1. **Read the README.md** for component usage
2. **Start with simple workflows** (VPC → Security Group)
3. **Test validation** before deploying
4. **Generate Terraform** to review infrastructure code
5. **Deploy incrementally** (test in sandbox first)

## Advanced Configuration

### Using Docker

If you prefer Docker:

```bash
docker run -d \
  -v $(pwd)/components:/app/components \
  -e LANGFLOW_COMPONENTS_PATH=/app/components \
  -p 7860:7860 \
  langflowai/langflow:latest
```

### Custom Port

```bash
langflow run --port 8080
```

### Development Mode

For development with auto-reload:

```bash
langflow run --components-path ./components --dev
```

## Support

For issues:
1. Check Langflow documentation: https://docs.langflow.org
2. Review AWS service documentation
3. Check component error messages in Langflow UI
4. Verify AWS credentials and permissions

## Security Reminders

- **Never commit `.env` file** to version control
- **Use IAM roles** when possible instead of access keys
- **Rotate credentials** regularly
- **Use least privilege** IAM policies
- **Review Terraform code** before deploying
