import re

def rd(f):
    with open(f, 'r', encoding='utf-8') as fh:
        return fh.read()

JS1 = rd('_clean_js0.txt')
JS2_RAW = rd('_clean_js1.txt')
CSS = rd('_css.txt')
BODY = rd('_body.txt')
GLUE = rd('_glue.txt')

# ── Strip functions that are re-implemented in GLUE ─────────────────────────
# Patterns: function names to completely remove
TO_REMOVE = [
    'getServerUrl',
    'configServerUrl',
    'renderServerBadge',
    'initTabs',
    'boot',
    'renderAll',
    'renderChat',
    'renderDrafts',
    'renderQueue',
    'goTab',
    'selectDoc',
    'handleFiles',
]

JS2 = JS2_RAW

# Remove DEFAULT_SERVER_URL const
JS2 = re.sub(r'const DEFAULT_SERVER_URL\s*=\s*["\'][^"\']+["\'];\n?', '', JS2)

# Remove each function body with a careful regex
for fn in TO_REMOVE:
    # Match: [async] function fnName(...) { ... } at top-level
    # Strategy: find the function declaration and use brace counting to find end
    # First try simple single-line or small functions
    JS2 = re.sub(
        r'(?:async\s+)?function\s+' + re.escape(fn) + r'\s*\([^)]*\)\s*\{[^{}]*\}\n?',
        '', JS2
    )

# Verify no <script or </script leaked
if '<script' in JS2.lower():
    print("ERROR: <script tag found in JS2!")
    idx = JS2.lower().find('<script')
    print("Context:", JS2[max(0,idx-50):idx+100].encode('ascii','replace').decode())
else:
    print("OK: no stray <script> in JS2")

print(f"JS2 length: {len(JS2)}")

# ── Build final HTML ─────────────────────────────────────────────────────────
HTML = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DefensaIPN.ai v7.1 — Sistema Jurídico Inteligente</title>
<meta name="description" content="Sistema jurídico inteligente para la defensa legal ante el IPN. Organiza expedientes, analiza documentos y consulta a la IA.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%230a0a0f'/><text x='16' y='22' font-size='20' text-anchor='middle' fill='%23d4af37'>%E2%9A%96</text></svg>">
<style>
{CSS}
</style>
</head>
<body>
{BODY}
<script>
{JS1}
</script>
<script>
{JS2}
// ── UI GLUE (simplified interface layer) ────────────────────────
{GLUE}
initFirebase();
</script>
</body>
</html>
"""

# Final check
if 'Unexpected token' in HTML:
    print("WARNING: potential syntax issue")

script_opens = HTML.count('<script>')
script_closes = HTML.count('</script>')
print(f"script tags: opens={script_opens} closes={script_closes}")

div_opens = HTML.count('<div')
div_closes = HTML.count('</div>')
print(f"div tags: opens={div_opens} closes={div_closes} diff={div_opens-div_closes}")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Done! Total size: {len(HTML)} chars")
