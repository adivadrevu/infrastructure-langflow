"""ECR Repository Component

Langflow component for creating AWS ECR (Elastic Container Registry) repositories.
"""

import json
from typing import Optional, Dict, Any
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, BoolInput, DataInput, DropdownInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
from ..utils.models import AWSCredentials
from ..utils.aws_client import create_ecr_client


class ECRComponent(Component):
    """ECR Repository Creation Component
    
    Creates an ECR repository for storing Docker images.
    """
    
    display_name: str = "ECR Repository"
    description: str = "Create AWS ECR (Elastic Container Registry) repository"
    documentation: str = "https://docs.aws.amazon.com/ecr/latest/userguide/repositories.html"
    icon: str = "Container"
    priority: int = 65
    name: str = "ecr"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        StrInput(
            name="name",
            display_name="Repository Name",
            info="Name for the ECR repository",
            required=True
        ),
        DropdownInput(
            name="image_tag_mutability",
            display_name="Image Tag Mutability",
            info="Whether image tags can be overwritten",
            options=["MUTABLE", "IMMUTABLE"],
            value="MUTABLE",
            required=True
        ),
        BoolInput(
            name="scan_on_push",
            display_name="Scan on Push",
            info="Enable image scanning on push",
            value=True,
            required=False
        ),
        DropdownInput(
            name="encryption_type",
            display_name="Encryption Type",
            info="Encryption type for images",
            options=["AES256", "KMS"],
            value="AES256",
            required=False
        ),
        StrInput(
            name="kms_key_id",
            display_name="KMS Key ID",
            info="KMS key ID (required if encryption_type is KMS)",
            value="",
            required=False
        ),
        StrInput(
            name="lifecycle_policy_json",
            display_name="Lifecycle Policy (JSON)",
            info="JSON lifecycle policy for the repository",
            value="",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="ecr_output", display_name="ECR Output", method="build_ecr"),
    ]
    
    def build_ecr(self) -> Data:
        """Create ECR repository and return output with repository URI and ARN."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            ecr_client = create_ecr_client(creds)
            
            # Prepare encryption configuration
            encryption_config = []
            if self.encryption_type:
                enc_config = {'encryptionType': self.encryption_type}
                if self.encryption_type == 'KMS' and self.kms_key_id:
                    enc_config['kmsKey'] = self.kms_key_id
                encryption_config.append(enc_config)
            
            # Create repository
            create_kwargs = {
                'repositoryName': self.name,
                'imageTagMutability': self.image_tag_mutability,
                'imageScanningConfiguration': {
                    'scanOnPush': self.scan_on_push
                }
            }
            
            if encryption_config:
                create_kwargs['encryptionConfigurations'] = encryption_config
            
            response = ecr_client.create_repository(**create_kwargs)
            
            repository = response['repository']
            repository_uri = repository.get('repositoryUri', '')
            repository_arn = repository.get('repositoryArn', '')
            
            # Set lifecycle policy if provided
            if self.lifecycle_policy_json:
                try:
                    lifecycle_policy = json.loads(self.lifecycle_policy_json)
                    ecr_client.put_lifecycle_policy(
                        repositoryName=self.name,
                        lifecyclePolicyText=json.dumps(lifecycle_policy)
                    )
                except json.JSONDecodeError:
                    # If not JSON, treat as string
                    ecr_client.put_lifecycle_policy(
                        repositoryName=self.name,
                        lifecyclePolicyText=self.lifecycle_policy_json
                    )
            
            result = {
                'repository_name': self.name,
                'repository_uri': repository_uri,
                'repository_arn': repository_arn,
                'image_tag_mutability': self.image_tag_mutability,
                'scan_on_push': self.scan_on_push,
                'status': 'created'
            }
            
            self.status = f"✓ ECR Repository '{self.name}' created successfully (URI: {repository_uri})"
            return Data(data=result)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            
            # Handle case where repository already exists
            if error_code == 'RepositoryAlreadyExistsException':
                try:
                    describe_response = ecr_client.describe_repositories(repositoryNames=[self.name])
                    if describe_response.get('repositories'):
                        repo = describe_response['repositories'][0]
                        result = {
                            'repository_name': self.name,
                            'repository_uri': repo.get('repositoryUri', ''),
                            'repository_arn': repo.get('repositoryArn', ''),
                            'image_tag_mutability': repo.get('imageTagMutability', 'MUTABLE'),
                            'scan_on_push': self.scan_on_push,
                            'status': 'exists'
                        }
                        self.status = f"ℹ ECR Repository '{self.name}' already exists"
                        return Data(data=result)
                except:
                    pass
            
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
