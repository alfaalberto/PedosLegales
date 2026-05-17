import re

with open('public/index.html','r',encoding='utf-8') as f:
    c = f.read()

# Find the GLUE section (between last </script> end marker and the final script block)
# Look for the section where _orig* are assigned
print("=== _orig* assignments in glue ===")
for ref in ['_origRenderDocuments','_origHandleFiles','_origRenderDrafts','_origRenderChat','_origSelectDoc']:
    idx = c.find(ref)
    if idx != -1:
        ctx = c[max(0,idx-30):idx+120].encode('ascii','replace').decode()
        print(f"\n{ref}:\n  {ctx}")
    else:
        print(f"\n{ref}: NOT FOUND")

print("\n\n=== renderDocuments full body ===")
idx = c.find('async function renderDocuments')
if idx == -1: idx = c.find('function renderDocuments')
end = c.find('\nasync function ', idx+1)
if end == -1: end = c.find('\nfunction ', idx+1)
print(c[idx:min(idx+2000, end if end>0 else idx+2000)].encode('ascii','replace').decode())

print("\n\n=== handleFiles full body ===")
idx = c.find('function handleFiles')
# find the closing brace by counting
depth = 0
start = c.find('{', idx)
pos = start
for i, ch in enumerate(c[start:start+2000]):
    if ch == '{': depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            print(c[idx:start+i+1].encode('ascii','replace').decode())
            break

print("\n\n=== processQueue full body ===")
idx = c.find('async function processQueue')
if idx == -1: idx = c.find('function processQueue')
print(c[idx:idx+800].encode('ascii','replace').decode())

print("\n\n=== renderQueue full body ===")
idx = c.find('function renderQueue')
print(c[idx:idx+600].encode('ascii','replace').decode())

print("\n\n=== docsOfActive check ===")
idx = c.find('function docsOfActive')
if idx == -1: idx = c.find('async function docsOfActive')
print(c[idx:idx+300].encode('ascii','replace').decode() if idx != -1 else "NOT FOUND")

print("\n\n=== selectDoc full body ===")
idx = c.find('async function selectDoc')
if idx == -1: idx = c.find('function selectDoc')
print(c[idx:idx+500].encode('ascii','replace').decode() if idx != -1 else "NOT FOUND")
