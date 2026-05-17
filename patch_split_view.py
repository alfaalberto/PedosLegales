import os
import re

html_path = r"d:\PEDOS LEGALES\App_DefensaIPN\DefensaIPN_ai_v7_1_auditada_corregida\public\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace the HTML structure for #docVisorCard
old_html_start = """        <!-- Visor integrado -->
        <div id="docVisorCard" class="card" style="margin-top:20px;display:none">"""
old_html_end = """          <div id="sourcePreview" style="margin-top:4px"></div>
        </div>"""

new_html = """        <!-- Visor integrado (Side-by-Side) -->
        <div id="docVisorCard" class="card" style="margin-top:20px;display:none;padding:24px;border-top:4px solid var(--blue);">
          <div class="card-title" style="margin-bottom:16px;">📋 Cotejo de Documento</div>
          <div id="selectedDocBox" class="alert alert-info" style="margin-bottom:20px"></div>
          
          <!-- CONTENEDOR PRINCIPAL SIDE-BY-SIDE -->
          <div style="display:flex; gap:24px; align-items: stretch; flex-wrap:wrap;">
            
            <!-- PANEL IZQUIERDO: VISOR ORIGINAL -->
            <div style="flex:1; min-width:400px; display:flex; flex-direction:column; background:var(--s); border:1px solid var(--brd); border-radius:var(--r2); box-shadow:0 10px 30px rgba(0,0,0,0.4); overflow:hidden;">
               <div style="background:rgba(255,255,255,0.05); padding:12px 18px; border-bottom:1px solid var(--brd); display:flex; justify-content:space-between; align-items:center;">
                 <span style="font-weight:700; color:#fff;">📄 Documento Original</span>
                 <div id="sourcePreview" style="font-size:0.75rem; color:var(--mut);"></div>
               </div>
               <div id="blobPreview" style="background:#f0f0f5; flex:1; min-height:65vh; display:flex; flex-direction:column;">
                  <!-- Aquí se inyecta iframe o canvas -->
               </div>
            </div>

            <!-- PANEL DERECHO: OCR Y METADATOS -->
            <div style="flex:1; min-width:400px; display:flex; flex-direction:column; gap:20px;">
              
              <!-- SECCIÓN OCR -->
              <div class="field" style="margin:0; display:flex; flex-direction:column; flex:1;">
                <label style="color:var(--blue); font-weight:700; font-size:0.95rem;">⌨️ Texto extraído (OCR) para cotejo</label>
                <div id="ocrRichView" class="ocr-viewer" style="flex:1; height:45vh; resize:vertical; margin-top:8px; border-radius:8px;">Sin texto OCR disponible.</div>
                
                <details style="margin-top:12px">
                  <summary style="cursor:pointer;font-size:.8rem;color:var(--gold);user-select:none;font-weight:600;">✏️ Editar / corregir texto extraído manualmente</summary>
                  <textarea id="selectedText" style="min-height:250px;margin-top:12px;width:100%;background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:14px;color:var(--ink);font-family:'JetBrains Mono',monospace;font-size:.85rem;resize:vertical;outline:none;box-shadow:inset 0 0 10px rgba(0,0,0,0.5);"></textarea>
                </details>

                <div class="btn-row" style="margin-top:14px;">
                  <button class="btn btn-primary" onclick="saveSelectedText()" style="flex:1;">💾 Guardar corrección</button>
                  <button class="btn btn-ghost" onclick="markReviewed()" style="border-color:var(--green); color:var(--green); flex:1;">✅ Marcar cotejado</button>
                </div>
              </div>

              <!-- SECCIÓN METADATOS -->
              <div style="background:rgba(255,255,255,0.02); padding:18px; border-radius:var(--r2); border:1px solid var(--brd); margin-top:auto;">
                <div style="font-weight:700; margin-bottom:16px; color:#fff; font-size:0.95rem;">🏷️ Clasificación y Metadatos</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
                  <div class="field" style="margin:0;"><label>Folio / Oficio</label><input id="selectedFolio" placeholder="Ej: OFICIO/2024"></div>
                  <div class="field" style="margin:0;"><label>Remitente</label><input id="selectedAuthority" placeholder="Autoridad"></div>
                  <div class="field" style="margin:0;"><label>Fecha</label><input id="selectedDocDate" type="date"></div>
                  <div class="field" style="margin:0;"><label>Clasificación</label>
                    <select id="selectedRole"><option>Sin clasificar</option><option>Citatorio</option><option>Acta administrativa</option><option>Notificación</option><option>Opinión jurídica / dictamen</option><option>Respuesta ARCO</option><option>Acuerdo</option><option>Queja / denuncia</option><option>Oficio</option><option>Correo</option><option>Acuse</option><option>Prueba / anexo</option><option>Borrador propio</option><option>Otro</option></select>
                  </div>
                  <div class="field" style="grid-column: span 2; margin:0;"><label>Estado procesal</label>
                    <select id="selectedStatus"><option>Pendiente de clasificación</option><option>Pendiente de cotejo</option><option>Metadatos incompletos</option><option>Listo para RAG</option><option>Listo para escrito</option><option>Solo referencia interna</option><option>No usar</option></select>
                  </div>
                  <div class="field" style="grid-column: span 2; margin:0;"><label>Notas / Relevancia</label><textarea id="selectedNotes" style="min-height:60px"></textarea></div>
                </div>
                <!-- Campos ocultos -->
                <input id="selectedStage" type="hidden" value="Ingreso">
                <input id="selectedPriority" type="hidden" value="Media">
                <input id="selectedConf" type="hidden" value="Interno">
                <input id="selectedAction" type="hidden" value="">
                <input id="selectedDue" type="hidden" value="">
                <input id="storeBlob" type="hidden" value="yes">
                <input id="ocrLang" type="hidden" value="spa">
                <input id="selectedTags" type="hidden" value="">
                <button class="btn btn-gold" onclick="saveSelectedMeta()" style="width:100%; margin-top:16px; font-weight:700; font-size:0.95rem;">💾 Guardar Metadatos</button>
              </div>

            </div>
          </div>
        </div>"""

pattern_html = re.compile(r'        <!-- Visor integrado -->.*?<div id="sourcePreview" style="margin-top:4px"></div>\n        </div>', re.DOTALL)
if pattern_html.search(content):
    content = pattern_html.sub(new_html, content)
else:
    print("WARNING: Could not find HTML block to replace.")

# 2. Update renderSelectedDoc logic
# We need to remove <div id="blobPreview"> from sourcePreview.innerHTML
js_old_pattern = re.compile(r'\$\("sourcePreview"\)\.innerHTML=\(d\.blob \|\| d\.blobOmitted\)\?`<b>Original disponible\.</b> <span class="small">Tipo: \$\{esc\(d\.mimeType\)\}\.</span><div id="blobPreview" style="margin-top:10px"></div><p class=\'tiny muted\' style=\'margin-top:6px\'>Cargando visor original\.\.\.</p>`:"<p class=\'tiny muted\'>No hay archivo original para visualizar\.</p>";')

js_new = """$("sourcePreview").innerHTML=(d.blob || d.blobOmitted)?`✅ Disponible (${esc(d.mimeType)})`:`❌ Sin archivo local`; 
  if(d.blob || d.blobOmitted) renderBlobPreview(d);
  else { const bp = document.getElementById("blobPreview"); if(bp) bp.innerHTML = "<div style='color:#888; padding:30px; text-align:center;'>No se adjuntó archivo original a este documento.</div>"; }"""

if js_old_pattern.search(content):
    content = js_old_pattern.sub(js_new, content)
else:
    print("WARNING: Could not find JS block to update.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Split view layout successfully applied.")
