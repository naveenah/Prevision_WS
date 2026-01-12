#!/usr/bin/env python3
"""Batch fix all remaining property tests"""

import re

def main():
    with open('onboarding/tests/test_properties.py', 'r') as f:
        content = f.read()
    
    # Pattern: Find test methods that don't have "tenant = create_test_tenant()" yet
    # but have "tenant=" usage
    
    pattern = r'(    def test_\w+\([^)]*\):\s*"""[^"]*""")\s*(\n        [^t])'
    
    def add_tenant(match):
        method_and_docstring = match.group(1)
        next_line = match.group(2)
        return f'{method_and_docstring}\n        tenant = create_test_tenant(){next_line}'
    
    content = re.sub(pattern, add_tenant, content)
    
    with open('onboarding/tests/test_properties.py', 'w') as f:
        f.write(content)
    
    print("✓ Fixed all test methods")

if __name__ == '__main__':
    main()
