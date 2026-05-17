with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Remove getBlobLocal from get()
c = c.replace(
    'if (d && d.blobOmitted) d.blob = await getBlobLocal(String(d.id || d.key));',
    '// getBlobLocal removed for lazy loading'
)

# 2. Remove getBlobLocal from all() and byIndex()
c = c.replace(
    'for (const d of docs) { if (d.blobOmitted) d.blob = await getBlobLocal(String(d.id || d.key)); }',
    '// getBlobLocal removed for lazy loading'
)

# 3. Add getBlobLocal to renderBlobPreview
OLD_RBP = '''async function renderBlobPreview(d){
  const el=$("blobPreview"); if(!el)return;
  _revokeBlob();
  if(!d || !d.blob){
    el.innerHTML='<div class="viewer-no-blob"><div class="nb-icon">📂</div><p>El archivo original no está guardado.<br><small style="color:var(--mut)">Los documentos nuevos se guardarán automáticamente.</small></p></div>';
    return;
  }
  el.innerHTML='<div class="viewer-loading">⏳ Cargando vista previa...</div>';'''

NEW_RBP = '''async function renderBlobPreview(d){
  const el=$("blobPreview"); if(!el)return;
  _revokeBlob();
  if(!d) return;
  if(!d.blob && d.blobOmitted) {
    el.innerHTML='<div class="viewer-loading">⏳ Descargando archivo original desde la nube...</div>';
    try { d.blob = await getBlobLocal(d.id); } catch(e){}
  }
  if(!d.blob){
    el.innerHTML='<div class="viewer-no-blob"><div class="nb-icon">📂</div><p>El archivo original no está disponible localmente o bloqueado por CORS.<br><small style="color:var(--mut)">Los documentos nuevos se guardarán automáticamente.</small></p></div>';
    return;
  }
  el.innerHTML='<div class="viewer-loading">⏳ Cargando vista previa...</div>';'''

c = c.replace(OLD_RBP, NEW_RBP)

print("Patch applied to getBlobLocal lazy load")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
