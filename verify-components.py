#!/usr/bin/env python3
"""Verify all Langflow components are properly configured and can be discovered."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def verify_components():
    """Verify all components can be imported and are properly configured."""
    print("🔍 Verifying Langflow Components...")
    print("=" * 70)
    
    errors = []
    aws_components = []
    deployment_components = []
    
    # Test AWS components
    try:
        from components.aws import (
            AWSCredentialsComponent, VPCComponent, ECSClusterComponent,
            ECSServiceComponent, ALBComponent, SecurityGroupComponent,
            ECRComponent, IAMRoleComponent, ServiceDiscoveryComponent
        )
        
        aws_components = [
            ("AWS Credentials", AWSCredentialsComponent),
            ("VPC", VPCComponent),
            ("ECS Cluster", ECSClusterComponent),
            ("ECS Service", ECSServiceComponent),
            ("Application Load Balancer", ALBComponent),
            ("Security Group", SecurityGroupComponent),
            ("ECR Repository", ECRComponent),
            ("IAM Role", IAMRoleComponent),
            ("Service Discovery", ServiceDiscoveryComponent),
        ]
        
        print(f"\n✅ AWS Category: {len(aws_components)} components")
        for name, comp in aws_components:
            try:
                assert hasattr(comp, 'display_name'), f"{name}: Missing display_name"
                assert hasattr(comp, 'name'), f"{name}: Missing name"
                assert hasattr(comp, 'inputs'), f"{name}: Missing inputs"
                assert hasattr(comp, 'outputs'), f"{name}: Missing outputs"
                print(f"   ✓ {comp.display_name} ({comp.name})")
            except AssertionError as e:
                errors.append(str(e))
                print(f"   ✗ {name}: {e}")
                
    except Exception as e:
        errors.append(f"AWS import error: {e}")
        print(f"   ✗ Failed to import AWS components: {e}")
    
    # Test Deployment components
    try:
        from components.deployment import (
            TerraformGeneratorComponent, AWSDeployerComponent, ValidatorComponent
        )
        
        deployment_components = [
            ("Terraform Generator", TerraformGeneratorComponent),
            ("AWS Deployer", AWSDeployerComponent),
            ("Infrastructure Validator", ValidatorComponent),
        ]
        
        print(f"\n✅ Deployment Category: {len(deployment_components)} components")
        for name, comp in deployment_components:
            try:
                assert hasattr(comp, 'display_name'), f"{name}: Missing display_name"
                assert hasattr(comp, 'name'), f"{name}: Missing name"
                assert hasattr(comp, 'inputs'), f"{name}: Missing inputs"
                assert hasattr(comp, 'outputs'), f"{name}: Missing outputs"
                print(f"   ✓ {comp.display_name} ({comp.name})")
            except AssertionError as e:
                errors.append(str(e))
                print(f"   ✗ {name}: {e}")
                
    except Exception as e:
        errors.append(f"Deployment import error: {e}")
        print(f"   ✗ Failed to import Deployment components: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    total = len(aws_components) + len(deployment_components)
    print(f"📊 Summary: {total} total components")
    print(f"   - AWS: {len(aws_components)} components")
    print(f"   - Deployment: {len(deployment_components)} components")
    
    if errors:
        print(f"\n❌ Found {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("\n✅ All components are properly configured!")
        print("\n💡 To see components in Langflow UI:")
        print("   1. Look for 'aws' category in the left sidebar")
        print("   2. Look for 'deployment' category in the left sidebar")
        print("   3. Use the search bar to find components by name")
        print("   4. Make sure Langflow was started with: --components-path ./components")
        return True

if __name__ == "__main__":
    success = verify_components()
    sys.exit(0 if success else 1)
