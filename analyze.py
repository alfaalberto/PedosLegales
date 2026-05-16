import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract script blocks
scripts = re.findall(r'<script[^>]*>.*?</script>', content, re.DOTALL)
print(f'Script blocks found: {len(scripts)}')
for i, s in enumerate(scripts):
    preview = s[:100].encode('ascii', 'replace').decode()
    print(f'Script {i}: {len(s)} chars => {preview}')
