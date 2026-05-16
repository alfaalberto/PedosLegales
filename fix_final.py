import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ─── 1. FIX THE MISSING </div> for .main-area ────────────────────────────────
# The structure should be:
#   </main>      ← closes <main>
#   </div>       ← closes .main-area
#   </div><!-- /main-app -->  ← closes .app-layout / #main-app
# Currently there are only 2 closing divs instead of 3.
old_tail = '</main>\n\n<script>'
new_tail = '</main>\n  </div><!-- /main-area -->\n</div><!-- /app-layout -->\n\n<script>'
content = content.replace(old_tail, new_tail, 1)

# ─── 2. FIX the final closing of #main-app ───────────────────────────────────
# Remove the old /main-app comment that is now redundant/misplaced
content = content.replace(
    '</script>\n</div><!-- /main-app -->\n</body>',
    '</script>\n</body>'
)

# ─── 3. FIX the `api` function ───────────────────────────────────────────────
# The old api function doesn't handle non-JSON responses (e.g., when server is
# returning HTML or nothing). Replace with robust version.
# Find and replace the api function
api_old_patterns = [
    # Original version
    'async function api(path,opts={}){const url=getServerUrl()+path;const res=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});const data=await res.json().catch(()=>({}));if(!res.ok||data.ok===false)throw new Error(data.error||"Error del servidor");return data}',
    # Our attempted fix from fix_ui.py
    'async function api(path,opts={}){const url=getServerUrl()+path;const res=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});const text=await res.text();let data;try{data=JSON.parse(text)}catch(e){throw new Error("La respuesta no es JSON v\u00e1lido (Revisa el servidor Express).");}if(!res.ok||!data.ok)throw new Error(data?.error||"Error del servidor");return data;}',
]

api_new = '''async function api(path,opts={}){
  const base=getServerUrl();
  const url=base+path;
  let res,text,data;
  try{res=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});}
  catch(e){throw new Error("No se pudo conectar al servidor Express ("+base+"). Verifica que esté corriendo: "+e.message);}
  try{text=await res.text();}catch(e){throw new Error("Error leyendo respuesta del servidor.");}
  try{data=JSON.parse(text);}catch(e){throw new Error("El servidor no respondió JSON válido. URL usada: "+url+". Respuesta: "+text.slice(0,200));}
  if(!res.ok||data.ok===false)throw new Error(data?.error||"Error del servidor (status "+res.status+")");
  return data;
}'''

replaced = False
for old in api_old_patterns:
    if old in content:
        content = content.replace(old, api_new, 1)
        replaced = True
        print(f"API function replaced (pattern {api_old_patterns.index(old)+1})")
        break

if not replaced:
    print("WARNING: api() function not found with known patterns, trying regex...")
    # fallback regex
    pat = re.compile(r'async function api\(path,opts=\{\}\)\{.*?return data\}', re.DOTALL)
    m = pat.search(content)
    if m:
        content = content[:m.start()] + api_new + content[m.end():]
        print("API function replaced via regex")
    else:
        print("ERROR: Could not find api() function!")

# ─── 4. FIX checkHealth ──────────────────────────────────────────────────────
# The healthBox might not be visible if the panel section structure changed.
# Make checkHealth also show/display modelBox
old_check = "async function checkHealth(){try{const d=await api(\"/api/health\");$(\"healthBox\").className=d.api_key_configured?\"box success\":\"box notice\";$(\"healthBox\").innerHTML=`<b>Servidor:</b> activo<br>API key: ${d.api_key_configured?\"configurada\":\"NO configurada\"}<br>Web search: ${d.allow_web_search?\"habilitado\":\"deshabilitado\"}<br>Razonamiento: ${esc(d.reasoning_effort)}<br>Policy: ${esc(d.policy_version)}`;}catch(e){$(\"healthBox\").className=\"box dangerbox\";$(\"healthBox\").textContent=e.message}}"

new_check = """async function checkHealth(){
  const box=$("healthBox");
  if(box){box.className="box notice";box.textContent="Verificando servidor...";}
  try{
    const d=await api("/api/health");
    if(box){
      box.className=d.api_key_configured?"box success":"box notice";
      box.innerHTML="<b>Servidor:</b> <span style='color:var(--success)'>activo ✓</span><br>"+
        "<b>API key:</b> "+(d.api_key_configured?"configurada ✓":"NO configurada ✗")+"<br>"+
        "<b>Web search:</b> "+(d.allow_web_search?"habilitado":"deshabilitado")+"<br>"+
        "<b>Razonamiento:</b> "+esc(d.reasoning_effort)+"<br>"+
        "<b>Policy:</b> "+esc(d.policy_version)+"<br>"+
        "<b>Max tokens:</b> "+d.max_output_tokens;
    }
    const dot=$("serverDot");
    if(dot){dot.className="sdot on";}
  }catch(e){
    if(box){box.className="box dangerbox";box.innerHTML="<b>Error:</b> "+esc(e.message);}
    const dot=$("serverDot");
    if(dot){dot.className="sdot off";}
  }
}"""

if old_check in content:
    content = content.replace(old_check, new_check)
    print("checkHealth replaced")
else:
    print("WARNING: checkHealth not found with exact pattern, trying regex...")
    pat = re.compile(r'async function checkHealth\(\)\{.*?\}\}', re.DOTALL)
    m = pat.search(content)
    if m:
        content = content[:m.start()] + new_check + content[m.end():]
        print("checkHealth replaced via regex")
    else:
        print("ERROR: checkHealth not found!")

# ─── 5. FIX resolveModel ─────────────────────────────────────────────────────
old_resolve = 'async function resolveModel(){try{const d=await api("/api/models/resolve");$("modelBox").className="box success";$("modelBox").innerHTML=`<b>Modelo:</b> <span class="tag green">${esc(d.selected)}</span><br><b>Razón:</b> ${esc(d.reason)}<br><b>Verificado:</b> ${esc(d.checked_at)}`;  }catch(e){$("modelBox").className="box dangerbox";$("modelBox").textContent=e.message}}'

new_resolve = """async function resolveModel(){
  const box=$("modelBox");
  if(box){box.style.display="";box.className="box notice";box.textContent="Resolviendo modelo...";}
  try{
    const d=await api("/api/models/resolve");
    if(box){
      box.className="box success";
      box.innerHTML="<b>Modelo seleccionado:</b> <span class='tag green'>"+esc(d.selected)+"</span><br>"+
        "<b>Razón:</b> "+esc(d.reason)+"<br>"+
        "<b>Verificado:</b> "+esc(d.checked_at)+"<br>"+
        "<b>Modo:</b> "+esc(d.model_policy_mode);
    }
  }catch(e){
    if(box){box.className="box dangerbox";box.innerHTML="<b>Error:</b> "+esc(e.message);}
  }
}"""

if old_resolve in content:
    content = content.replace(old_resolve, new_resolve)
    print("resolveModel replaced")
else:
    print("WARNING: resolveModel not found with exact pattern, trying regex...")
    pat = re.compile(r'async function resolveModel\(\)\{.*?\}\}', re.DOTALL)
    m = pat.search(content)
    if m:
        content = content[:m.start()] + new_resolve + content[m.end():]
        print("resolveModel replaced via regex")
    else:
        print("ERROR: resolveModel not found!")

# ─── 6. FIX runDoctor ────────────────────────────────────────────────────────
old_doctor = """async function runDoctor(){
 try{
  const d=await api("/api/doctor");
  $("doctorBox").innerHTML=d.checks.map(c=>`${c.ok?"✅":"⚠️"} <b>${esc(c.name)}</b>: ${esc(c.detail)}`).join("<br>")+"<br><br>Modo vendor offline: "+d.offline_vendor_mode;
 }catch(e){$("doctorBox").innerHTML="Error doctor: "+esc(e.message)}
}"""

new_doctor = """async function runDoctor(){
  const box=$("doctorBox");
  if(box){box.className="box notice";box.textContent="Ejecutando diagnóstico v7...";}
  try{
    const d=await api("/api/doctor");
    if(box){
      box.className="box info";
      const rows=d.checks.map(c=>{
        const ok=c.ok;
        return '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05)">'+
          '<span style="color:'+(ok?'var(--success)':'var(--danger)');window.__dummy=0;return '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05)">'+
          '<span style="font-size:1.1rem">'+(ok?"✅":"⚠️")+'</span>'+
          '<span><b>'+esc(c.name)+'</b>: '+esc(c.detail)+'</span></div>';
      });
      box.innerHTML=rows.join("")+'<div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.1)"><b>Vendor offline:</b> '+String(d.offline_vendor_mode)+'</div>';
    }
  }catch(e){
    if(box){box.className="box dangerbox";box.innerHTML="<b>Error diagnóstico:</b> "+esc(e.message);}
  }
}"""

# Simpler version without the bug:
new_doctor = """async function runDoctor(){
  const box=$("doctorBox");
  if(box){box.className="box notice";box.textContent="Ejecutando diagnóstico v7...";}
  try{
    const d=await api("/api/doctor");
    if(box){
      box.className="box info";
      const rows=d.checks.map(c=>'<div style="padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05)">'+(c.ok?"✅":"⚠️")+" <b>"+esc(c.name)+"</b>: "+esc(c.detail)+"</div>");
      box.innerHTML=rows.join("")+"<div style='margin-top:10px'><b>Vendor offline:</b> "+String(d.offline_vendor_mode)+"</div>";
    }
  }catch(e){
    if(box){box.className="box dangerbox";box.innerHTML="<b>Error diagnóstico:</b> "+esc(e.message);}
  }
}"""

pat = re.compile(r'async function runDoctor\(\)\{.*?\}\}', re.DOTALL)
m = pat.search(content)
if m:
    content = content[:m.start()] + new_doctor + content[m.end():]
    print("runDoctor replaced via regex")
else:
    print("ERROR: runDoctor not found!")

# ─── 7. ENSURE modelBox is always visible (show:none removed) ────────────────
content = content.replace(
    '<div id="modelBox" class="box info" style="display:none">Modelo sin resolver.</div>',
    '<div id="modelBox" class="box info">Modelo: pendiente de verificación.</div>'
)

# ─── 8. FIX renderPanel to update acsName ────────────────────────────────────
# After renderPanel runs, update the active case name in sidebar
if 'if($("acsName")) $("acsName").textContent' not in content:
    # The mCase line - find and replace
    old_mcase = '$("mCases").textContent=cases.length;$("mDocs").textContent=docs.length;'
    new_mcase = 'if($("acsName"))$("acsName").textContent=c?c.name:"Sin caso activo";$("mCases").textContent=cases.length;$("mDocs").textContent=docs.length;'
    if old_mcase in content:
        content = content.replace(old_mcase, new_mcase)
        print("acsName update added to renderPanel")

# ─── 9. Verify div balance ───────────────────────────────────────────────────
opens = content.count('<div')
closes = content.count('</div>')
print(f"\nDiv balance: <div={opens}, </div>={closes}, diff={opens-closes}")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! File written.")
