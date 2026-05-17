import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ─── 1. Fix docsOfActive (missing async) ────────────────────────────────────
c = c.replace(
    'function docsOfActive(){return state.activeCaseId?await byIndex("documents","caseId",state.activeCaseId):[]}',
    'async function docsOfActive(){return state.activeCaseId?await byIndex("documents","caseId",state.activeCaseId):[]}'
)
print("1. docsOfActive async fix:", 'async function docsOfActive' in c)

# ─── 2. Add missing hidden inputs that processQueue needs ────────────────────
# storeBlob, ocrLang — add to the hidden section
OLD_HIDDEN_END = '<input id="selectedDue" type="hidden" value="">'
NEW_HIDDEN_END = '''<input id="selectedDue" type="hidden" value="">
      <input id="storeBlob" type="hidden" value="no">
      <input id="ocrLang" type="hidden" value="spa">'''
c = c.replace(OLD_HIDDEN_END, NEW_HIDDEN_END)
print("2. storeBlob/ocrLang hidden inputs:", 'id="storeBlob"' in c)

# ─── 3. Add docStatusFilter hidden input (used by renderDocuments filter) ────
c = c.replace(
    '<input id="allowWeb" type="hidden" value="no">',
    '<input id="allowWeb" type="hidden" value="no">\n    <input id="docStatusFilter" type="hidden" value="">'
)
print("3. docStatusFilter:", 'id="docStatusFilter"' in c)

# ─── 4. Fix the _orig* pattern — move them to AFTER initFirebase so functions exist ──
# The issue: const _origX = window.X runs during script parse when X isn't yet defined
# Fix: wrap them in a DOMContentLoaded or just defer assignment inside boot()
# Solution: Replace the glue _orig* assignments with safe lazy getters

ORIG_ASSIGNS = '''// ── SIMPLIFIED UI GLUE (simplified interface layer) ────────────────────────
const DEFAULT_SERVER_URL = "http://localhost:8787";'''

NEW_ASSIGNS = '''// ── SIMPLIFIED UI GLUE (simplified interface layer) ────────────────────────
const DEFAULT_SERVER_URL = "http://localhost:8787";
// _orig* are resolved lazily at runtime, not at parse time
let _origRenderDocuments = null;
let _origHandleFiles = null;
let _origRenderDrafts = null;
let _origRenderChat = null;
let _origSelectDoc = null;
function _resolveOrig(){
  if(!_origRenderDocuments && typeof window._rawRenderDocuments==="function") _origRenderDocuments=window._rawRenderDocuments;
  if(!_origHandleFiles && typeof window._rawHandleFiles==="function") _origHandleFiles=window._rawHandleFiles;
}'''

# Instead, let's just fix the glue's renderDocuments to NOT call _orig and instead
# directly call the full render (which already writes to docTable correctly)

# ─── 5. Replace the glue renderDocuments wrapper with a direct implementation ──
# The original renderDocuments from JS2 already writes to docTable correctly
# The glue just needs to call it. The problem is _origRenderDocuments is null.
# Fix: use a function reference approach

OLD_RDOC = '''// Override renderDocuments to render table in new UI
const _origRenderDocuments=window.renderDocuments;
async function renderDocuments(){
  if(typeof _origRenderDocuments==="function")await _origRenderDocuments();
}'''

NEW_RDOC = '''// renderDocuments — direct implementation using docsOfActive
async function renderDocuments(){
  const docs = await docsOfActive();
  const f = (document.getElementById("docSearch")?.value||"").toLowerCase();
  const roleF = document.getElementById("docRoleFilter")?.value||"";
  const list = docs.filter(d=>{
    if(roleF && (d.docRole||"Sin clasificar")!==roleF) return false;
    return !f||JSON.stringify({...d,blob:null}).toLowerCase().includes(f);
  }).sort((a,b)=>(a.fileName||"").localeCompare(b.fileName||""));
  const tbody = document.getElementById("docTable");
  if(!tbody) return;
  if(!list.length){
    tbody.innerHTML=`<tr><td colspan="4" style="text-align:center;color:var(--mut);padding:24px">Sin documentos en este expediente. Ve a "Agregar documentos" para cargar archivos.</td></tr>`;
    return;
  }
  tbody.innerHTML = list.map(d=>{
    const ocrOk = d.ocrStatus==="done";
    const reviewed = d.reviewed;
    const stTag = reviewed?"<span class='tag tag-green'>✓ Cotejado</span>":ocrOk?"<span class='tag tag-blue'>OCR listo</span>":"<span class='tag tag-gray'>"+esc(d.ocrStatus||"pendiente")+"</span>";
    const roleTag = `<span class="tag tag-gold">${esc(d.docRole||"Sin clasificar")}</span>`;
    const name = esc(d.fileName||"");
    const kb = d.size?((d.size/1024).toFixed(0)+" KB"):"";
    return `<tr>
      <td><b>${name}</b><br><span style="font-size:.72rem;color:var(--mut)">${kb}</span></td>
      <td>${roleTag}</td>
      <td>${stTag}</td>
      <td><button class="btn btn-ghost btn-sm" onclick="selectDoc('${d.id}')">📂 Abrir</button></td>
    </tr>`;
  }).join("");
}'''

c = c.replace(OLD_RDOC, NEW_RDOC)
print("4. renderDocuments replaced:", 'Sin documentos en este expediente' in c)

# ─── 6. Fix handleFiles glue — call the JS2 native one directly ──────────────
OLD_HF = '''// handleFiles - show bar
const _origHandleFiles=window.handleFiles;
function handleFiles(fl){
  if(_origHandleFiles)_origHandleFiles(fl);
  const prog=document.getElementById("ocrProgress");
  if(prog&&state.queue.length){prog.style.display="";prog.textContent=state.queue.length+" archivo(s) en cola. Haz clic en 'Iniciar procesamiento'.";}
}'''

# The original handleFiles from JS2 is correct. The glue tried to wrap it
# but the assignment was null. Let's just remove the glue override and keep the original.
# The original handleFiles already references ocrProgress and renderQueue correctly.
c = c.replace(OLD_HF, '// handleFiles — uses native implementation from JS2 core')
print("5. handleFiles override removed:", '// handleFiles — uses native implementation' in c)

# ─── 7. Fix renderDrafts — remove _orig call, keep direct implementation ─────
OLD_RDRAFTS = '''// Override renderDrafts for new UI
const _origRenderDrafts=window.renderDrafts;
async function renderDrafts(){'''
NEW_RDRAFTS = '''// renderDrafts for new UI
async function renderDrafts(){'''
c = c.replace(OLD_RDRAFTS, NEW_RDRAFTS)
print("6. renderDrafts _orig removed")

# ─── 8. Fix renderChat — remove _orig call ────────────────────────────────────
OLD_RCHAT = '''// Chat render override (remove citation audit noise from display)
const _origRenderChat=window.renderChat;
async function renderChat(){'''
NEW_RCHAT = '''// renderChat for new UI
async function renderChat(){'''
c = c.replace(OLD_RCHAT, NEW_RCHAT)
print("7. renderChat _orig removed")

# ─── 9. Fix selectDoc — remove _orig call ─────────────────────────────────────
OLD_SDOC = '''// Override selectDoc to show visor inside documents page
const _origSelectDoc=window.selectDoc;
async function selectDoc(id){'''
NEW_SDOC = '''// selectDoc — shows visor inside documents page
async function selectDoc(id){'''
c = c.replace(OLD_SDOC, NEW_SDOC)
print("8. selectDoc _orig removed")

# ─── 10. Fix renderAll to call renderDocuments correctly ────────────────────
OLD_RALL = '''  if(id==="documents")if(typeof _origRenderDocuments==="function")await _origRenderDocuments();'''
NEW_RALL = '''  if(id==="documents")await renderDocuments();'''
c = c.replace(OLD_RALL, NEW_RALL)
print("9. renderAll uses renderDocuments directly")

# ─── 11. Add ocrProgress show in handleFiles — patch processQueue to show ocrBar ──
# processQueue already references $(\"ocrBar\") which maps to document.getElementById
# via the $ helper — should work. But ensure ocrBar is visible.
# Already handled in HTML: ocrBar has display:none initially, processQueue shows it.

# ─── 12. Verify div balance ──────────────────────────────────────────────────
opens = c.count('<div')
closes = c.count('</div>')
print(f"\n=== DIV BALANCE: opens={opens} closes={closes} diff={opens-closes} ===")

scripts_open = len([m for m in __import__('re').finditer(r'<script[^>]*>', c)])
scripts_close = c.count('</script>')
print(f"=== SCRIPT BALANCE: opens={scripts_open} closes={scripts_close} ===")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("\nDone! index.html patched.")
