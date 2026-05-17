with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

lines = c.split('\n')
for i, line in enumerate(lines, 1):
    if any(k in line for k in ['renderBlobPreview','storeBlob','blobPreview','loadPdfJs','mammoth','objectURL','createObject']):
        print(f"{i}: {line[:160].encode('ascii','replace').decode()}")
