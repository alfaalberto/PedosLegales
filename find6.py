with open('public/index.html','r',encoding='utf-8') as f:
    c = f.read()

import re
# Find processQueue end
idx = c.find('async function processQueue')
if idx != -1:
    block = c[idx:idx+2000]
    print(block.encode('ascii','replace').decode())
