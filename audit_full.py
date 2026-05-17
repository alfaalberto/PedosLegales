import re

with open('public/index.html','r',encoding='utf-8') as f:
    c = f.read()

# Check key element IDs exist
ids_needed = ['docTable','dropZone','fileInput','folderInput','ocrProgress','ocrBar','queueList',
              'chatBox','chatInput','draftList','draftEditor','caseGrid','acsName','serverDot',
              'userInitial','userBadge','loginEmail','loginPassword','loginBtn','healthBox',
              'modelBox','doctorBox','exportTitle','exportContent','exportStatus','cryptoStatus',
              'masterPassword','auditTable','selectedText','selectedFolio','selectedAuthority',
              'selectedDocDate','selectedRole','selectedStatus','selectedNotes','docVisorCard',
              'ragFilter','ragTopK','chunkChars','modelOverride','allowWeb','chatMode']

print('=== ELEMENT IDS ===')
missing_ids = []
for id_ in ids_needed:
    found = f'id="{id_}"' in c
    if not found:
        missing_ids.append(id_)
    print(f'  {"OK" if found else "MISS"}: #{id_}')

print(f'\nMissing: {len(missing_ids)} => {missing_ids}')

# Check key functions
fns_needed = ['renderDocuments','handleFiles','setupDrop','processQueue','sendChat',
              'selectCase','createCase','renderCaseGrid','showPage','boot','initFirebase',
              'doLogin','doLogout','checkHealth','resolveModel','runDoctor','renderAll',
              'renderChat','renderDrafts','renderQueue','activeCase','all','get','put',
              'messagesOfActive','draftsOfActive','saveLastAssistantAsDraft','saveDraftVersion',
              'deleteDraft','selectDraft','downloadDraftTxt','saveSelectedMeta','saveSelectedText',
              'markReviewed','renderSelectedDoc','renderStorage','renderAudit','runSelfAudit',
              'exportAudit','clearAudit','fullBackup','importFullBackup','exportEncryptedBackup',
              'importEncryptedBackup','exportServer','ensureDefaultCase','loadState','saveState',
              'quickOpinion','updateSidebarCase','openNewCaseModal','createCaseFromModal']

print('\n=== FUNCTIONS ===')
missing_fns = []
for fn in fns_needed:
    found = f'function {fn}' in c or f'async function {fn}' in c
    if not found:
        missing_fns.append(fn)
    print(f'  {"OK" if found else "MISS"}: {fn}()')

print(f'\nMissing: {len(missing_fns)} => {missing_fns}')

# Check renderDocuments body
print('\n=== renderDocuments (first 600 chars) ===')
idx = c.find('async function renderDocuments')
if idx == -1: idx = c.find('function renderDocuments')
if idx != -1:
    print(c[idx:idx+600].encode('ascii','replace').decode())
else:
    print('NOT FOUND')

# Check handleFiles body
print('\n=== handleFiles (first 400 chars) ===')
idx = c.find('function handleFiles')
if idx != -1:
    print(c[idx:idx+400].encode('ascii','replace').decode())
else:
    print('NOT FOUND')

# Check setupDrop
print('\n=== setupDrop (first 600 chars) ===')
idx = c.find('function setupDrop')
if idx != -1:
    print(c[idx:idx+600].encode('ascii','replace').decode())
else:
    print('NOT FOUND')

# Check if _origRenderDocuments references
print('\n=== _orig* references ===')
for ref in ['_origRenderDocuments','_origHandleFiles','_origRenderDrafts','_origRenderChat','_origSelectDoc']:
    print(f'  {ref}: {"FOUND" if ref in c else "NOT FOUND"}')
