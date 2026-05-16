import re

# ── Read parts ──
def rd(f):
    with open(f,'r',encoding='utf-8') as fh: return fh.read()

CSS  = rd('_css.txt')
BODY = rd('_body.txt')
GLUE = rd('_glue.txt')
JS1  = rd('_js_block1.txt')
JS2  = rd('_js_block2.txt')

# ── Remove getServerUrl and configServerUrl and DEFAULT_SERVER_URL from JS2 ──
# (they are replaced by glue)
JS2 = re.sub(r'const DEFAULT_SERVER_URL\s*=.*?;', '', JS2)
JS2 = re.sub(r'function getServerUrl\(\)\s*\{[^}]+\}', '', JS2)
JS2 = re.sub(r'function configServerUrl\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function renderServerBadge\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function initTabs\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function boot\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function renderAll\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function renderChat\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function renderDrafts\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function renderQueue\(\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function handleFiles\(.*?\}\s*\n', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'function goTab\(id\)\s*\{.*?\}', '', JS2, flags=re.DOTALL)
JS2 = re.sub(r'async function selectDoc\(.*?\}', '', JS2, flags=re.DOTALL)

# ── Build final HTML ──
HTML = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DefensaIPN.ai v7.1 — Sistema Jurídico Inteligente</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Lora:wght@500;700&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%230a0a0f'/><text x='16' y='22' font-size='20' text-anchor='middle' fill='%23d4af37'>⚖</text></svg>">
<style>
{CSS}
</style>
</head>
<body>
{BODY}
{JS1}
<script>
{JS2}
{GLUE}
initFirebase();
</script>
</body>
</html>
"""

with open('public/index.html','w',encoding='utf-8') as f:
    f.write(HTML)

opens  = HTML.count('<div')
closes = HTML.count('</div>')
print(f"Done! {len(HTML)} chars, div balance: {opens-closes}")
