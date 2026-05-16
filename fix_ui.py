import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace the CSS block
new_css = """<style>
/* ── Variables ─────────────────────────────────────────────────── */
:root {
  --bg: #09090b; --panel: #18181b; --panel-border: #27272a;
  --sidebar: #000000; --sidebar-border: #27272a;
  --ink: #f4f4f5; --muted: #a1a1aa;
  --accent: #d4af37; --accent-hover: #fcd34d;
  --primary: #3b82f6; --primary-hover: #60a5fa;
  --danger: #ef4444; --success: #10b981; --warning: #f59e0b;
  --radius: 12px; --radius-sm: 8px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
  --glass: rgba(24, 24, 27, 0.7);
}
* { box-sizing: border-box; }
body {
  margin: 0; color: var(--ink);
  font-family: "Inter", system-ui, sans-serif;
  font-size: 14px; line-height: 1.6;
  background: var(--bg);
  height: 100vh; overflow: hidden;
  display: flex;
}
/* ── App Layout ─────────────────────────────────────────────────── */
.app-layout {
  display: flex;
  width: 100%; height: 100%;
}
.sidebar {
  width: 260px; background: var(--sidebar);
  border-right: 1px solid var(--sidebar-border);
  display: flex; flex-direction: column;
  padding: 20px 0; z-index: 50;
}
.main-area {
  flex: 1; display: flex; flex-direction: column;
  background: var(--bg);
  position: relative;
  overflow-x: hidden;
}
/* ── Sidebar ────────────────────────────────────────────────────── */
.hdr-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 0 20px 24px;
}
.brand-badge {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), #b48600);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; color: #000;
  box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
}
.brand-name { font-family: "Lora", serif; font-size: 1.1rem; font-weight: 700; margin: 0; color: #fff; }
.brand-sub { font-size: 0.7rem; color: var(--muted); margin: 0; }
.active-case-selector {
  margin: 0 20px 20px; padding: 12px;
  background: var(--panel); border: 1px solid var(--panel-border);
  border-radius: var(--radius-sm);
  cursor: pointer; transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}
.active-case-selector:hover { border-color: var(--accent); }
.acs-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin-bottom: 4px; font-weight: 700; }
.acs-name { font-size: 0.9rem; font-weight: 600; color: var(--accent); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav-group-title {
  font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--muted); font-weight: 700; padding: 16px 24px 8px;
}
nav {
  display: flex; flex-direction: column; flex: 1;
  overflow-y: auto; scrollbar-width: none;
}
nav::-webkit-scrollbar { display: none; }
.tab {
  cursor: pointer; background: transparent; border: none;
  color: #a1a1aa; padding: 10px 24px;
  font-family: "Inter", sans-serif; font-weight: 500; font-size: 0.85rem;
  text-align: left; transition: all 0.2s;
  display: flex; align-items: center; gap: 10px;
}
.tab:hover { color: #fff; background: rgba(255,255,255,0.03); }
.tab.active {
  color: #fff; font-weight: 600;
  background: linear-gradient(90deg, rgba(212, 175, 55, 0.1), transparent);
  border-left: 3px solid var(--accent);
}
/* ── Topbar ─────────────────────────────────────────────────────── */
.topbar {
  display: flex; align-items: center; justify-content: flex-end;
  padding: 16px 32px;
  background: var(--bg);
  border-bottom: 1px solid var(--panel-border);
  position: sticky; top: 0; z-index: 40;
}
.hdr-actions { display: flex; align-items: center; gap: 12px; }
.user-chip {
  display: flex; align-items: center; gap: 8px;
  background: var(--panel); border: 1px solid var(--panel-border);
  border-radius: 999px; padding: 4px 14px 4px 6px;
}
.user-avatar {
  width: 24px; height: 24px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #b48600);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 800; color: #000;
}
.hdr-btn {
  border: 1px solid var(--panel-border); background: var(--panel); color: var(--ink);
  border-radius: 999px; padding: 6px 16px; font-size: 0.75rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.hdr-btn:hover { border-color: var(--accent); color: var(--accent); }
.sdot { width: 8px; height: 8px; border-radius: 50%; background: var(--muted); }
.sdot.on { background: var(--success); box-shadow: 0 0 8px var(--success); }
.sdot.off { background: var(--danger); box-shadow: 0 0 8px var(--danger); }
/* ── Main Content ───────────────────────────────────────────────── */
main { flex: 1; overflow-y: auto; padding: 32px; }
section { display: none; animation: fadeIn 0.3s ease; }
section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
.grid { display: grid; gap: 20px; }
.two { grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); }
.three { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.cards { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
/* ── Cards ──────────────────────────────────────────────────────── */
.card {
  background: var(--panel); border: 1px solid var(--panel-border);
  border-radius: var(--radius); box-shadow: var(--shadow-sm);
  padding: 24px; transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover { box-shadow: var(--shadow); }
.card-gold { border-top: 3px solid var(--accent); }
.mcard {
  background: var(--panel); border: 1px solid var(--panel-border);
  border-radius: var(--radius); padding: 20px; position: relative; overflow: hidden;
}
.mcard::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--accent), #b48600); opacity: 0; transition: opacity 0.3s;
}
.mcard:hover::after { opacity: 1; }
.mcard-lbl { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
.mcard-val { font-size: 2.2rem; font-weight: 800; margin: 8px 0 4px; color: #fff; }
.mcard-sub { font-size: 0.75rem; color: var(--muted); }
/* ── Case List Items ────────────────────────────────────────────── */
.casepill {
  display: block; text-align: left; width: 100%; margin: 8px 0;
  padding: 16px; background: var(--panel); border: 1px solid var(--panel-border);
  border-radius: var(--radius-sm); cursor: pointer; transition: all 0.2s;
}
.casepill:hover { border-color: var(--accent); background: rgba(212, 175, 55, 0.05); transform: translateY(-1px); }
.casepill.ok { border-color: var(--accent); background: rgba(212, 175, 55, 0.1); box-shadow: 0 0 10px rgba(212, 175, 55, 0.1); }
/* ── Typography ─────────────────────────────────────────────────── */
h2 { font-family: "Lora", serif; font-size: 1.25rem; font-weight: 600; margin: 0 0 16px; color: #fff; }
h3 { font-size: 0.8rem; font-weight: 700; margin: 0 0 8px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
.small { font-size: 0.85rem; } .tiny { font-size: 0.75rem; } .muted { color: var(--muted); }
.mono { font-family: "JetBrains Mono", ui-monospace, monospace; }
/* ── Forms ──────────────────────────────────────────────────────── */
label { display: block; margin: 16px 0 6px; color: #d4d4d8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
input, select, textarea {
  width: 100%; border: 1px solid var(--panel-border); background: #000;
  color: #fff; border-radius: var(--radius-sm); padding: 10px 14px;
  font: inherit; font-size: 0.9rem; outline: none; transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus, select:focus, textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }
textarea { min-height: 120px; resize: vertical; line-height: 1.6; }
/* ── Buttons ────────────────────────────────────────────────────── */
button, .btn {
  border: 0; border-radius: var(--radius-sm); padding: 10px 20px;
  font-family: "Inter", sans-serif; font-size: 0.85rem; font-weight: 600;
  cursor: pointer; background: var(--primary); color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  gap: 8px; transition: all 0.2s;
}
button:hover, .btn:hover { background: var(--primary-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
button:active { transform: translateY(0); }
button:disabled { opacity: 0.5; cursor: not-allowed; }
button.secondary, .btn.secondary { background: var(--panel); color: var(--ink); border: 1px solid var(--panel-border); box-shadow: none; }
button.secondary:hover { border-color: var(--muted); background: #27272a; }
button.danger { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
button.danger:hover { background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.5); }
button.ok { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
button.warn { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
/* ── Toolbar & Rows ─────────────────────────────────────────────── */
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin: 16px 0; }
.row { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end; }
.row > * { flex: 1; min-width: 200px; }
/* ── Alerts ─────────────────────────────────────────────────────── */
.box { border: 1px solid var(--panel-border); border-radius: var(--radius-sm); padding: 14px 16px; background: rgba(255,255,255,0.02); margin: 12px 0; font-size: 0.85rem; }
.info { border-left: 3px solid var(--primary); background: rgba(59, 130, 246, 0.05); }
.success { border-left: 3px solid var(--success); background: rgba(16, 185, 129, 0.05); }
.notice { border-left: 3px solid var(--warning); background: rgba(245, 158, 11, 0.05); }
.dangerbox { border-left: 3px solid var(--danger); background: rgba(239, 68, 68, 0.05); }
/* ── Tags ───────────────────────────────────────────────────────── */
.tag { display: inline-block; border-radius: 6px; padding: 3px 8px; margin: 2px; font-size: 0.7rem; font-weight: 600; background: rgba(255,255,255,0.1); color: #fff; }
.tag.violet { background: rgba(139, 92, 246, 0.15); color: #c4b5fd; }
.tag.yellow { background: rgba(245, 158, 11, 0.15); color: #fcd34d; }
.tag.green { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; }
.tag.red { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }
/* ── Paper ──────────────────────────────────────────────────────── */
.paper { background: #fff; color: #111827; border-radius: var(--radius-sm); padding: 32px; white-space: pre-wrap; line-height: 1.8; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); min-height: 400px; overflow: auto; font-family: "Lora", serif; font-size: 0.95rem; }
/* ── Table ──────────────────────────────────────────────────────── */
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { border-bottom: 1px solid var(--panel-border); padding: 12px; text-align: left; vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
tr:hover td { background: rgba(255,255,255,0.02); }
/* ── Dropzone ───────────────────────────────────────────────────── */
progress { width: 100%; height: 8px; border-radius: 999px; appearance: none; }
progress::-webkit-progress-bar { background: var(--panel-border); border-radius: 999px; }
progress::-webkit-progress-value { background: linear-gradient(90deg, var(--primary), #60a5fa); border-radius: 999px; }
.drop { border: 2px dashed var(--panel-border); border-radius: var(--radius); padding: 40px 20px; text-align: center; background: rgba(255,255,255,0.01); transition: all 0.2s; }
.drop.drag { background: rgba(59, 130, 246, 0.05); border-color: var(--primary); }
/* ── Chat ───────────────────────────────────────────────────────── */
.chatbox { height: 500px; overflow-y: auto; border: 1px solid var(--panel-border); border-radius: var(--radius-sm); padding: 16px; background: #000; }
.msg { max-width: 85%; padding: 14px 18px; border-radius: var(--radius-sm); margin: 12px 0; white-space: pre-wrap; font-size: 0.9rem; box-shadow: var(--shadow-sm); }
.msg.user { margin-left: auto; background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
.msg.assistant { margin-right: auto; background: var(--panel); border: 1px solid var(--panel-border); border-bottom-left-radius: 4px; }
.msgmeta { font-size: 0.7rem; color: rgba(255,255,255,0.6); margin-bottom: 6px; }
.srcitem { cursor: pointer; transition: background 0.2s; }
.srcitem:hover { background: rgba(255,255,255,0.05); }
/* ── Misc ───────────────────────────────────────────────────────── */
.step { display: flex; gap: 16px; align-items: flex-start; border: 1px solid var(--panel-border); border-radius: var(--radius-sm); padding: 16px; background: rgba(255,255,255,0.01); margin: 12px 0; transition: border-color 0.2s; }
.step:hover { border-color: var(--muted); }
.stepnum { flex: 0 0 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; background: var(--panel); border: 2px solid var(--panel-border); color: var(--muted); }
.step.done .stepnum { background: var(--success); border-color: var(--success); color: #fff; }
.step.warn .stepnum { background: var(--warning); border-color: var(--warning); color: #fff; }
.step.bad .stepnum { background: var(--danger); border-color: var(--danger); color: #fff; }
.healthbar { height: 8px; border-radius: 999px; background: var(--panel-border); overflow: hidden; margin: 12px 0; }
.healthbar span { display: block; height: 100%; background: linear-gradient(90deg, var(--danger), var(--warning) 50%, var(--success)); transition: width 0.5s ease; }
.docgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin: 16px 0; }
.badgeblock { border: 1px solid var(--panel-border); border-radius: var(--radius-sm); padding: 12px; background: rgba(255,255,255,0.02); text-align: center; }
.viewerFrame { width: 100%; min-height: 600px; border: none; border-radius: var(--radius-sm); background: #fff; }
.imgPreview { max-width: 100%; border-radius: var(--radius-sm); }
</style>"""

start_css = html.find('<style>')
end_css = html.find('</style>') + 8
html = html[:start_css] + new_css + html[end_css:]

# 3. Replace the layout structure
old_layout_start = html.find('<div id="main-app"')
old_layout_end = html.find('<section id="panel"', old_layout_start)

new_layout = """<div id="main-app" style="display:none" class="app-layout">
  <aside class="sidebar">
    <div class="hdr-brand">
      <div class="brand-badge">⚖</div>
      <div>
        <p class="brand-name">DefensaIPN.ai</p>
        <p class="brand-sub">Sistema Jurídico Inteligente</p>
      </div>
    </div>
    <div class="active-case-selector" onclick="goTab('cases')">
      <div class="acs-label">Expediente Activo</div>
      <div class="acs-name" id="acsName">Ningún caso seleccionado</div>
    </div>
    <nav id="tabs"></nav>
  </aside>
  <div class="main-area">
    <header class="topbar">
      <div class="hdr-actions">
        <div class="user-chip">
          <div class="user-avatar" id="userInitial">U</div>
          <span id="userBadge" class="tiny"></span>
        </div>
        <button class="hdr-btn hdr-server" onclick="configServerUrl()" title="Configura la URL del servidor Express">
          <span class="sdot" id="serverDot"></span>
          Servidor: <span id="serverUrlBadge">local</span>
        </button>
        <button class="hdr-btn" onclick="doLogout()">Cerrar sesión</button>
      </div>
    </header>
    <main>
"""

html = html[:old_layout_start] + new_layout + html[old_layout_end:]

# 4. Fix JS `api` function
api_func_old = """async function api(path,opts={}){const url=getServerUrl()+path;const res=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});const data=await res.json().catch(()=>({}));if(!res.ok||data.ok===false)throw new Error(data.error||"Error del servidor");return data}"""
api_func_new = """async function api(path,opts={}){const url=getServerUrl()+path;const res=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});const text=await res.text();let data;try{data=JSON.parse(text)}catch(e){throw new Error("La respuesta no es JSON válido (Revisa el servidor Express).");}if(!res.ok||!data.ok)throw new Error(data?.error||"Error del servidor");return data;}"""

html = html.replace(api_func_old, api_func_new)

# 5. Fix JS `renderPanel` and update sidebar Active Case Name
# Find the renderPanel line
if '$("mCase").textContent=c?c.name.slice(0,16):"—";' in html:
    html = html.replace('$("mCase").textContent=c?c.name.slice(0,16):"—";', 'if($("acsName")) $("acsName").textContent = c ? c.name : "Ningún caso seleccionado";')

# Also remove mCase entirely from HTML so it doesn't break if not found
html = html.replace('<span id="mCase" style="display:none"></span>', '')

# 6. Restrict tabs to only "Casos" if no case is selected
# Change `initTabs` function slightly
init_tabs_old = """tabs.forEach(([id,label])=>{const b=document.createElement("button");b.className="tab"+(id==="panel"?" active":"");b.textContent=label;b.onclick=()=>{document.querySelectorAll("section").forEach(s=>s.classList.remove("active"));document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));$(id).classList.add("active");b.classList.add("active");renderAll()};nav.appendChild(b)})"""
init_tabs_new = """tabs.forEach(([id,label])=>{const b=document.createElement("button");b.className="tab"+(id==="panel"?" active":"");b.innerHTML=`<span style="display:inline-block;width:16px">${id==='cases'?'📁':id==='chat'?'💬':'•'}</span> ${label}`;b.id="tabbtn_"+id;b.onclick=()=>{if(!state.activeCaseId && id!=="cases"){alert("Selecciona un caso primero.");goTab('cases');return;}document.querySelectorAll("section").forEach(s=>s.classList.remove("active"));document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));$(id).classList.add("active");b.classList.add("active");renderAll()};nav.appendChild(b)})"""

html = html.replace(init_tabs_old, init_tabs_new)

# 7. In `goTab`, also restrict
go_tab_old = """function goTab(id){
 document.querySelectorAll("section").forEach(s=>s.classList.remove("active"));"""
go_tab_new = """function goTab(id){
 if(!state.activeCaseId && id !== 'cases') { id = 'cases'; }
 document.querySelectorAll("section").forEach(s=>s.classList.remove("active"));"""

html = html.replace(go_tab_old, go_tab_new)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done replacing.")
