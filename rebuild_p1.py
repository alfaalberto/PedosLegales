import re, json

with open('public/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

scripts = re.findall(r'<script[^>]*>.*?</script>', src, re.DOTALL)
with open('_js_block1.txt', 'w', encoding='utf-8') as f:
    f.write(scripts[0])
with open('_js_block2.txt', 'w', encoding='utf-8') as f:
    f.write(scripts[1])

print("Extracted", len(scripts), "script blocks")
print("Block 1:", len(scripts[0]), "chars")
print("Block 2:", len(scripts[1]), "chars")
