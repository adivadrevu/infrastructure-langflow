#!/usr/bin/env python3
"""Fix relative imports in component files to work with Langflow's direct import."""

import os
import re

def fix_imports_in_file(filepath):
    """Fix relative imports in a component file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: from ..utils.models import
    pattern1 = r'from \.\.utils\.models import ([^\n]+)'
    replacement1 = r'''try:
    from ..utils.models import \1
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from utils.models import \1'''
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: from ..utils.aws_client import
    pattern2 = r'from \.\.utils\.aws_client import ([^\n]+)'
    replacement2 = r'''try:
    from ..utils.aws_client import \1
except ImportError:
    import sys, os
    components_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if components_dir not in sys.path:
        sys.path.insert(0, components_dir)
    from utils.aws_client import \1'''
    content = re.sub(pattern2, replacement2, content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    components_dir = 'components'
    fixed_count = 0
    
    # Fix AWS components
    for root, dirs, files in os.walk(os.path.join(components_dir, 'aws')):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    print(f"✅ Fixed: {filepath}")
                    fixed_count += 1
    
    # Fix deployment components
    for root, dirs, files in os.walk(os.path.join(components_dir, 'deployment')):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    print(f"✅ Fixed: {filepath}")
                    fixed_count += 1
    
    print(f"\n✅ Fixed imports in {fixed_count} files")

if __name__ == '__main__':
    main()
