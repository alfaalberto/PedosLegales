import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find renderSelectedDoc and its sourcePreview line
lines = c.split('\n')
for i, line in enumerate(lines, 1):
    if 'sourcePreview' in line or ('renderChat' in line and 'function' in line):
        print(f"{i}: {line[:150].encode('ascii','replace').decode()}")
