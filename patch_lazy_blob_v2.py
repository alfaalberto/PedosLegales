import os

html_path = r"d:\PEDOS LEGALES\App_DefensaIPN\DefensaIPN_ai_v7_1_auditada_corregida\public\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# The line to replace:
# $("sourcePreview").innerHTML=d.blob?`<b>Original guardado.</b> <span class="small">Tipo: ${esc(d.mimeType)}.</span><div id="blobPreview" style="margin-top:10px"></div>`+"<p class='tiny muted' style='margin-top:6px'>El archivo original está guardado localmente.</p>":"<p class='tiny muted'>No se guardó blob local.</p>"; if(d.blob) renderBlobPreview(d);

old_line = """$("sourcePreview").innerHTML=d.blob?`<b>Original guardado.</b> <span class="small">Tipo: ${esc(d.mimeType)}.</span><div id="blobPreview" style="margin-top:10px"></div>`+"<p class='tiny muted' style='margin-top:6px'>El archivo original está guardado localmente.</p>":"<p class='tiny muted'>No se guardó blob local.</p>"; if(d.blob) renderBlobPreview(d);"""

new_line = """$("sourcePreview").innerHTML=(d.blob || d.blobOmitted)?`<b>Original disponible.</b> <span class="small">Tipo: ${esc(d.mimeType)}.</span><div id="blobPreview" style="margin-top:10px"></div><p class='tiny muted' style='margin-top:6px'>Cargando visor original...</p>`:"<p class='tiny muted'>No hay archivo original para visualizar.</p>"; if(d.blob || d.blobOmitted) renderBlobPreview(d);"""

if old_line in content:
    content = content.replace(old_line, new_line)
    print("Fixed missing blob preview logic successfully.")
else:
    print("Could not find the exact old line. Attempting regex replacement...")
    import re
    # Try a more flexible regex
    pattern = re.compile(r'\$\("sourcePreview"\)\.innerHTML=d\.blob\?`<b>Original guardado.*?if\(d\.blob\) renderBlobPreview\(d\);')
    if pattern.search(content):
        content = pattern.sub(new_line, content)
        print("Fixed missing blob preview logic with regex.")
    else:
        print("Still could not find the line to replace.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
