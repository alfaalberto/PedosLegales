with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ─── 1. Add storageBucket to Firebase config ──────────────────────────────────
OLD_CFG = '''const FIREBASE_CONFIG_FALLBACK = {
  apiKey: "AIzaSyB9T9Uado1Q-O3P8D-MZl-b7v3GCkNfCCA",
  authDomain: "pedoslegales.firebaseapp.com",
  projectId: "pedoslegales",
  appId: "1:638020457588:web:9c947c0363f94e2e33ad21"
};'''

NEW_CFG = '''const FIREBASE_CONFIG_FALLBACK = {
  apiKey: "AIzaSyB9T9Uado1Q-O3P8D-MZl-b7v3GCkNfCCA",
  authDomain: "pedoslegales.firebaseapp.com",
  projectId: "pedoslegales",
  storageBucket: "pedoslegales.firebasestorage.app",
  messagingSenderId: "638020457588",
  appId: "1:638020457588:web:9c947c0363f94e2e33ad21"
};'''

c = c.replace(OLD_CFG, NEW_CFG)
print("1. storageBucket added:", 'storageBucket' in c)

# ─── 2. Fix ocrProgress display:none → show it when files arrive ─────────────
# The handleFiles sets innerHTML on ocrProgress but it starts hidden
# Fix: remove display:none and let it show/hide via JS
c = c.replace(
    '<div id="ocrProgress" class="alert alert-info" style="margin-top:14px;display:none"></div>',
    '<div id="ocrProgress" class="alert alert-info" style="margin-top:14px"></div>'
)
print("2. ocrProgress always visible:", 'id="ocrProgress" class="alert' in c)

# ─── 3. Fix handleFiles to show ocrBar and ocrProgress properly ───────────────
# The original handleFiles doesn't show the ocrBar. Patch it.
OLD_HF = '''function handleFiles(fileList){if(!state.activeCaseId){alert("Crea o selecciona un caso primero.");return}const files=[...fileList];const allowed=files.filter(f=>isSupported(f));const rejected=files.length-allowed.length;  allowed.forEach(f=>state.queue.push({file:f,path:f.webkitRelativePath||f.name,status:"pendiente"}));
  const parts=[];
  if(allowed.length)parts.push(`${allowed.length} archivo(s) agregados a la cola.`);
  if(rejected)parts.push(`${rejected} ignorado(s) ??? solo se admiten PDF, im??genes y Word (.docx/.doc).`);
  if(parts.length)$("ocrProgress").innerHTML=parts.join(" ");
  renderQueue()}'''

NEW_HF = '''function handleFiles(fileList){
  if(!state.activeCaseId){alert("Crea o selecciona un caso primero. Ve a 'Expedientes' y abre uno.");return;}
  const files=[...fileList];
  const allowed=files.filter(f=>isSupported(f));
  const rejected=files.length-allowed.length;
  allowed.forEach(f=>state.queue.push({file:f,path:f.webkitRelativePath||f.name,status:"pendiente"}));
  const parts=[];
  if(allowed.length) parts.push("✅ "+allowed.length+" archivo(s) en cola. Haz clic en 'Iniciar procesamiento'.");
  if(rejected) parts.push("⚠️ "+rejected+" ignorado(s) — solo PDF, imágenes y Word (.docx/.doc).");
  const prog=$("ocrProgress");
  if(prog){prog.innerHTML=parts.join(" ")||"Cola vacía.";prog.style.display="";}
  const bar=$("ocrBar");
  if(bar){bar.style.display="";bar.value=0;}
  renderQueue();
}'''
c = c.replace(OLD_HF, NEW_HF)
print("3. handleFiles fixed:", '✅' in c)

# ─── 4. Fix processQueue to also show ocrBar ─────────────────────────────────
# Check if ocrBar is shown at start of processQueue
OLD_PQ_START = '''async function processQueue(){
 if(!state.queue.length){alert("Cola vac??a.");return}const c=await activeCase();if(!c){alert("Selecciona caso.");return}
 $("ocrBar").value=0;let done=0;'''
NEW_PQ_START = '''async function processQueue(){
 if(!state.queue.length){alert("Cola vacía. Arrastra archivos primero.");return;}
 const c=await activeCase();
 if(!c){alert("Selecciona o crea un expediente primero.");return;}
 const bar=$("ocrBar");const prog=$("ocrProgress");
 if(bar){bar.style.display="";bar.value=0;}
 if(prog){prog.style.display="";prog.innerHTML="⏳ Iniciando procesamiento...";}
 let done=0;'''
c = c.replace(OLD_PQ_START, NEW_PQ_START)
print("4. processQueue start fixed:", 'Iniciando procesamiento' in c)

# ─── 5. Fix processQueue item done — show ocrBar update ──────────────────────
OLD_PQ_DONE = '''  done++;$("ocrBar").value=Math.round(done/state.queue.length*100);$("ocrProgress").innerHTML=`Procesados ${done}/${state.queue.length}`;renderQueue();'''
NEW_PQ_DONE = '''  done++;
  if(bar){bar.value=Math.round(done/state.queue.length*100);}
  if(prog){prog.innerHTML=`✅ Procesados ${done} / ${state.queue.length}`;}
  renderQueue();'''
c = c.replace(OLD_PQ_DONE, NEW_PQ_DONE)
print("5. processQueue progress fixed:", '✅ Procesados' in c)

# ─── 6. Fix processQueue completion ──────────────────────────────────────────
# Find and fix the end of processQueue to show completion message
OLD_PQ_END = ''' state.queue=[];await saveState();renderAll();alert("Procesamiento completo.");'''
NEW_PQ_END = ''' state.queue=[];await saveState();await renderAll();
 if(prog){prog.innerHTML="✅ Procesamiento completo. Ve a 'Documentos' para ver los archivos cargados.";}
 if(bar){bar.value=100;}'''
c = c.replace(OLD_PQ_END, NEW_PQ_END)
print("6. processQueue completion fixed:", 'Procesamiento completo. Ve' in c)

# ─── 7. Fix dropZone — the HTML has ondragover/ondrop attrs AND setupDrop adds listeners → double handlers
# Remove the HTML attrs and rely only on setupDrop
OLD_DROPZONE = '''<div id="dropZone" class="drop-zone" onclick="document.getElementById('fileInput').click()" ondragover="event.preventDefault();this.classList.add('drag')" ondragleave="this.classList.remove('drag')" ondrop="this.classList.remove('drag');handleFiles(event.dataTransfer.files)">'''
NEW_DROPZONE = '''<div id="dropZone" class="drop-zone" onclick="document.getElementById('fileInput').click()">'''
c = c.replace(OLD_DROPZONE, NEW_DROPZONE)
print("7. dropZone attrs cleaned:", 'ondragover' not in c or c.count('ondragover')==0)

# ─── 8. Also fix renderQueue glue to not conflict ─────────────────────────────
OLD_RQ_GLUE = '''// queueList render
const _origRenderQueue=window.renderQueue;
function renderQueue(){
  const el=document.getElementById("queueList");
  const bar=document.getElementById("ocrBar");
  const prog=document.getElementById("ocrProgress");
  if(!el)return;
  if(!state.queue.length){el.innerHTML="";if(bar)bar.style.display="none";if(prog)prog.style.display="none";return;}
  if(bar)bar.style.display="";
  el.innerHTML=state.queue.map(q=>`<div class="alert ${q.status==="ok"?"alert-ok":q.status.startsWith("error")?"alert-err":"alert-info"}" style="margin:6px 0"><b>${esc(q.file.name)}</b> <span style="float:right">${esc(q.status)}</span></div>`).join("");
}'''
NEW_RQ_GLUE = '''// renderQueue — show queue items with status
function renderQueue(){
  const el=document.getElementById("queueList");
  if(!el)return;
  if(!state.queue.length){el.innerHTML="<p style='color:var(--mut);font-size:.82rem;padding:8px 0'>Cola vacía.</p>";return;}
  el.innerHTML=state.queue.map(q=>{
    const cls=q.status==="ok"?"alert-ok":q.status.startsWith("error")?"alert-err":q.status==="procesando"?"alert-warn":"alert-info";
    const icon=q.status==="ok"?"✅":q.status.startsWith("error")?"❌":q.status==="procesando"?"⏳":"📄";
    const kb=q.file?.size?((q.file.size/1024).toFixed(0)+" KB"):"";
    return `<div class="alert ${cls}" style="margin:5px 0;display:flex;align-items:center;gap:8px">
      <span style="font-size:1.1rem">${icon}</span>
      <span style="flex:1"><b>${esc(q.file?.name||"")}</b> <span style="font-size:.72rem;opacity:.7">${kb}</span></span>
      <span style="font-size:.72rem">${esc(q.status)}</span>
    </div>`;
  }).join("");
}'''
c = c.replace(OLD_RQ_GLUE, NEW_RQ_GLUE)
print("8. renderQueue glue improved:", 'Cola vacía' in c)

# ─── 9. Verify file size and balance ─────────────────────────────────────────
print(f"\nFile: {len(c)} chars")
scripts_o = c.count('<script'); scripts_c = c.count('</script>')
divs_o = c.count('<div'); divs_c = c.count('</div>')
print(f"Scripts: {scripts_o}/{scripts_c}  Divs: {divs_o}/{divs_c} diff={divs_o-divs_c}")

with open('public/index.html','w',encoding='utf-8') as f:
    f.write(c)
print("Done!")
