#!/usr/bin/env python

print("Checking riskfolio package imports...")

try:
    import riskfolio
    print("SUCCESS: import riskfolio works!")
except ImportError as e:
    print(f"ERROR importing riskfolio: {e}")

try:
    import riskfolio_lib
    print("SUCCESS: import riskfolio_lib works!")
except ImportError as e:
    print(f"ERROR importing riskfolio_lib: {e}")

try:
    from riskfolio_lib import riskfolio
    print("SUCCESS: from riskfolio_lib import riskfolio works!")
except ImportError as e:
    print(f"ERROR importing from riskfolio_lib import riskfolio: {e}")

# Check installed packages
print("\nChecking installed packages with 'risk' in the name:")
import pkg_resources
risk_packages = [p for p in pkg_resources.working_set if 'risk' in p.project_name.lower()]
for p in risk_packages:
    print(f"Found package: {p.project_name} (version: {p.version})") 