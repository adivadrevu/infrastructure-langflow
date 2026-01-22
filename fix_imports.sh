#!/bin/bash
# Fix all relative imports in component files

cd components

# Fix AWS components
for file in aws/*.py; do
    if [ "$(basename $file)" != "__init__.py" ]; then
        # Replace relative utils imports with try/except pattern
        sed -i "s|from \.\.utils\.models import|try:\n    from ..utils.models import\nexcept ImportError:\n    import sys, os\n    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n    from utils.models import|g" "$file"
        sed -i "s|from \.\.utils\.aws_client import|try:\n    from ..utils.aws_client import\nexcept ImportError:\n    import sys, os\n    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n    from utils.aws_client import|g" "$file"
    fi
done

# Fix deployment components
for file in deployment/*.py; do
    if [ "$(basename $file)" != "__init__.py" ]; then
        sed -i "s|from \.\.utils\.models import|try:\n    from ..utils.models import\nexcept ImportError:\n    import sys, os\n    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n    from utils.models import|g" "$file"
    fi
done

echo "✅ Import fixes applied"
