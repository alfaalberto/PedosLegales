with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find the exact renderBlobPreview block
import re
idx = c.find('async function renderBlobPreview(d){')
if idx == -1:
    print("NOT FOUND with that signature")
    # Search all occurrences of renderBlobPreview
    for m in re.finditer(r'renderBlobPreview', c):
        print(f"At {m.start()}: {c[m.start():m.start()+80].encode('ascii','replace').decode()}")
else:
    print(f"Found at {idx}")
    # Find the closing brace
    depth = 0
    start_brace = c.find('{', idx)
    for i, ch in enumerate(c[start_brace:start_brace+3000]):
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = start_brace + i + 1
                print(f"Function ends at {end}")
                print("Full function:")
                print(c[idx:end].encode('ascii','replace').decode())
                break
