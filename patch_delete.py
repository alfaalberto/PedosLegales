import os
import re

html_path = r"d:\PEDOS LEGALES\App_DefensaIPN\DefensaIPN_ai_v7_1_auditada_corregida\public\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add "Eliminar Documento" button in Split-View
split_view_target = """<button class="btn btn-gold" onclick="saveSelectedMeta()" style="width:100%; margin-top:16px; font-weight:700; font-size:0.95rem;">💾 Guardar Metadatos</button>"""
split_view_replacement = """<div style="display:flex; gap:10px; margin-top:16px;">
                  <button class="btn btn-gold" onclick="saveSelectedMeta()" style="flex:2; font-weight:700; font-size:0.95rem;">💾 Guardar Metadatos</button>
                  <button class="btn btn-danger" onclick="deleteCurrentDoc()" style="flex:1; font-weight:700; font-size:0.95rem;" title="Eliminar este documento">🗑️ Borrar</button>
                </div>"""

if split_view_target in content:
    content = content.replace(split_view_target, split_view_replacement)

# 2. Add deleteCurrentDoc and deleteDuplicates functions
js_additions = """
async function deleteCurrentDoc() {
  if (!state.selectedDocId) return;
  if (!confirm("¿Eliminar PERMANENTEMENTE este documento del expediente?")) return;
  const id = state.selectedDocId;
  await del("documents", id);
  try { await delBlobLocal(id); } catch(e){}
  state.selectedDocId = null;
  const card = document.getElementById("docVisorCard");
  if(card) card.style.display = "none";
  await saveState();
  await renderAll();
  alert("Documento eliminado.");
}

async function deleteDuplicates() {
  const docs = await docsOfActive();
  const seen = new Set();
  const duplicates = [];
  
  // Identificamos duplicados basados en sha256
  for (const d of docs) {
    if (!d.sha256) continue;
    if (seen.has(d.sha256)) {
      duplicates.push(d);
    } else {
      seen.add(d.sha256);
    }
  }
  
  if (duplicates.length === 0) {
    alert("No se encontraron documentos duplicados exactos (basado en hash SHA-256) en este expediente.");
    return;
  }
  
  if (!confirm(`Se encontraron ${duplicates.length} documentos duplicados.\\n\\n¿Deseas ELIMINARLOS automáticamente para mantener tu expediente limpio?`)) return;
  
  for (const d of duplicates) {
    await del("documents", d.id);
    try { await delBlobLocal(d.id); } catch(e){}
  }
  
  if (duplicates.some(d => d.id === state.selectedDocId)) {
    state.selectedDocId = null;
    const card = document.getElementById("docVisorCard");
    if(card) card.style.display = "none";
  }
  
  await saveState();
  await renderAll();
  alert(`${duplicates.length} documento(s) duplicado(s) eliminado(s) exitosamente.`);
}
"""

if "async function deleteDoc(id){" in content:
    content = content.replace("async function deleteDoc(id){", js_additions + "\nasync function deleteDoc(id){")

# 3. Add button in the Documentos view toolbar
doc_toolbar_target = """<select id="docRoleFilter" onchange="renderDocuments()" style="background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:8px 12px;color:var(--ink);font:inherit;outline:none">"""
doc_toolbar_replacement = """<button class="btn btn-danger btn-sm" onclick="deleteDuplicates()" style="display:flex;align-items:center;gap:6px;" title="Busca y borra archivos repetidos idénticos">🗑️ Limpiar Duplicados</button>
          <select id="docRoleFilter" onchange="renderDocuments()" style="background:#000;border:1px solid var(--brd);border-radius:var(--r2);padding:8px 12px;color:var(--ink);font:inherit;outline:none">"""

if doc_toolbar_target in content:
    content = content.replace(doc_toolbar_target, doc_toolbar_replacement)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Delete features added successfully.")
