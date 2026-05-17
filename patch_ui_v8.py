import os
import re

html_path = r"d:\PEDOS LEGALES\App_DefensaIPN\DefensaIPN_ai_v7_1_auditada_corregida\public\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS
css_old = """:root{--bg:#0a0a0f;--s:#111118;--b:#1c1c28;--brd:#2a2a3a;--ink:#f0f0f8;--mut:#7070a0;--gold:#d4af37;--blue:#4f8ef7;--green:#22c55e;--red:#ef4444;--warn:#f59e0b;--r:12px;--r2:8px}"""
css_new = """:root{--bg:#05050A;--s:rgba(20,20,30,0.65);--b:rgba(30,30,45,0.7);--brd:rgba(255,255,255,0.08);--ink:#f8fafc;--mut:#94a3b8;--gold:#eab308;--blue:#3b82f6;--green:#10b981;--red:#ef4444;--warn:#f59e0b;--r:16px;--r2:10px}
body{background:radial-gradient(circle at top right,#131326,#05050A);color:var(--ink);}
.sidebar{backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);background:rgba(15,15,22,0.75);}
.card, .case-card, .draft-item, .login-card, .metric-box {backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 8px 32px rgba(0,0,0,0.3);border:1px solid var(--brd);}
.btn-primary{background:linear-gradient(135deg,var(--blue),#60a5fa);box-shadow:0 4px 14px rgba(59,130,246,0.3);border:none;}
.btn-gold{background:linear-gradient(135deg,var(--gold),#fde047);box-shadow:0 4px 14px rgba(234,179,8,0.25);border:none;}
.page-header{background:linear-gradient(180deg, rgba(20,20,30,0.8) 0%, transparent 100%); border-bottom: none;}
"""

content = content.replace(css_old, css_new + css_old)

# 2. Add Nav Item
nav_old = """<button class="nav-item" id="nav-indice" onclick="showPage('indice')"><span class="nav-icon">📊</span><span>Índice del Expediente</span></button>"""
nav_new = """<button class="nav-item" id="nav-indice" onclick="showPage('indice')"><span class="nav-icon">📊</span><span>Índice del Expediente</span></button>
      <button class="nav-item" id="nav-progreso" onclick="showPage('progreso')"><span class="nav-icon">📈</span><span>Monitoreo y Avance</span></button>"""
content = content.replace(nav_old, nav_new)

# 3. Add Page
page_progreso = """
    <!-- ══ PROGRESO ══ -->
    <div class="page" id="page-progreso">
      <div class="page-header">
        <div class="page-title">📈 Monitoreo y Avance del Expediente</div>
        <div class="page-sub" id="progresoCaseSub">Tablero Kanban y Línea de Tiempo del caso activo</div>
      </div>
      <div class="page-body">
        <div id="dashboardStats" class="metrics-row"></div>
        
        <div class="card" style="margin-bottom:20px; background:transparent; border:none; box-shadow:none; padding:0;">
          <div class="card-title" style="font-size:1.1rem; padding-left:10px;">🚥 Etapas del Proceso (Tablero)</div>
          <div id="kanbanBoard" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:16px;overflow-x:auto;padding:10px;">
            <!-- Kanban columns -->
          </div>
        </div>

        <div class="card" style="margin-top:20px;">
          <div class="card-title">⏳ Línea de Tiempo de Eventos</div>
          <div id="timelineView" style="position:relative;padding-left:24px;border-left:2px solid var(--brd);margin-left:12px;margin-top:20px;">
            <!-- Timeline items -->
          </div>
        </div>
      </div>
    </div>
"""
# Insert before <!-- ══ CONFIGURACIÓN ══ -->
content = content.replace("<!-- ══ CONFIGURACIÓN ══ -->", page_progreso + "\n    <!-- ══ CONFIGURACIÓN ══ -->")

# 4. Add JavaScript logic
js_code = """
async function renderProgreso(){
  const docs = await docsOfActive();
  
  // 1. Stats
  const statsEl = document.getElementById("dashboardStats");
  if(statsEl){
    const total = docs.length;
    const reviewed = docs.filter(d=>d.reviewed||d.ocrStatus==="reviewed").length;
    const pending = docs.filter(d=>docPendingReasons(d).length>0).length;
    const health = caseHealth(docs);
    
    statsEl.innerHTML = `
      <div class="metric-box" style="background:rgba(234,179,8,0.1);border-color:rgba(234,179,8,0.3)"><div class="metric-val" style="color:var(--gold)">${health.score}%</div><div class="metric-lbl">Salud (${esc(health.label)})</div></div>
      <div class="metric-box"><div class="metric-val">${total}</div><div class="metric-lbl">Documentos</div></div>
      <div class="metric-box"><div class="metric-val" style="color:var(--green)">${reviewed}</div><div class="metric-lbl">Cotejados (OCR)</div></div>
      <div class="metric-box"><div class="metric-val" style="color:var(--warn)">${pending}</div><div class="metric-lbl">Acción Pendiente</div></div>
    `;
  }

  // 2. Kanban (Etapas)
  const kbEl = document.getElementById("kanbanBoard");
  if(kbEl){
    const stages = ["Ingreso", "Integración", "Resolución", "Cerrado"];
    const byStage = { "Ingreso": [], "Integración": [], "Resolución": [], "Cerrado": [], "Otro": [] };
    
    docs.forEach(d => {
      const s = d.stage || "Ingreso";
      if(byStage[s]) byStage[s].push(d);
      else byStage["Otro"].push(d);
    });

    let kbHtml = "";
    stages.forEach(st => {
      const items = byStage[st]||[];
      kbHtml += `<div style="background:var(--s);border:1px solid var(--brd);border-radius:var(--r2);padding:14px;min-height:200px;backdrop-filter:blur(10px);">
        <div style="font-weight:700;margin-bottom:14px;color:var(--ink);display:flex;align-items:center;justify-content:space-between;">
          <span>${st}</span>
          <span style="background:var(--brd);padding:2px 8px;border-radius:12px;font-size:0.7rem;">${items.length}</span>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          ${items.map(d=>`
            <div style="background:rgba(255,255,255,0.03);padding:10px 12px;border-radius:8px;font-size:.8rem;cursor:pointer;border:1px solid var(--brd);transition:all .2s;box-shadow:0 2px 8px rgba(0,0,0,0.2);" onclick="selectDoc('${d.id}')" onmouseover="this.style.borderColor='var(--blue)';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='var(--brd)';this.style.transform='none'">
              <div style="font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#fff;">${esc(d.fileName)}</div>
              <div style="color:var(--mut);margin-top:4px;display:flex;justify-content:space-between;align-items:center;">
                <span style="background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:4px;font-size:0.65rem;">${esc(d.docRole||"Sin clasificar")}</span>
                ${d.priority==="Urgente"||d.priority==="Alta"?'<span style="color:var(--red);font-weight:bold" title="Prioridad Alta">!</span>':''}
              </div>
            </div>
          `).join("")}
          ${items.length===0?'<div style="color:var(--mut);font-size:.75rem;text-align:center;font-style:italic;padding:20px 0;">Vacío</div>':''}
        </div>
      </div>`;
    });
    kbEl.innerHTML = kbHtml;
  }

  // 3. Timeline
  const tlEl = document.getElementById("timelineView");
  if(tlEl){
    const datedDocs = docs.filter(d=>d.docDate).sort((a,b)=>a.docDate.localeCompare(b.docDate));
    if(datedDocs.length===0){
      tlEl.innerHTML = `<div style="color:var(--mut);padding:10px 0;">No hay documentos con fecha asignada para armar la línea de tiempo. Ve a "Documentos" y captura la 'Fecha del documento' en sus metadatos.</div>`;
    } else {
      let tlHtml = "";
      datedDocs.forEach((d, i) => {
        tlHtml += `
          <div style="position:relative;margin-bottom:24px;">
            <div style="position:absolute;left:-31px;top:4px;width:14px;height:14px;background:linear-gradient(135deg, var(--blue), #60a5fa);border-radius:50%;box-shadow:0 0 10px rgba(59,130,246,0.6);border:2px solid #05050A;"></div>
            <div style="font-weight:800;color:var(--blue);font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;">${esc(d.docDate)}</div>
            <div style="background:var(--s);border:1px solid var(--brd);border-radius:var(--r2);padding:14px 18px;margin-top:8px;display:inline-block;cursor:pointer;transition:all .2s;min-width:300px;backdrop-filter:blur(8px);" onclick="selectDoc('${d.id}')" onmouseover="this.style.borderColor='var(--gold)';this.style.boxShadow='0 4px 16px rgba(0,0,0,0.4)'" onmouseout="this.style.borderColor='var(--brd)';this.style.boxShadow='none'">
              <div style="font-weight:700;color:#fff;font-size:0.95rem;margin-bottom:4px;">${esc(d.fileName)}</div>
              <div style="font-size:.8rem;color:var(--mut);">
                <span style="color:var(--gold)">${esc(d.docRole||"Sin clasificar")}</span> · 
                ${esc(d.authority||"Sin autoridad")} · Folio: ${esc(d.folio||"N/A")}
              </div>
            </div>
          </div>
        `;
      });
      tlEl.innerHTML = tlHtml;
    }
  }
}
"""

content = content.replace("function showPage(name){", js_code + "\nfunction showPage(name){")

# Register 'progreso' page in logic
content = content.replace('const NEEDS_CASE=["import","documents","chat","drafts"];', 'const NEEDS_CASE=["import","documents","chat","drafts","progreso"];')
content = content.replace('if(name==="indice")renderIndice();', 'if(name==="indice")renderIndice();\n  if(name==="progreso")renderProgreso();')
content = content.replace('if(id==="indice")renderIndice();', 'if(id==="indice")renderIndice();\n  if(id==="progreso")renderProgreso();')

# Further UX Fixes
# 1. Update the document viewer UI slightly to be more premium
doc_viewer_old = """.doc-viewer-wrap{margin-top:20px;border:1px solid var(--brd);border-radius:var(--r);overflow:hidden;background:#000}"""
doc_viewer_new = """.doc-viewer-wrap{margin-top:20px;border:1px solid var(--brd);border-radius:var(--r);overflow:hidden;background:rgba(0,0,0,0.6);box-shadow:inset 0 0 20px rgba(0,0,0,0.8);}"""
content = content.replace(doc_viewer_old, doc_viewer_new)

# 2. Add transition to sidebar elements for smoother feel
nav_css_old = """.nav-item{display:flex;align-items:center;gap:10px;padding:10px 18px;cursor:pointer;color:var(--mut);font-size:.85rem;font-weight:500;transition:all .15s;border:none;background:transparent;width:100%;text-align:left;border-left:3px solid transparent}"""
nav_css_new = """.nav-item{display:flex;align-items:center;gap:10px;padding:12px 20px;margin:2px 10px;border-radius:8px;cursor:pointer;color:var(--mut);font-size:.88rem;font-weight:500;transition:all .2s ease;border:none;background:transparent;width:calc(100% - 20px);text-align:left;}
.nav-item:hover{color:var(--ink);background:rgba(255,255,255,.05);transform:translateX(2px);}
.nav-item.active{color:#fff;font-weight:600;background:linear-gradient(90deg, rgba(59,130,246,0.15), transparent);border-left:3px solid var(--blue);}
"""
content = content.replace(nav_css_old, nav_css_new)
content = content.replace(""".nav-item:hover{color:var(--ink);background:rgba(255,255,255,.03)}""", "")
content = content.replace(""".nav-item.active{color:#fff;font-weight:600;background:rgba(212,175,55,.08);border-left-color:var(--gold)}""", "")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
