import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find line numbers for key functions
lines = c.split('\n')
for i, line in enumerate(lines, 1):
    if 'renderChat' in line or 'renderSelectedDoc' in line or 'draftEditor' in line or 'msg.role' in line or 'marked' in line.lower():
        print(f"{i}: {line[:120].encode('ascii','replace').decode()}")
