"""Shared Utilities

Shared utilities and models used across the application.
These are legacy utilities being migrated to clean architecture.
"""

# For backward compatibility, expose models and aws_client
from .models import *
from .aws_client import *
