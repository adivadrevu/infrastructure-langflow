"""IAM Role Component

Langflow component for creating AWS IAM Roles with policies.
"""

import json
from typing import Optional, Dict, Any, List
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, DataInput, Output
from lfx.schema import Data
from botocore.exceptions import ClientError
from ..utils.models import AWSCredentials
from ..utils.aws_client import create_iam_client


class IAMRoleComponent(Component):
    """IAM Role Creation Component
    
    Creates an IAM role with assume role policy and inline/managed policies.
    """
    
    display_name: str = "IAM Role"
    description: str = "Create AWS IAM Role with assume role policy and policies"
    documentation: str = "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html"
    icon: str = "Key"
    priority: int = 60
    name: str = "iam_role"
    
    inputs = [
        DataInput(
            name="credentials",
            display_name="AWS Credentials",
            info="AWS credentials from credentials component",
            required=True
        ),
        StrInput(
            name="name",
            display_name="Role Name",
            info="Name for the IAM role",
            required=True
        ),
        StrInput(
            name="assume_role_policy_document",
            display_name="Assume Role Policy Document (JSON)",
            info='JSON policy document: {"Version": "2012-10-17", "Statement": [...]}',
            required=True
        ),
        StrInput(
            name="policies_json",
            display_name="Inline Policies (JSON Array)",
            info='JSON array: [{"name": "policy1", "policyDocument": {...}}]',
            value="[]",
            required=False
        ),
        StrInput(
            name="managed_policy_arns_json",
            display_name="Managed Policy ARNs (JSON Array)",
            info='JSON array: ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]',
            value="[]",
            required=False
        ),
    ]
    
    outputs = [
        Output(name="iam_role_output", display_name="IAM Role Output", method="build_iam_role"),
    ]
    
    def build_iam_role(self) -> Data:
        """Create IAM role with policies and return output."""
        try:
            # Parse credentials
            if isinstance(self.credentials, dict):
                creds = AWSCredentials(**self.credentials)
            else:
                creds = AWSCredentials.parse_obj(self.credentials)
            
            iam_client = create_iam_client(creds)
            
            # Parse assume role policy document
            if isinstance(self.assume_role_policy_document, str):
                try:
                    assume_policy = json.loads(self.assume_role_policy_document)
                    assume_policy_str = json.dumps(assume_policy)
                except json.JSONDecodeError:
                    assume_policy_str = self.assume_role_policy_document
            else:
                assume_policy_str = json.dumps(self.assume_role_policy_document)
            
            # Create role
            response = iam_client.create_role(
                RoleName=self.name,
                AssumeRolePolicyDocument=assume_policy_str,
                Tags=[
                    {'Key': 'Name', 'Value': self.name},
                    {'Key': 'ManagedBy', 'Value': 'infrastructure-composer'}
                ]
            )
            
            role_arn = response['Role']['Arn']
            role_name = response['Role']['RoleName']
            
            # Attach inline policies
            policies = json.loads(self.policies_json) if self.policies_json else []
            for policy in policies:
                policy_name = policy.get('name', '')
                policy_doc = policy.get('policyDocument', {})
                
                if isinstance(policy_doc, dict):
                    policy_doc_str = json.dumps(policy_doc)
                else:
                    policy_doc_str = str(policy_doc)
                
                iam_client.put_role_policy(
                    RoleName=self.name,
                    PolicyName=policy_name,
                    PolicyDocument=policy_doc_str
                )
            
            # Attach managed policies
            managed_policy_arns = json.loads(self.managed_policy_arns_json) if self.managed_policy_arns_json else []
            for policy_arn in managed_policy_arns:
                iam_client.attach_role_policy(
                    RoleName=self.name,
                    PolicyArn=policy_arn
                )
            
            result = {
                'role_name': role_name,
                'role_arn': role_arn,
                'policies_count': len(policies),
                'managed_policies_count': len(managed_policy_arns),
                'status': 'created'
            }
            
            self.status = f"✓ IAM Role '{role_name}' created successfully (ARN: {role_arn})"
            return Data(result)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            
            # Handle case where role already exists
            if error_code == 'EntityAlreadyExistsException':
                try:
                    get_response = iam_client.get_role(RoleName=self.name)
                    role = get_response['Role']
                    result = {
                        'role_name': role['RoleName'],
                        'role_arn': role['Arn'],
                        'policies_count': 0,
                        'managed_policies_count': 0,
                        'status': 'exists'
                    }
                    self.status = f"ℹ IAM Role '{self.name}' already exists"
                    return Data(result)
                except:
                    pass
            
            error_msg = f"AWS Error: {error_msg}"
            self.status = f"✗ {error_msg}"
            return Data({
                'error': error_msg,
                'status': 'failed'
            })
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data({
                'error': error_msg,
                'status': 'failed'
            })
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status = f"✗ {error_msg}"
            return Data({
                'error': error_msg,
                'status': 'failed'
            })
