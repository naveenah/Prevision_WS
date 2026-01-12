#!/usr/bin/env python3
"""Final fix: properly format all test methods"""

def main():
    with open('onboarding/tests/test_properties.py', 'r') as f:
        content = f.read()
    
    # Fix all cases where docstring and tenant creation are on same line
    content = content.replace('"""        tenant = create_test_tenant()        ', '"""\n        tenant = create_test_tenant()\n        ')
    content = content.replace('"""        tenant = create_test_tenant()       ', '"""\n        tenant = create_test_tenant()\n        ')
    content = content.replace('"""tenant = create_test_tenant()', '"""\n        tenant = create_test_tenant()\n       ')
    
    # Fix trailing commas in parameter lists
    content = content.replace(', \n    ):', '\n    ):')
    
    with open('onboarding/tests/test_properties.py', 'w') as f:
        f.write(content)
    
    print("✓ Fixed syntax errors")

if __name__ == '__main__':
    main()
