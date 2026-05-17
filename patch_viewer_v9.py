import os

html_path = r"d:\PEDOS LEGALES\App_DefensaIPN\DefensaIPN_ai_v7_1_auditada_corregida\public\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add ensureDocxPreview function
new_function = """async function ensureDocxPreview(){
  if(window.docx) return window.docx;
  await loadScriptOnce("https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js","JSZip");
  await loadScriptOnce("https://cdn.jsdelivr.net/npm/docx-preview@0.3.3/dist/docx-preview.min.js","docx");
  return window.docx;
}
"""

if "ensureDocxPreview" not in content:
    content = content.replace("async function ensureMammoth()", new_function + "\nasync function ensureMammoth()")

# 2. Replace PDF logic
pdf_logic_start = "  // PDF — render with PDF.js page by page"
pdf_logic_end_marker = "  // DOCX / DOC — render with mammoth.js"

# Extract the old PDF logic
if pdf_logic_start in content and pdf_logic_end_marker in content:
    before_pdf = content.split(pdf_logic_start)[0]
    after_pdf = content.split(pdf_logic_end_marker)[1]
    
    new_pdf_logic = """  // PDF — render native iframe para ver sellos y formato original
  if(/pdf/i.test(mime)||/\\.pdf$/i.test(fname)){
    el.innerHTML=_viewerWrap(fname,'PDF Original',`<iframe src="${_currentBlobUrl}" style="width:100%; height:65vh; border:none; border-radius:4px; background:#fff; box-shadow:0 4px 24px rgba(0,0,0,0.5);"></iframe>`,'');
    _attachBlobBtns(d,_currentBlobUrl);
    return;
  }

  // DOCX / DOC — render con docx-preview para ver formato, sellos y encabezados
"""
    content = before_pdf + new_pdf_logic + after_pdf

# 3. Replace DOCX logic
docx_logic_start = "  // DOCX / DOC — render con docx-preview"
if docx_logic_start not in content:
    docx_logic_start = "  // DOCX / DOC — render with mammoth.js"

docx_logic_end_marker = "  // FALLBACK"

if docx_logic_start in content and docx_logic_end_marker in content:
    before_docx = content.split(docx_logic_start)[0]
    after_docx = content.split(docx_logic_end_marker)[1]
    
    new_docx_logic = """  // DOCX / DOC — render con docx-preview para ver formato, sellos y encabezados
  if(/docx?/i.test(mime)||/\\.docx?$/.test(fname)){
    const isDoc = /\\.doc$/i.test(fname) && !/\\.docx$/i.test(fname);
    if(isDoc) {
      el.innerHTML=_viewerWrap(fname,'Word antiguo (.doc)',`<div class="viewer-no-blob"><div class="nb-icon">⚠️</div><p>El formato .doc antiguo no soporta vista previa completa de sellos y encabezados en el navegador.<br><a href="${_currentBlobUrl}" download="${fname}" class="btn btn-primary btn-sm" style="margin-top:12px">⬇ Descargar original</a></p></div>`,'');
      _attachBlobBtns(d,_currentBlobUrl);
      return;
    }
    
    el.innerHTML=_viewerWrap(fname,'Word (docx-preview)',`<div class="viewer-loading">⏳ Cargando visor avanzado de Word (sellos y formato)...</div><div id="docxContainer" style="background:#d1d5db; width:100%; height:65vh; overflow:auto; border-radius:4px; padding:10px; box-sizing:border-box; color:#000;"></div>`,'');
    _attachBlobBtns(d,_currentBlobUrl);
    
    setTimeout(async () => {
      try{
        const docx = await ensureDocxPreview();
        const container = document.getElementById("docxContainer");
        if(container) {
          container.innerHTML = "";
          await docx.renderAsync(d.blob, container, null, {
            className: "docx-render",
            inWrapper: true,
            ignoreWidth: false,
            ignoreHeight: false,
            ignoreFonts: false,
            breakPages: true,
            useBase64URL: true
          });
        }
      }catch(e){
        console.warn("docx-preview falló, intentando mammoth...", e);
        try {
          const mammoth=await ensureMammoth();
          const buf=await d.blob.arrayBuffer();
          const result=await mammoth.convertToHtml({arrayBuffer:buf});
          const html=result.value||'<p style="color:var(--mut)">Sin contenido visible.</p>';
          const container = document.getElementById("docxContainer");
          if(container) {
             container.style.background = "#fff";
             container.innerHTML = `<div class="docx-render" style="max-width:800px; margin:0 auto; padding:40px;">${html}</div>`;
          }
        }catch(e2){
          el.innerHTML=_viewerWrap(fname,'Word',`<div style="color:var(--red);padding:20px">No se pudo renderizar: ${esc(e2.message)}</div>`,'');
        }
      }
    }, 100);
    return;
  }

  // FALLBACK
"""
    content = before_docx + new_docx_logic + after_docx

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Viewer logic successfully updated.")
