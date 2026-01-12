#!/usr/bin/env python3
"""Script to fix property tests by replacing unique_tenant fixture with create_test_tenant() calls"""

import re

def fix_property_tests():
    with open('onboarding/tests/test_properties.py', 'r') as f:
        content = f.read()

    # Step 1: Remove unique_tenant from method signatures
    content = re.sub(r'(def test_\w+\([^)]*), unique_tenant\)', r'\1)', content)
    
    # Step 2: Replace unique_tenant usage with tenant variable
    content = content.replace('tenant=unique_tenant', 'tenant=tenant')
    content = content.replace('(unique_tenant)', '(tenant)')
    content = content.replace('tenant = unique_tenant', 'tenant = tenant')
    content = content.replace('filter(tenant=tenant)', 'filter(tenant=tenant)')
    
    # Step 3: Add tenant creation after docstrings in each test method
    lines = content.split('\n')
    result_lines = []
    in_test_method = False
    need_tenant_creation = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        result_lines.append(line)
        
        # Detect test method definition
        if re.match(r'    def test_\w+\(self', line):
            in_test_method = True
            need_tenant_creation = True
            indent_level = len(line) - len(line.lstrip())
            continue
        
        # If we're in a test method and need to add tenant creation
        if in_test_method and need_tenant_creation:
            # Check if this line is a docstring end or first real line
            if '"""' in line and line.strip().endswith('"""'):
                # Add tenant creation after docstring
                result_lines.append(' ' * (indent_level + 8) + 'tenant = create_test_tenant()')
                need_tenant_creation = False
                in_test_method = False
            elif line.strip() and not line.strip().startswith('"""') and not line.strip().startswith('@'):
                # No docstring, add tenant creation before this line
                result_lines.insert(-1, ' ' * (indent_level + 8) + 'tenant = create_test_tenant()')
                need_tenant_creation = False
                in_test_method = False

    with open('onboarding/tests/test_properties.py', 'w') as f:
        f.write('\n'.join(result_lines))
    
    print("✓ Successfully updated property tests")

if __name__ == '__main__':
    fix_property_tests()
