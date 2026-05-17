with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ─── 1. Add sidebar nav item for Índice ───────────────────────────────────────
c = c.replace(
    '<button class="nav-item" id="nav-ajustes" onclick="showPage(\'ajustes\')"><span class="nav-icon">⚙️</span><span>Configuración</span></button>',
    '<button class="nav-item" id="nav-indice" onclick="showPage(\'indice\')"><span class="nav-icon">📊</span><span>Índice del Expediente</span></button>\n      <button class="nav-item" id="nav-ajustes" onclick="showPage(\'ajustes\')"><span class="nav-icon">⚙️</span><span>Configuración</span></button>'
)
print("1. Nav item added:", 'nav-indice' in c)

# ─── 2. Add page-indice HTML before the hidden sections div ──────────────────
INDICE_PAGE = '''
    <!-- ══ ÍNDICE ══ -->
    <div class="page" id="page-indice">
      <div class="page-header">
        <div class="page-title">📊 Índice del Expediente</div>
        <div class="page-sub" id="indiceCaseSub">Estructura y organización de todos los documentos</div>
      </div>
      <div class="page-body">
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;align-items:center">
          <select id="indiceCaseFilter" onchange="renderIndice()" style="background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:8px 12px;color:var(--ink);font:inherit;outline:none">
            <option value="">Expediente activo</option>
            <option value="all">Todos los expedientes</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="renderIndice()">🔄 Actualizar</button>
          <button class="btn btn-ghost btn-sm" onclick="exportIndice('txt')">📄 Exportar TXT</button>
          <button class="btn btn-ghost btn-sm" onclick="window.print()">🖨 Imprimir</button>
        </div>
        <div id="indiceStats" class="metrics-row" style="margin-bottom:20px"></div>
        <div id="indiceOutput"></div>
      </div>
    </div>
'''
c = c.replace('    <!-- ══ HIDDEN SECTIONS for JS compatibility ══ -->', INDICE_PAGE + '\n    <!-- ══ HIDDEN SECTIONS for JS compatibility ══ -->')
print("2. Índice page added:", 'page-indice' in c)

# ─── 3. Add CSS for the index ─────────────────────────────────────────────────
IDX_CSS = """
/* ── DOCUMENT INDEX ── */
.idx-case-block{margin-bottom:32px}
.idx-case-header{display:flex;align-items:center;gap:12px;padding:16px 20px;background:linear-gradient(135deg,rgba(212,175,55,.12),rgba(79,142,247,.06));border:1px solid var(--gold);border-radius:var(--r);margin-bottom:16px}
.idx-case-icon{font-size:1.8rem}
.idx-case-name{font-size:1.05rem;font-weight:800;color:#fff}
.idx-case-type{font-size:.75rem;color:var(--gold);margin-top:2px}
.idx-case-meta{margin-left:auto;text-align:right;font-size:.72rem;color:var(--mut)}
.idx-folder{margin-bottom:14px}
.idx-folder-label{display:flex;align-items:center;gap:8px;font-size:.78rem;font-weight:700;color:var(--mut);text-transform:uppercase;letter-spacing:.06em;padding:6px 0;border-bottom:1px solid var(--brd);margin-bottom:8px}
.idx-folder-label span{flex:1}
.idx-folder-count{background:var(--b);padding:2px 8px;border-radius:4px;font-weight:600;color:var(--ink)}
.idx-doc-row{display:grid;grid-template-columns:28px 1fr auto;align-items:start;gap:10px;padding:10px 12px;border-radius:var(--r2);transition:background .15s;border:1px solid transparent;margin-bottom:6px}
.idx-doc-row:hover{background:rgba(255,255,255,.03);border-color:var(--brd)}
.idx-doc-icon{font-size:1.1rem;margin-top:2px}
.idx-doc-info{}
.idx-doc-name{font-weight:600;font-size:.88rem;margin-bottom:3px}
.idx-doc-meta{font-size:.72rem;color:var(--mut);display:flex;gap:10px;flex-wrap:wrap}
.idx-doc-actions{display:flex;gap:6px;align-items:center;flex-shrink:0}
.idx-empty{color:var(--mut);font-size:.83rem;padding:8px 12px;font-style:italic}
.idx-stat{background:var(--b);border:1px solid var(--brd);border-radius:var(--r2);padding:14px;text-align:center}
.idx-stat-val{font-size:1.6rem;font-weight:800;color:#fff}
.idx-stat-lbl{font-size:.68rem;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.idx-type-pill{display:inline-block;padding:1px 7px;border-radius:4px;font-size:.65rem;font-weight:700;margin-right:4px}
@media print{.sidebar,.page-header,.btn,.nav-item{display:none!important}.page-body{padding:0!important}.idx-doc-actions{display:none!important}}
"""
c = c.replace('</style>', IDX_CSS + '\n</style>', 1)
print("3. Index CSS added")

# ─── 4. Add deleteCase to renderCaseGrid ──────────────────────────────────────
OLD_GRID = '''    html+=`<div class="case-card${isCur?" current":""}" onclick="selectCaseAndGo('${c.id}')">
      ${isCur?\'<div class="cc-active-badge">ACTIVO</div>\':""}
      <div class="cc-icon">${icon}</div>
      <div class="cc-name">${esc(c.name)}</div>
      <div class="cc-type">${esc(c.type||"")}</div>
      <div class="cc-stats"><span>📄 ${nd} docs</span><span>💬 ${nm} chats</span></div>
    </div>`;'''

NEW_GRID = '''    html+=`<div class="case-card${isCur?" current":""}">
      ${isCur?\'<div class="cc-active-badge">ACTIVO</div>\':""}
      <div class="cc-icon" onclick="selectCaseAndGo(\'${c.id}\')" style="cursor:pointer">${icon}</div>
      <div class="cc-name" onclick="selectCaseAndGo(\'${c.id}\')" style="cursor:pointer">${esc(c.name)}</div>
      <div class="cc-type">${esc(c.type||"")}</div>
      <div class="cc-stats"><span>📄 ${nd} docs</span><span>💬 ${nm} chats</span></div>
      <div class="btn-row" style="margin-top:10px">
        <button class="btn btn-primary btn-sm" onclick="selectCaseAndGo(\'${c.id}\')" style="flex:1">Abrir</button>
        <button class="btn btn-ghost btn-sm" onclick="showCaseIndex(\'${c.id}\')">📊</button>
        <button class="btn btn-danger btn-sm" onclick="deleteCase(\'${c.id}\',\'${esc(c.name)}\')">🗑</button>
      </div>
    </div>`;'''

c = c.replace(OLD_GRID, NEW_GRID)
print("4. Case card with delete button:", 'deleteCase' in c)

# ─── 5. Add glue functions: deleteCase, renderIndice, exportIndice, showCaseIndex
GLUE_FUNCS = '''
// ── DELETE CASE ──────────────────────────────────────────────────────────────
async function deleteCase(id, name){
  if(!confirm("¿Eliminar el expediente \\"" + name + "\\"?\\n\\nSe eliminarán también TODOS sus documentos, mensajes y borradores.\\nEsta acción no se puede deshacer.")) return;
  const docs=await byIndex("documents","caseId",id);
  for(const d of docs)await del("documents",d.id);
  const msgs=await byIndex("messages","caseId",id);
  for(const m of msgs)await del("messages",m.id);
  const drs=await byIndex("drafts","caseId",id);
  for(const dr of drs)await del("drafts",dr.id);
  await del("cases",id);
  if(state.activeCaseId===id){
    const remaining=await all("cases");
    state.activeCaseId=remaining.length?remaining[0].id:null;
    await saveState();
  }
  await renderAll();
  alert("Expediente \\"" + name + "\\" eliminado.");
}

// ── SHOW CASE INDEX (quick shortcut) ─────────────────────────────────────────
async function showCaseIndex(caseId){
  await selectCase(caseId);
  showPage("indice");
}

// ── RENDER ÍNDICE ─────────────────────────────────────────────────────────────
function _docTypeIcon(mime, fname){
  if(!fname)fname="";
  if(/pdf/i.test(mime)||/\\.pdf$/i.test(fname)) return "📕";
  if(/image/i.test(mime)||/\\.(png|jpe?g|webp|bmp|gif|tiff?)$/i.test(fname)) return "🖼";
  if(/docx?/i.test(mime)||/\\.docx?$/i.test(fname)) return "📘";
  if(/text/i.test(mime)||/\\.txt$/i.test(fname)) return "📄";
  return "📎";
}
function _typeColor(role){
  const map={"Acta administrativa":"tag-red","Citatorio":"tag-red","Notificación":"tag-warn","Respuesta ARCO":"tag-blue","Acuse":"tag-green","Prueba / anexo":"tag-blue","Borrador propio":"tag-gold","Opinión jurídica / dictamen":"tag-gold"};
  return map[role]||"tag-gray";
}
function _statusDot(d){
  if(d.reviewed||d.ocrStatus==="reviewed") return '<span style="color:var(--green)">●</span> Cotejado';
  if(d.ocrStatus==="done") return '<span style="color:var(--blue)">●</span> OCR listo';
  if(d.ocrStatus==="processing") return '<span style="color:var(--warn)">●</span> Procesando';
  return '<span style="color:var(--red)">●</span> '+  (d.ocrStatus||"Pendiente");
}

async function renderIndice(){
  const filterEl=document.getElementById("indiceCaseFilter");
  const filterVal=filterEl?.value||"";
  const allCases=await all("cases");
  const allDocs=await all("documents");

  let casesToShow=[];
  if(filterVal==="all"){
    casesToShow=allCases;
  } else {
    const ac=await activeCase();
    casesToShow=ac?[ac]:allCases;
  }

  // Stats
  const statsEl=document.getElementById("indiceStats");
  const totalDocs=allDocs.filter(d=>casesToShow.some(c=>c.id===d.caseId)).length;
  const reviewed=allDocs.filter(d=>casesToShow.some(c=>c.id===d.caseId)&&(d.reviewed||d.ocrStatus==="reviewed")).length;
  const withBlob=allDocs.filter(d=>casesToShow.some(c=>c.id===d.caseId)&&d.blob).length;
  const roles={};
  allDocs.filter(d=>casesToShow.some(c=>c.id===d.caseId)).forEach(d=>{const r=d.docRole||"Sin clasificar";roles[r]=(roles[r]||0)+1;});
  const topRole=Object.entries(roles).sort((a,b)=>b[1]-a[1])[0];

  if(statsEl) statsEl.innerHTML=`
    <div class="idx-stat"><div class="idx-stat-val">${casesToShow.length}</div><div class="idx-stat-lbl">Expedientes</div></div>
    <div class="idx-stat"><div class="idx-stat-val">${totalDocs}</div><div class="idx-stat-lbl">Documentos total</div></div>
    <div class="idx-stat"><div class="idx-stat-val" style="color:var(--green)">${reviewed}</div><div class="idx-stat-lbl">OCR cotejados</div></div>
    <div class="idx-stat"><div class="idx-stat-val" style="color:${totalDocs-reviewed>0?"var(--warn)":"var(--green)"}">${totalDocs-reviewed}</div><div class="idx-stat-lbl">Pendientes revisión</div></div>
    <div class="idx-stat"><div class="idx-stat-val" style="color:var(--blue)">${withBlob}</div><div class="idx-stat-lbl">Con archivo original</div></div>
    ${topRole?`<div class="idx-stat"><div class="idx-stat-val" style="font-size:1rem">${topRole[1]}</div><div class="idx-stat-lbl">${esc(topRole[0])}</div></div>`:""}
  `;

  // Build index HTML
  const out=document.getElementById("indiceOutput"); if(!out)return;
  let html="";
  for(const cas of casesToShow){
    const docs=allDocs.filter(d=>d.caseId===cas.id).sort((a,b)=>(a.folderPath||"").localeCompare(b.folderPath||"")||(a.fileName||"").localeCompare(b.fileName||""));
    if(!docs.length&&filterVal!=="all") continue;

    // Group by folder
    const folders={};
    docs.forEach(d=>{
      const fp=d.folderPath&&d.folderPath!==d.fileName?d.folderPath.replace(d.fileName,"").replace(/\\/+$/,"").replace(/\\\\+$/,"")||"Raíz":"Raíz";
      if(!folders[fp])folders[fp]=[];
      folders[fp].push(d);
    });

    const icon=cas.type&&cas.type.includes("ARCO")?"🗂":cas.type&&cas.type.includes("Queja")?"⚠️":cas.type&&cas.type.includes("Denuncia")?"📢":"📁";
    const created=cas.createdAt?new Date(cas.createdAt).toLocaleDateString("es-MX"):"";
    const isCur=cas.id===state.activeCaseId;

    html+=`<div class="idx-case-block">
      <div class="idx-case-header">
        <div class="idx-case-icon">${icon}</div>
        <div>
          <div class="idx-case-name">${esc(cas.name)}${isCur?' <span style="font-size:.65rem;background:var(--gold);color:#000;padding:1px 7px;border-radius:3px;vertical-align:middle">ACTIVO</span>':""}</div>
          <div class="idx-case-type">${esc(cas.type||"")}</div>
          ${cas.description?`<div style="font-size:.75rem;color:var(--mut);margin-top:4px">${esc(cas.description)}</div>`:""}
        </div>
        <div class="idx-case-meta">
          <div>${docs.length} documento(s)</div>
          ${created?`<div>Creado: ${created}</div>`:""}
          <div style="display:flex;gap:6px;justify-content:flex-end;margin-top:6px;flex-wrap:wrap">
            <button class="btn btn-primary btn-sm" onclick="selectCaseAndGo('${cas.id}')">Abrir</button>
            <button class="btn btn-danger btn-sm" onclick="deleteCase('${cas.id}','${esc(cas.name)}')">🗑 Eliminar</button>
          </div>
        </div>
      </div>`;

    // Type summary pills
    const typeMap={};
    docs.forEach(d=>{const r=d.docRole||"Sin clasificar";typeMap[r]=(typeMap[r]||0)+1;});
    html+=`<div style="margin-bottom:12px;display:flex;flex-wrap:wrap;gap:6px">`;
    Object.entries(typeMap).sort((a,b)=>b[1]-a[1]).forEach(([r,n])=>{
      html+=`<span class="tag ${_typeColor(r)}" style="font-size:.72rem">${esc(r)}: ${n}</span>`;
    });
    html+=`</div>`;

    // Folders
    const sortedFolders=Object.keys(folders).sort();
    for(const folder of sortedFolders){
      const fdocs=folders[folder];
      const folderName=folder==="Raíz"?"📂 Carpeta raíz":`📂 ${folder}`;
      html+=`<div class="idx-folder">
        <div class="idx-folder-label">
          <span>${esc(folderName)}</span>
          <span class="idx-folder-count">${fdocs.length} archivo(s)</span>
        </div>`;
      for(const d of fdocs){
        const dicon=_docTypeIcon(d.mimeType||"",d.fileName||"");
        const kb=d.size?((d.size/1024).toFixed(0)+" KB"):"";
        const folio=d.folio?`· Folio: ${esc(d.folio)}`:"";
        const auth=d.authority?`· ${esc(d.authority)}`:"";
        const dt=d.docDate?`· ${esc(d.docDate)}`:"";
        const roleTag=`<span class="idx-type-pill ${_typeColor(d.docRole||"Sin clasificar")}">${esc(d.docRole||"Sin clasificar")}</span>`;
        html+=`<div class="idx-doc-row">
          <div class="idx-doc-icon">${dicon}</div>
          <div class="idx-doc-info">
            <div class="idx-doc-name">${esc(d.fileName||"sin nombre")}</div>
            <div class="idx-doc-meta">
              ${roleTag}
              <span>${_statusDot(d)}</span>
              ${kb?`<span>💾 ${kb}</span>`:""}
              ${folio?`<span>${folio}</span>`:""}
              ${auth?`<span>${auth}</span>`:""}
              ${dt?`<span>${dt}</span>`:""}
              ${d.blob?'<span style="color:var(--green)">📎 Archivo guardado</span>':''}
            </div>
          </div>
          <div class="idx-doc-actions">
            <button class="btn btn-ghost btn-sm" onclick="selectDoc('${d.id}')">📂 Ver</button>
          </div>
        </div>`;
      }
      html+=`</div>`;
    }
    if(!docs.length){html+=`<div class="idx-empty">Sin documentos en este expediente.</div>`;}
    html+=`</div>`;
  }

  if(!casesToShow.length) html=`<div class="alert alert-warn">No hay expedientes. Crea uno en la sección "Expedientes".</div>`;
  out.innerHTML=html;

  // update sub
  const sub=document.getElementById("indiceCaseSub");
  if(sub) sub.textContent=filterVal==="all"?`Todos los expedientes (${casesToShow.length})`:casesToShow[0]?.name||"";
}

async function exportIndice(fmt){
  const allCases=await all("cases");
  const allDocs=await all("documents");
  let txt="ÍNDICE MAESTRO DE EXPEDIENTES\\n"+"=".repeat(60)+"\\n\\n";
  txt+=`Generado: ${new Date().toLocaleString("es-MX")}\\n`;
  txt+=`Expedientes: ${allCases.length}  |  Documentos: ${allDocs.length}\\n\\n`;
  for(const cas of allCases){
    const docs=allDocs.filter(d=>d.caseId===cas.id).sort((a,b)=>(a.folderPath||"").localeCompare(b.folderPath||""));
    txt+=`${"━".repeat(60)}\\n`;
    txt+=`EXPEDIENTE: ${cas.name}\\n`;
    txt+=`Tipo: ${cas.type||"—"}  |  Documentos: ${docs.length}\\n`;
    if(cas.description) txt+=`Desc: ${cas.description}\\n`;
    txt+="\\n";
    const folders={};
    docs.forEach(d=>{
      const fp=d.folderPath&&d.folderPath!==d.fileName?d.folderPath.replace(d.fileName,"").replace(/\\/+$/,"").replace(/\\\\+$/,"")||"Raíz":"Raíz";
      if(!folders[fp])folders[fp]=[];
      folders[fp].push(d);
    });
    for(const [folder,fdocs] of Object.entries(folders).sort()){
      txt+=`  📂 ${folder} (${fdocs.length} archivo(s))\\n`;
      fdocs.forEach((d,i)=>{
        txt+=`     ${i+1}. ${d.fileName||"sin nombre"}\\n`;
        txt+=`        Tipo: ${d.docRole||"Sin clasificar"} | Estado: ${d.ocrStatus||"—"} | ${d.reviewed?"Cotejado":"No cotejado"}\\n`;
        if(d.folio) txt+=`        Folio: ${d.folio}\\n`;
        if(d.authority) txt+=`        Autoridad: ${d.authority}\\n`;
        if(d.docDate) txt+=`        Fecha doc: ${d.docDate}\\n`;
      });
      txt+="\\n";
    }
  }
  downloadText(txt,"indice_maestro_defensaipn_"+new Date().toISOString().slice(0,10)+".txt");
}
'''

c = c.replace('initFirebase();\n</script>', GLUE_FUNCS + '\ninitFirebase();\n</script>', 1)
print("5. Glue functions added:", 'deleteCase' in c and 'renderIndice' in c)

# ─── 6. Add renderIndice call in showPage ────────────────────────────────────
c = c.replace(
    "if(name===\"ajustes\"){renderStorage();checkHealth().catch(()=>{});resolveModel().catch(()=>{});}",
    "if(name===\"ajustes\"){renderStorage();checkHealth().catch(()=>{});resolveModel().catch(()=>{});}\n  if(name===\"indice\")renderIndice();"
)
print("6. showPage triggers renderIndice:", 'name==="indice"' in c)

# ─── 7. Update renderAll to include indice ────────────────────────────────────
c = c.replace(
    'if(id==="ajustes"){renderStorage();renderAudit();}',
    'if(id==="ajustes"){renderStorage();renderAudit();}\n  if(id==="indice")renderIndice();'
)
print("7. renderAll updated:", 'id==="indice"' in c)

# ─── 8. Add indice to goTab map ───────────────────────────────────────────────
c = c.replace(
    "const map={cases:\"casos\",import:\"import\",inbox:\"documents\",documents:\"documents\",viewer:\"documents\",index:\"ajustes\",chat:\"chat\",drafts:\"drafts\",privacy:\"ajustes\",exporter:\"ajustes\",audit:\"ajustes\",panel:\"casos\",workflow:\"casos\"};",
    "const map={cases:\"casos\",import:\"import\",inbox:\"documents\",documents:\"documents\",viewer:\"documents\",index:\"indice\",chat:\"chat\",drafts:\"drafts\",privacy:\"ajustes\",exporter:\"ajustes\",audit:\"ajustes\",panel:\"casos\",workflow:\"casos\"};"
)
print("8. goTab map updated")

print(f"\nFile: {len(c)} chars")
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done!")
