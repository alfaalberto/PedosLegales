import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The regex r'<script[^>]*>(.*?)</script>' with DOTALL captures INNER content only
# But the _js_block2.txt was saved WITH the <script> tags from a previous run
# Let's re-extract properly

# Find all raw script tags including the tags
raw_scripts = re.findall(r'<script[^>]*>.*?</script>', content, re.DOTALL)
print(f"Found {len(raw_scripts)} script blocks")

# Extract inner content (without <script> tags)
inner = []
for s in raw_scripts:
    # Remove opening <script...> and closing </script>
    inner_text = re.sub(r'^<script[^>]*>', '', s, count=1)
    inner_text = re.sub(r'</script>\s*$', '', inner_text)
    inner.append(inner_text.strip())
    print(f"Block {len(inner)}: {len(inner_text)} chars, starts: {inner_text[:80].encode('ascii','replace').decode()}")

# Save clean blocks
with open('_js1_clean.txt', 'w', encoding='utf-8') as f:
    f.write(inner[0])
with open('_js2_clean.txt', 'w', encoding='utf-8') as f:
    f.write(inner[1])

print("Clean JS blocks saved")
