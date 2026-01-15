#!/usr/bin/env python3
"""Comprehensive cleanup of test_properties.py"""

import re


def main():
    with open("onboarding/tests/test_properties.py", "r") as f:
        lines = f.readlines()

    cleaned_lines = []
    prev_line = ""

    for line in lines:
        # Skip duplicate tenant creation lines
        if (
            "tenant = create_test_tenant()" in line
            and "tenant = create_test_tenant()" in prev_line
        ):
            continue

        # Fix wrong indentation for tenant creation
        if "       tenant = create_test_tenant()" in line:
            line = line.replace(
                "       tenant = create_test_tenant()",
                "        tenant = create_test_tenant()",
            )

        # Remove trailing comma before closing paren in function signatures
        if re.match(r"^        self, \w+, \s*$", line):
            line = line.replace(", \n", "\n")

        cleaned_lines.append(line)
        prev_line = line

    with open("onboarding/tests/test_properties.py", "w") as f:
        f.writelines(cleaned_lines)

    print("✓ Cleaned up file")


if __name__ == "__main__":
    main()
