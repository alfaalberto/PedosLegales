import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ─── 1. Add marked.js CDN + custom CSS in <head> ──────────────────────────────
OLD_HEAD_END = '<link rel="icon"'
NEW_HEAD = '''<script src="https://cdn.jsdelivr.net/npm/marked@9/marked.min.js"></script>
<link rel="icon"'''
c = c.replace(OLD_HEAD_END, NEW_HEAD, 1)

# ─── 2. Add viewer CSS before </style> ────────────────────────────────────────
VIEWER_CSS = """
/* ── MARKDOWN VIEWER ── */
.md-body { font-size:.93rem; line-height:1.75; color:var(--ink); }
.md-body h1,.md-body h2 { font-size:1.05rem; font-weight:700; margin:18px 0 8px; color:#fff; border-bottom:1px solid var(--brd); padding-bottom:6px; }
.md-body h3 { font-size:.95rem; font-weight:700; margin:14px 0 6px; color:#e2e2f0; }
.md-body p { margin:0 0 10px; }
.md-body ul,.md-body ol { padding-left:22px; margin:0 0 10px; }
.md-body li { margin:4px 0; }
.md-body strong { color:#fff; font-weight:700; }
.md-body em { color:#c4b5fd; font-style:italic; }
.md-body code { font-family:'JetBrains Mono',ui-monospace,monospace; font-size:.82rem; background:rgba(255,255,255,.07); padding:2px 6px; border-radius:4px; color:#a5f3fc; }
.md-body pre { background:#000; border:1px solid var(--brd); border-radius:var(--r2); padding:14px; overflow-x:auto; margin:10px 0; }
.md-body pre code { background:transparent; padding:0; color:#a5f3fc; }
.md-body blockquote { border-left:3px solid var(--gold); margin:10px 0; padding:8px 14px; background:rgba(212,175,55,.06); border-radius:0 var(--r2) var(--r2) 0; color:#d4d4d8; }
.md-body hr { border:none; border-top:1px solid var(--brd); margin:16px 0; }
.md-body table { width:100%; border-collapse:collapse; margin:10px 0; font-size:.84rem; }
.md-body th,.md-body td { padding:8px 12px; border:1px solid var(--brd); }
.md-body th { background:rgba(255,255,255,.05); color:var(--mut); font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; }
/* ── OCR VIEWER ── */
.ocr-viewer { font-family:'Lora',Georgia,serif; font-size:.94rem; line-height:1.85; color:#e8e8f0; background:#000; border:1px solid var(--brd); border-radius:var(--r2); padding:24px 28px; max-height:400px; overflow-y:auto; white-space:pre-wrap; word-break:break-word; }
.ocr-viewer .page-break { border-top:2px dashed var(--brd); margin:16px 0; padding-top:14px; color:var(--mut); font-size:.72rem; font-family:'Inter',sans-serif; text-transform:uppercase; letter-spacing:.08em; }
/* ── DRAFT VIEWER ── */
.draft-view { font-family:'Lora',Georgia,serif; font-size:.95rem; line-height:1.9; background:#000; border:1px solid var(--brd); border-radius:var(--r2); padding:32px; min-height:500px; white-space:pre-wrap; color:#e8e8f0; }
/* ── CHAT MSG overrides ── */
.msg.assistant .md-body { color:var(--ink); }
.msg.assistant .md-body strong { color:#fff; }
.msg.assistant .md-body code { background:rgba(255,255,255,.1); }
"""
c = c.replace('</style>', VIEWER_CSS + '\n</style>', 1)

# ─── 3. Replace renderChat glue (line ~1554) with markdown version ─────────────
OLD_RCHAT = '''// renderChat for new UI
async function renderChat(){
  const msgs=(await messagesOfActive()).sort((a,b)=>a.createdAt.localeCompare(b.createdAt));
  const box=document.getElementById("chatBox");if(!box)return;
  if(!msgs.length){box.innerHTML="<div style='color:var(--mut);text-align:center;margin-top:40px;font-size:.9rem'>No hay mensajes. Escribe tu primera pregunta arriba.</div>";return;}
  box.innerHTML=msgs.map(m=>{
    const text=(m.content||"").replace(/\\n---\\nVALIDACIÓN LOCAL.*$/s,"").trim();
    const isUser=m.role==="user";
    const time=new Date(m.createdAt).toLocaleTimeString("es-MX",{hour:"2-digit",minute:"2-digit"});
    return `<div class="msg ${m.role}"><div class="msg-meta">${isUser?"Tú":("IA"+(m.meta?.model?" · "+esc(m.meta.model):""))} · ${time}</div>${esc(text)}</div>`;
  }).join("");
  box.scrollTop=box.scrollHeight;
}'''

NEW_RCHAT = '''// renderChat for new UI — with Markdown rendering for AI responses
function mdRender(text){
  if(typeof marked==="undefined") return "<pre>"+esc(text)+"</pre>";
  try{
    marked.setOptions({breaks:true,gfm:true});
    return marked.parse(text);
  }catch(e){return "<pre>"+esc(text)+"</pre>";}
}
async function renderChat(){
  const msgs=(await messagesOfActive()).sort((a,b)=>a.createdAt.localeCompare(b.createdAt));
  const box=document.getElementById("chatBox");if(!box)return;
  if(!msgs.length){
    box.innerHTML="<div style='color:var(--mut);text-align:center;margin-top:60px'><div style=\\'font-size:2rem;margin-bottom:12px\\'>💬</div>Escribe tu primera pregunta sobre el expediente</div>";
    return;
  }
  box.innerHTML=msgs.map(m=>{
    let text=(m.content||"").replace(/\\n---\\nVALIDACIÓN LOCAL[\\s\\S]*$/,"").trim();
    const isUser=m.role==="user";
    const time=new Date(m.createdAt).toLocaleTimeString("es-MX",{hour:"2-digit",minute:"2-digit"});
    const meta=isUser?"Tú":("IA"+(m.meta?.model?" · <span style=\\'font-size:.65rem;opacity:.7\\'>"+esc(m.meta.model)+"</span>":""));
    const body=isUser?"<p style=\\'margin:0\\'>"+esc(text)+"</p>":("<div class=\\'md-body\\'>"+mdRender(text)+"</div>");
    return `<div class="msg ${m.role}"><div class="msg-meta">${meta} · ${time}</div>${body}</div>`;
  }).join("");
  box.scrollTop=box.scrollHeight;
}'''

c = c.replace(OLD_RCHAT, NEW_RCHAT)
print("renderChat replaced:", 'mdRender' in c)

# ─── 4. Replace the original renderChat (line ~1146) to not conflict ──────────
# The original at line 1146 uses esc(m.content) — replace with mdRender too
OLD_RCHAT_ORIG = '''async function renderChat(){
 const msgs=(await messagesOfActive()).sort((a,b)=>a.createdAt.localeCompare(b.createdAt));
 $("chatBox").innerHTML=msgs.map(m=>`<div class="msg ${m.role}"><div class="msgmeta">${esc(m.role)} · ${esc(new Date(m.createdAt).toLocaleString())}${m.meta?.model?` · ${esc(m.meta.model)}`:""}</div>${esc(m.content)}</div>`).join("")||"<p class='muted'>Sin mensajes. Haz una pregunta sobre el caso activo.</p>";
 $("chatBox").scrollTop=$("chatBox").scrollHeight;
}'''
NEW_RCHAT_ORIG = '// renderChat — overridden by glue version below'
c = c.replace(OLD_RCHAT_ORIG, NEW_RCHAT_ORIG)
print("original renderChat stubbed:", '// renderChat — overridden' in c)

# ─── 5. Replace renderSelectedDoc to show formatted OCR viewer ────────────────
OLD_RSD_LINE = '$(\"sourcePreview\").innerHTML=d.blob?`<b>Original guardado localmente.</b><br><span class=\"small\">Tipo: ${esc(d.mimeType)}.</span><div id=\"blobPreview\"></div>`:\"No se guard\u00f3 archivo original local; solo texto/metadatos.\"; if(d.blob) renderBlobPreview(d);'

NEW_RSD_LINE = '''$(\"sourcePreview\").innerHTML=d.blob?`<b>Original guardado.</b> <span class="small">Tipo: ${esc(d.mimeType)}.</span><div id="blobPreview" style="margin-top:10px"></div>`:"<p class='tiny muted'>No se guardó blob local.</p>";
  if(d.blob) renderBlobPreview(d);
  // Show formatted OCR text (replace textarea preview with rich viewer)
  const ocrViewEl=document.getElementById("ocrRichView");
  if(ocrViewEl){
    const ocrText=d.ocrText||"";
    // Split into pages and render
    const pages=ocrText.split(/---\s*P[ÁA]GINA\s+\d+\s*---/i);
    if(pages.length>1){
      ocrViewEl.innerHTML=pages.map((p,i)=>{
        const pageNum=i+1;
        return (i>0?`<div class="page-break">— Página ${pageNum} —</div>`:"")+"<p>"+esc(p.trim()).replace(/\\n/g,"<br>")+"</p>";
      }).join("");
    } else {
      ocrViewEl.innerHTML="<p>"+esc(ocrText.trim()).replace(/\\n/g,"<br>")+"</p>";
    }
  }'''

c = c.replace(OLD_RSD_LINE, NEW_RSD_LINE)
print("renderSelectedDoc OCR viewer:", 'ocrRichView' in c)

# ─── 6. Add OCR rich viewer element above the textarea in document visor ──────
OLD_VISOR_FIELD = '<div class="field"><label>Texto extraído (OCR)</label><textarea id="selectedText" style="min-height:200px"></textarea></div>'
NEW_VISOR_FIELD = '''<div class="field">
              <label>Vista del documento (OCR)</label>
              <div id="ocrRichView" class="ocr-viewer" style="min-height:160px">Sin texto OCR disponible.</div>
              <details style="margin-top:8px">
                <summary style="cursor:pointer;font-size:.72rem;color:var(--mut);user-select:none">✏️ Editar/corregir texto OCR</summary>
                <textarea id="selectedText" style="min-height:160px;margin-top:8px;width:100%;background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:10px;color:var(--ink);font:inherit;font-size:.85rem;resize:vertical;outline:none"></textarea>
              </details>
            </div>'''
c = c.replace(OLD_VISOR_FIELD, NEW_VISOR_FIELD)
print("OCR viewer element added:", 'ocrRichView' in c)

# ─── 7. Replace draftEditor textarea with a rich viewer + edit toggle ─────────
OLD_DRAFT_EDITOR = '<textarea id="draftEditor" style="width:100%;min-height:400px;background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:14px;color:var(--ink);font:inherit;font-size:.88rem;line-height:1.7;outline:none;resize:vertical;margin-top:10px"></textarea>'
NEW_DRAFT_EDITOR = '''<div style="margin-top:10px">
              <div style="display:flex;gap:8px;margin-bottom:8px">
                <button class="btn btn-ghost btn-sm" onclick="toggleDraftEdit(false)" id="btnDraftView" style="border-color:var(--gold);color:var(--gold)">👁 Vista</button>
                <button class="btn btn-ghost btn-sm" onclick="toggleDraftEdit(true)" id="btnDraftEdit">✏️ Editar</button>
              </div>
              <div id="draftRichView" class="draft-view md-body" style="display:block"></div>
              <textarea id="draftEditor" style="display:none;width:100%;min-height:400px;background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:14px;color:var(--ink);font:inherit;font-size:.88rem;line-height:1.7;outline:none;resize:vertical"></textarea>
            </div>'''
c = c.replace(OLD_DRAFT_EDITOR, NEW_DRAFT_EDITOR)
print("Draft editor replaced:", 'draftRichView' in c)

# ─── 8. Update renderDrafts to also populate the rich view ─────────────────────
OLD_DRAFT_SEL = '''  const meta=document.getElementById("draftMeta");
  const ed=document.getElementById("draftEditor");
  if(meta)meta.textContent=sel?sel.title:"Selecciona un borrador de la lista";
  if(ed)ed.value=sel?.content||"";'''
NEW_DRAFT_SEL = '''  const meta=document.getElementById("draftMeta");
  const ed=document.getElementById("draftEditor");
  const rv=document.getElementById("draftRichView");
  if(meta)meta.textContent=sel?sel.title:"Selecciona un borrador de la lista";
  if(ed)ed.value=sel?.content||"";
  if(rv)rv.innerHTML=sel?.content?mdRender(sel.content):"<p style='color:var(--mut)'>Selecciona un borrador.</p>";'''
c = c.replace(OLD_DRAFT_SEL, NEW_DRAFT_SEL)
print("renderDrafts rich view updated:", 'draftRichView' in c)

# ─── 9. Add toggleDraftEdit and saveDraftVersion patch in glue ────────────────
ADD_TO_GLUE = '''
// Draft view/edit toggle
function toggleDraftEdit(edit){
  const ed=document.getElementById("draftEditor");
  const rv=document.getElementById("draftRichView");
  const btnV=document.getElementById("btnDraftView");
  const btnE=document.getElementById("btnDraftEdit");
  if(!ed||!rv)return;
  if(edit){
    rv.style.display="none";ed.style.display="";
    if(btnV){btnV.style.borderColor="";btnV.style.color="";}
    if(btnE){btnE.style.borderColor="var(--gold)";btnE.style.color="var(--gold)";}
  } else {
    ed.style.display="none";rv.style.display="";
    rv.innerHTML=ed.value?mdRender(ed.value):"<p style='color:var(--mut)'>Borrador vacío.</p>";
    if(btnV){btnV.style.borderColor="var(--gold)";btnV.style.color="var(--gold)";}
    if(btnE){btnE.style.borderColor="";btnE.style.color="";}
  }
}
'''

# Insert before initFirebase(); at the end
c = c.replace('initFirebase();\n</script>', ADD_TO_GLUE + 'initFirebase();\n</script>', 1)
print("toggleDraftEdit added:", 'toggleDraftEdit' in c)

# ─── VERIFY ───────────────────────────────────────────────────────────────────
print(f"\nFile size: {len(c)} chars")
print(f"Script balance: opens={c.count('<script')}, closes={c.count('</script>')}")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done!")
