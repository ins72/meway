#!/usr/bin/env python3

import re

# Read the file
with open('backend/services/email_marketing_service.py', 'r') as f:
    content = f.read()

# Fix the extra closing parentheses
content = re.sub(r'await self\._calculate_count\(user_id\)\)', 'await self._calculate_count(user_id)', content)

# Fix the missing closing brackets and return statements
fixes = [
    # Line around 672
    (r'\["total"\] if result else min_val', ']).to_list(length=1)\n                return result[0]["total"] if result else min_val'),
    
    # Line around 696
    (r'\["avg"\] if result else \(min_val \+ max_val\) / 2', ']).to_list(length=1)\n                return result[0]["avg"] if result else (min_val + max_val) / 2'),
    
    # Line around 746
    (r'\["avg"\] if result else \(min_val \+ max_val\) / 2', ']).to_list(length=1)\n                return result[0]["avg"] if result else (min_val + max_val) / 2'),
    
    # Line around 758
    (r'\["_id"\] if result and result\[0\]\["_id"\] in choices else choices\[0\]', ']).to_list(length=1)\n                return result[0]["_id"] if result and result[0]["_id"] in choices else choices[0]'),
    
    # Line around 785
    (r'\["total"\] if result else \(min_val \+ max_val\) // 2', ']).to_list(length=1)\n                return result[0]["total"] if result else (min_val + max_val) // 2'),
    
    # Line around 811
    (r'\["conversion_rate"\] if result else \(min_val \+ max_val\) / 2', ']).to_list(length=1)\n                return result[0]["conversion_rate"] if result else (min_val + max_val) / 2'),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content)

# Fix the assignment operator issue
content = re.sub(r'if result\.deleted_count = await self\._calculate_count\(user_id\):', 'if result.deleted_count == 0:', content)

# Write the fixed content back
with open('backend/services/email_marketing_service.py', 'w') as f:
    f.write(content)

print("Fixed syntax errors")