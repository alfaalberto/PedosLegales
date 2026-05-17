import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ─── 1. Enable blob storage by default ───────────────────────────────────────
c = c.replace(
    '<input id="storeBlob" type="hidden" value="no">',
    '<input id="storeBlob" type="hidden" value="yes">'
)
print("1. storeBlob=yes:", 'value="yes"' in c)

# ─── 2. Add native viewer CSS ─────────────────────────────────────────────────
VIEWER_CSS = """
/* ── NATIVE DOC VIEWER ── */
.doc-viewer-wrap{margin-top:20px;border:1px solid var(--brd);border-radius:var(--r);overflow:hidden;background:#000}
.doc-viewer-toolbar{display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--s);border-bottom:1px solid var(--brd);flex-wrap:wrap}
.doc-viewer-toolbar .vt-title{font-size:.8rem;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--mut)}
.doc-viewer-toolbar .vt-badge{font-size:.68rem;padding:2px 8px;border-radius:4px;background:rgba(79,142,247,.15);color:#7eb3ff;white-space:nowrap}
.doc-viewer-inner{min-height:400px;max-height:75vh;overflow:auto;position:relative;background:#1a1a1a;display:flex;flex-direction:column;align-items:center;padding:20px}
.doc-viewer-inner img{max-width:100%;border-radius:4px;box-shadow:0 4px 20px rgba(0,0,0,.5)}
.doc-viewer-inner iframe{width:100%;min-height:65vh;border:none;background:#fff;border-radius:4px}
.pdf-page-wrap{margin-bottom:16px;position:relative}
.pdf-page-wrap canvas{display:block;max-width:100%;border-radius:4px;box-shadow:0 4px 20px rgba(0,0,0,.5)}
.pdf-page-num{position:absolute;top:6px;right:8px;background:rgba(0,0,0,.7);color:#fff;font-size:.65rem;padding:2px 7px;border-radius:4px}
.docx-render{background:#fff;color:#111;font-family:Georgia,serif;font-size:1rem;line-height:1.8;padding:40px 48px;border-radius:4px;box-shadow:0 4px 20px rgba(0,0,0,.5);max-width:800px;width:100%;text-align:left}
.docx-render h1,.docx-render h2,.docx-render h3{font-weight:700;margin:1em 0 .4em}
.docx-render p{margin:.6em 0}
.docx-render table{border-collapse:collapse;width:100%;margin:1em 0}
.docx-render td,.docx-render th{border:1px solid #ccc;padding:6px 10px}
.viewer-no-blob{text-align:center;padding:48px 24px;color:var(--mut)}
.viewer-no-blob .nb-icon{font-size:3rem;margin-bottom:12px}
.viewer-loading{text-align:center;padding:48px;color:var(--mut)}
.pdf-nav{display:flex;align-items:center;gap:10px;padding:8px 14px;border-top:1px solid var(--brd);background:var(--s);justify-content:center}
"""
c = c.replace('</style>', VIEWER_CSS + '\n</style>', 1)
print("2. Viewer CSS added")

# ─── 3. Replace renderBlobPreview with full implementation ────────────────────
OLD_RBP = '''async function renderBlobPreview(d){
 const el=$(\"blobPreview\");if(!el)return;
 try{
  const url=URL.createObjectURL(d.blob);
  if(/^image\\//.test(d.mimeType||\"\") || /\\.(png|jpe?g|webp|bmp|tiff?)$/i.test(d.fileName||\"\")){\r\n    el.innerHTML=`<img class=\"imgPreview\" src=\"${url}\" alt=\"vista original\">`;\r\n  }else if(/pdf/i.test(d.mimeType||\"\") || /\\.pdf$/i.test(d.fileName||\"\")){\r\n    el.innerHTML=`<iframe class=\"viewerFrame\" src=\"${url}\"></iframe>`;\r\n  }else{\r\n    el.innerHTML=`<a class=\"btn secondary\" href=\"${url}\" target=\"_blank\">Abrir original</a>`;\r\n  }\r\n }catch(e){el.textContent=\"No se pudo previsualizar original: \"+e.message}\r\n}'''

NEW_RBP = '''// ── NATIVE DOCUMENT VIEWER ─────────────────────────────────────────────────
let _currentBlobUrl = null;
function _revokeBlob(){if(_currentBlobUrl){URL.revokeObjectURL(_currentBlobUrl);_currentBlobUrl=null;}}

function _viewerWrap(title, mimeTag, innerHtml, navHtml=''){
  return `<div class="doc-viewer-wrap">
    <div class="doc-viewer-toolbar">
      <span class="vt-title">📄 ${esc(title)}</span>
      <span class="vt-badge">${esc(mimeTag)}</span>
      <button class="btn btn-ghost btn-sm" id="btnDownloadBlob">⬇ Descargar</button>
      <button class="btn btn-ghost btn-sm" id="btnOpenBlob" target="_blank">🔗 Abrir</button>
    </div>
    <div class="doc-viewer-inner" id="docViewerInner">${innerHtml}</div>
    ${navHtml?`<div class="pdf-nav">${navHtml}</div>`:''}
  </div>`;
}

async function renderBlobPreview(d){
  const el = $("blobPreview"); if(!el) return;
  _revokeBlob();
  if(!d.blob){ el.innerHTML = '<div class="viewer-no-blob"><div class="nb-icon">📂</div><div>El archivo original no fue guardado localmente.<br><small>Reactiva "Guardar archivo" y vuelve a importar el documento.</small></div></div>'; return; }

  el.innerHTML = '<div class="viewer-loading">⏳ Cargando vista previa...</div>';
  const mime = d.mimeType || guessMime(d.fileName || '');
  const fname = d.fileName || '';
  _currentBlobUrl = URL.createObjectURL(d.blob);

  // ── IMAGES ──────────────────────────────────────────────────────────────
  if(/^image\\//.test(mime) || /\\.(png|jpe?g|webp|bmp|gif|tiff?)$/i.test(fname)){
    el.innerHTML = _viewerWrap(fname, 'Imagen', `<img src="${_currentBlobUrl}" alt="${esc(fname)}" style="max-width:100%;border-radius:4px;box-shadow:0 4px 20px rgba(0,0,0,.5)">`);
    _attachBlobBtns(d, _currentBlobUrl);
    return;
  }

  // ── PDF ──────────────────────────────────────────────────────────────────
  if(/pdf/i.test(mime) || /\\.pdf$/i.test(fname)){
    try{
      const pdfjs = await loadPdfJs();
      const buf = await d.blob.arrayBuffer();
      const pdf = await pdfjs.getDocument({data: buf}).promise;
      const total = pdf.numPages;
      let currentPage = 1;

      async function renderPage(pageNum){
        const inner = document.getElementById('docViewerInner');
        if(!inner) return;
        inner.innerHTML = '<div class="viewer-loading">⏳ Renderizando página '+pageNum+'/'+total+'...</div>';
        const page = await pdf.getPage(pageNum);
        const vp = page.getViewport({scale: 1.8});
        const canvas = document.createElement('canvas');
        canvas.width = vp.width; canvas.height = vp.height;
        canvas.style.maxWidth = '100%';
        canvas.style.borderRadius = '4px';
        canvas.style.boxShadow = '0 4px 20px rgba(0,0,0,.5)';
        await page.render({canvasContext: canvas.getContext('2d'), viewport: vp}).promise;
        const wrap = document.createElement('div');
        wrap.className = 'pdf-page-wrap';
        const badge = document.createElement('span');
        badge.className = 'pdf-page-num';
        badge.textContent = 'Pág. '+pageNum+' / '+total;
        wrap.appendChild(canvas);
        wrap.appendChild(badge);
        inner.innerHTML = '';
        inner.appendChild(wrap);
        // update nav
        const prevBtn = document.getElementById('pdfPrev');
        const nextBtn = document.getElementById('pdfNext');
        const pageInfo = document.getElementById('pdfPageInfo');
        if(prevBtn) prevBtn.disabled = pageNum <= 1;
        if(nextBtn) nextBtn.disabled = pageNum >= total;
        if(pageInfo) pageInfo.textContent = pageNum + ' / ' + total;
      }

      const navHtml = `<button class="btn btn-ghost btn-sm" id="pdfPrev" onclick="window._pdfPrev()" disabled>◀ Anterior</button>
        <span id="pdfPageInfo" style="font-size:.82rem;color:var(--mut)">1 / ${total}</span>
        <button class="btn btn-ghost btn-sm" id="pdfNext" onclick="window._pdfNext()">Siguiente ▶</button>
        <span style="font-size:.72rem;color:var(--mut)">${total} página(s) total</span>`;

      el.innerHTML = _viewerWrap(fname, 'PDF · '+total+' páginas', '<div class="viewer-loading">⏳ Cargando...</div>', navHtml);
      _attachBlobBtns(d, _currentBlobUrl);

      window._pdfPrev = ()=>{if(currentPage>1){currentPage--;renderPage(currentPage);}};
      window._pdfNext = ()=>{if(currentPage<total){currentPage++;renderPage(currentPage);}};
      await renderPage(1);
    } catch(e){
      el.innerHTML = _viewerWrap(fname, 'PDF', `<div style="color:var(--red);padding:20px">Error renderizando PDF: ${esc(e.message)}<br><a href="${_currentBlobUrl}" target="_blank" class="btn btn-ghost btn-sm" style="margin-top:10px">🔗 Abrir en nueva pestaña</a></div>`);
    }
    return;
  }

  // ── DOCX / DOC ───────────────────────────────────────────────────────────
  if(/docx?/i.test(mime) || /\\.docx?$/i.test(fname)){
    try{
      const mammoth = await ensureMammoth();
      const buf = await d.blob.arrayBuffer();
      let result;
      try{ result = await mammoth.convertToHtml({arrayBuffer: buf}); }
      catch(e2){ result = {value:'<p>Error al convertir Word: '+esc(e2.message)+'</p>'}; }
      const html = result.value || '<p style="color:var(--mut)">Sin contenido visible.</p>';
      el.innerHTML = _viewerWrap(fname, fname.endsWith('.docx')?'Word DOCX':'Word DOC', `<div class="docx-render">${html}</div>`);
      _attachBlobBtns(d, _currentBlobUrl);
    } catch(e){
      el.innerHTML = _viewerWrap(fname, 'Word', `<div style="color:var(--red);padding:20px">No se pudo renderizar: ${esc(e.message)}</div>`);
    }
    return;
  }

  // ── FALLBACK: Download link ───────────────────────────────────────────────
  const ext = (fname.split('.').pop()||'').toUpperCase();
  el.innerHTML = _viewerWrap(fname, ext||'Archivo',
    `<div class="viewer-no-blob"><div class="nb-icon">📎</div><div>Vista previa no disponible para este formato.<br><a href="${_currentBlobUrl}" target="_blank" class="btn btn-primary btn-sm" style="margin-top:12px">🔗 Abrir archivo</a></div></div>`);
  _attachBlobBtns(d, _currentBlobUrl);
}

function _attachBlobBtns(d, url){
  setTimeout(()=>{
    const dl = document.getElementById('btnDownloadBlob');
    const op = document.getElementById('btnOpenBlob');
    if(dl) dl.onclick = ()=>{const a=document.createElement('a');a.href=url;a.download=d.fileName||'documento';a.click();};
    if(op) op.onclick = ()=>window.open(url,'_blank');
  }, 50);
}'''

c = c.replace(
    'async function renderBlobPreview(d){\n const el=$(\"blobPreview\");if(!el)return;\n try{\n  const url=URL.createObjectURL(d.blob);\n  if(/^image\\//.test(d.mimeType||\"\") || /\\.(png|jpe?g|webp|bmp|tiff?)$/i.test(d.fileName||\"\")){\r\n    el.innerHTML=`<img class=\"imgPreview\" src=\"${url}\" alt=\"vista original\">`;\r\n  }else if(/pdf/i.test(d.mimeType||\"\") || /\\.pdf$/i.test(d.fileName||\"\")){\r\n    el.innerHTML=`<iframe class=\"viewerFrame\" src=\"${url}\"></iframe>`;\r\n  }else{\r\n    el.innerHTML=`<a class=\"btn secondary\" href=\"${url}\" target=\"_blank\">Abrir original</a>`;\r\n  }\r\n }catch(e){el.textContent=\"No se pudo previsualizar original: \"+e.message}\r\n}',
    NEW_RBP
)
print("3. renderBlobPreview replaced:", '_currentBlobUrl' in c)

# ─── 4. Update the docVisorCard HTML to make blob preview the hero section ────
# Move blobPreview from sourcePreview to a dedicated section at the top
OLD_VISOR_CARD = '<div id="docVisorCard" class="card" style="margin-top:20px;display:none">\n          <div class="card-title">📋 Documento seleccionado</div>\n          <div id="selectedDocBox" class="alert alert-info" style="margin-bottom:12px"></div>\n          <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;flex-wrap:wrap">'

NEW_VISOR_CARD = '''<div id="docVisorCard" class="card" style="margin-top:20px;display:none">
          <div class="card-title">📋 Documento seleccionado</div>
          <div id="selectedDocBox" class="alert alert-info" style="margin-bottom:12px"></div>
          <!-- Native document viewer hero -->
          <div id="blobPreview"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;flex-wrap:wrap;margin-top:20px">'''

c = c.replace(OLD_VISOR_CARD, NEW_VISOR_CARD)
print("4. docVisorCard updated:", 'Native document viewer hero' in c)

# ─── 5. Remove old blobPreview from sourcePreview (now it's in its own div) ──
# The sourcePreview still exists but we move the blobPreview div up
c = c.replace(
    '<div id="sourcePreview" style="margin-top:12px"></div>',
    '<div id="sourcePreview" style="margin-top:4px"></div>'
)
print("5. sourcePreview adjusted")

# ─── 6. Verify ───────────────────────────────────────────────────────────────
scripts_open = len(__import__('re').findall(r'<script[^>]*>', c))
scripts_close = c.count('</script>')
divs_open = c.count('<div')
divs_close = c.count('</div>')
print(f"\nScript balance: {scripts_open}/{scripts_close}")
print(f"Div balance: {divs_open}/{divs_close} diff={divs_open-divs_close}")
print(f"File size: {len(c)} chars")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done!")
