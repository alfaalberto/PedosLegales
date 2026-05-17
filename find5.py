with open('public/index.html','r',encoding='utf-8') as f:
    c = f.read()

# Find the processQueue completion text
import re
idx = c.find('state.queue=[];await saveState();renderAll();')
if idx != -1:
    print("Found at char:", idx)
    print("Context:", c[idx-20:idx+80].encode('ascii','replace').decode())
else:
    idx2 = c.find('state.queue=[];')
    print("state.queue=[] at:", idx2)
    print("Context:", c[idx2-10:idx2+120].encode('ascii','replace').decode())
