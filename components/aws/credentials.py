"""AWS Credentials Component

Langflow component for inputting and validating AWS credentials.
"""

from typing import Optional
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, Output
from lfx.schema import Data
from ..utils.models import AWSCredentials
from ..utils.aws_client import validate_credentials


class AWSCredentialsComponent(Component):
    """AWS Credentials Input Component
    
    Provides AWS credentials (access key, secret, region) and validates them.
    Outputs credentials object for use by other AWS service components.
    """
    
    display_name: str = "AWS Credentials"
    description: str = "Input and validate AWS credentials (Access Key ID, Secret Access Key, Region)"
    documentation: str = "https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html"
    icon: str = "AWS"
    priority: int = 100
    name: str = "aws_credentials"
    
    inputs = [
        StrInput(
            name="access_key_id",
            display_name="Access Key ID",
            info="AWS Access Key ID",
            required=True,
            password=False
        ),
        StrInput(
            name="secret_access_key",
            display_name="Secret Access Key",
            info="AWS Secret Access Key",
            required=True,
            password=True
        ),
        StrInput(
            name="region",
            display_name="AWS Region",
            info="AWS Region (e.g., us-east-1, eu-west-1)",
            value="us-east-1",
            required=True
        ),
        StrInput(
            name="session_token",
            display_name="Session Token (Optional)",
            info="Temporary session token (for temporary credentials)",
            required=False,
            password=False
        ),
    ]
    
    outputs = [
        Output(name="credentials", display_name="AWS Credentials", method="build_credentials"),
        Output(name="validation_result", display_name="Validation Result", method="build_validation"),
    ]
    
    def build_credentials(self) -> Data:
        """Build and return credentials object."""
        credentials = AWSCredentials(
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            region=self.region,
            session_token=self.session_token if self.session_token else None
        )
        
        self.status = f"Credentials configured for region: {self.region}"
        return Data(credentials.dict(by_alias=True))
    
    def build_validation(self) -> Data:
        """Validate credentials and return validation result."""
        credentials = AWSCredentials(
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            region=self.region,
            session_token=self.session_token if self.session_token else None
        )
        
        validation = validate_credentials(credentials)
        
        if validation.get('valid'):
            self.status = f"✓ Credentials valid - Account: {validation.get('account_id')}"
        else:
            self.status = f"✗ Credentials invalid: {validation.get('error', 'Unknown error')}"
        
        return Data(validation)
