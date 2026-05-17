import os

html_path = r"d:\PEDOS LEGALES\App_DefensaIPN\DefensaIPN_ai_v7_1_auditada_corregida\public\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS for ocr-viewer
css_old = """/* ── OCR VIEWER ── */
.ocr-viewer { font-family:'Lora',Georgia,serif; font-size:.94rem; line-height:1.85; color:#e8e8f0; background:#000; border:1px solid var(--brd); border-radius:var(--r2); padding:24px 28px; max-height:400px; overflow-y:auto; white-space:pre-wrap; word-break:break-word; }
.ocr-viewer .page-break { border-top:2px dashed var(--brd); margin:16px 0; padding-top:14px; color:var(--mut); font-size:.72rem; font-family:'Inter',sans-serif; text-transform:uppercase; letter-spacing:.08em; }"""

css_new = """/* ── OCR VIEWER ── */
.ocr-viewer { font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 0.85rem; line-height: 1.6; color: #a5f3fc; background: rgba(10, 15, 25, 0.85); border: 1px solid var(--brd); border-left: 4px solid var(--blue); border-radius: var(--r2); padding: 24px 28px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; box-shadow: inset 0 0 20px rgba(0,0,0,0.6); }
.ocr-viewer .page-break { border-top: 2px dashed rgba(255,255,255,0.15); margin: 24px 0; padding-top: 12px; color: var(--gold); font-size: 0.72rem; font-family: 'Inter', sans-serif; text-transform: uppercase; letter-spacing: 0.1em; text-align: center; background: rgba(234, 179, 8, 0.05); border-radius: 4px; }
.ocr-viewer-line { display: block; margin-bottom: 4px; padding-left: 10px; border-left: 2px solid rgba(255,255,255,0.05); }"""

if "/* ── OCR VIEWER ── */" in content:
    # Replace the block
    start_idx = content.find("/* ── OCR VIEWER ── */")
    end_idx = content.find("/* ── DRAFT VIEWER ── */")
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + css_new + "\n" + content[end_idx:]

# 2. Update renderSelectedDoc logic for OCR
js_old = """  // Populate OCR rich viewer
  const _ocrV=document.getElementById("ocrRichView");
  if(_ocrV){
    const _ocrT=d.ocrText||""; 
    const _parts=_ocrT.split(/---\\s*P[\\u00c1A]GINA\\s+\\d+\\s*---/i);
    if(_parts.length>1){
      _ocrV.innerHTML=_parts.map((p,i)=>(i>0?`<div class="page-break">&mdash; P\\u00e1gina ${i+1} &mdash;</div>`:"")+"<span>"+esc(p.trim()).replace(/\\n/g,"<br>")+"</span>").join("");
    } else {
      _ocrV.innerHTML="<span>"+esc(_ocrT.trim()).replace(/\\n/g,"<br>")+"</span>";
    }
    if(!_ocrT.trim()) _ocrV.innerHTML="<span style='color:var(--mut)'>Sin texto OCR disponible para este documento.</span>";
  }"""

js_new = """  // Populate OCR rich viewer
  const _ocrV=document.getElementById("ocrRichView");
  if(_ocrV){
    const _ocrT=d.ocrText||""; 
    const _parts=_ocrT.split(/---\\s*P[\\u00c1A]GINA\\s+\\d+\\s*---/i);
    
    function formatOCRText(text) {
      if(!text.trim()) return "";
      // Escape HTML chars to prevent XSS but keep accents safe
      const safeText = esc(text.trim());
      // Split by newline and wrap in a styled div for better readability
      return safeText.split('\\n').map(line => `<span class="ocr-viewer-line">${line || '&nbsp;'}</span>`).join('');
    }

    if(_parts.length>1){
      _ocrV.innerHTML=_parts.map((p,i)=>(i>0?`<div class="page-break">&mdash; P\\u00e1gina ${i+1} &mdash;</div>`:"")+formatOCRText(p)).join("");
    } else {
      _ocrV.innerHTML=formatOCRText(_ocrT);
    }
    if(!_ocrT.trim()) _ocrV.innerHTML="<span style='color:var(--mut); font-family: Inter, sans-serif;'>Sin texto OCR disponible para este documento. Extrae el texto primero.</span>";
  }"""

if "// Populate OCR rich viewer" in content:
    # We can use text replacement
    import re
    # We will use regex to replace from "// Populate OCR rich viewer" to "  }\n}"
    pattern = re.compile(r'  // Populate OCR rich viewer.*?_ocrV\.innerHTML="<span style=\'color:var\(--mut\)\'>Sin texto OCR.*?}\n', re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub(js_new + "\n", content)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("OCR viewer logic updated successfully.")
