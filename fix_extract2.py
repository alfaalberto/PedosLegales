import re

# Extract clean JS from original known-good file
with open('_original_clean.html', 'r', encoding='utf-8') as f:
    src = f.read()

raw_scripts = re.findall(r'<script[^>]*>.*?</script>', src, re.DOTALL)
print(f"Found {len(raw_scripts)} script blocks in original")

inner = []
for i, s in enumerate(raw_scripts):
    txt = re.sub(r'^<script[^>]*>', '', s, count=1)
    txt = re.sub(r'</script>\s*$', '', txt)
    txt = txt.strip()
    inner.append(txt)
    print(f"Block {i}: {len(txt)} chars, start: {txt[:80].encode('ascii','replace').decode()}")

with open('_js1_clean.txt', 'w', encoding='utf-8') as f:
    f.write(inner[0])
with open('_js2_clean.txt', 'w', encoding='utf-8') as f:
    f.write(inner[1])

print("Done extracting clean JS blocks")

# ─── Now apply the same regex removals as rebuild_final.py ───────────────────
JS2 = inner[1]

JS2 = re.sub(r'const DEFAULT_SERVER_URL\s*=\s*["\'].*?["\'];', '', JS2)
JS2 = re.sub(r'function getServerUrl\(\)\s*\{[^}]+\}', '', JS2)
JS2 = re.sub(r'function configServerUrl\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function renderServerBadge\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function initTabs\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function boot\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function renderAll\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function renderChat\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function renderDrafts\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function renderQueue\(\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function goTab\(id\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function selectDoc\(id\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function handleFiles\(files\)\s*\{.*?\n\}', '', JS2, flags=re.DOTALL)

# Verify no HTML leaked in
if '<script' in JS2 or '</script' in JS2:
    print("WARNING: script tags found in JS2!")
else:
    print("JS2 clean - no stray script tags")
print(f"JS2 length after cleanup: {len(JS2)}")
print(f"JS2 first 200: {JS2[:200].encode('ascii','replace').decode()}")

with open('_js2_stripped.txt', 'w', encoding='utf-8') as f:
    f.write(JS2)
print("Stripped JS2 saved")
