with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

lines = c.split('\n')

print("=== 1. FIREBASE CONFIG ===")
for i,l in enumerate(lines,1):
    if any(k in l for k in ['FIREBASE_CONFIG','apiKey','storageBucket','initializeApp','firebaseConfig']):
        print(f"{i}: {l[:160].encode('ascii','replace').decode()}")

print("\n=== 2. handleFiles ===")
for i,l in enumerate(lines,1):
    if 'function handleFiles' in l or 'storeBlob' in l or 'ocrProgress' in l or 'processQueue' in l:
        print(f"{i}: {l[:140].encode('ascii','replace').decode()}")

print("\n=== 3. STORAGE UPLOAD CODE ===")
for i,l in enumerate(lines,1):
    if any(k in l for k in ['uploadBytes','storage','getStorage','storageRef','uploadFile','Storage upload','storeFile']):
        print(f"{i}: {l[:160].encode('ascii','replace').decode()}")

print("\n=== 4. ocrFile / ocrPdf / ocrImage ===")
for i,l in enumerate(lines,1):
    if any(k in l for k in ['async function ocrFile','async function processQueue','item.status']):
        print(f"{i}: {l[:140].encode('ascii','replace').decode()}")
