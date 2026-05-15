import express from "express";
import cors from "cors";
import helmet from "helmet";
import dotenv from "dotenv";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

// DefensaIPN.ai v7.1 — servidor local robustecido
// - No expone API key al navegador
// - Selecciona modelo dinámicamente
// - Valida/trocea paquetes RAG
// - Evita aceptar paquetes sin caso seleccionado
// - Mantiene web search desactivado salvo configuración explícita

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = Number(process.env.PORT || 8787);
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const MODEL_POLICY_MODE = process.env.MODEL_POLICY_MODE || "auto";
const FIXED_MODEL = process.env.OPENAI_MODEL || "gpt-5.5";
const REASONING_EFFORT = process.env.OPENAI_REASONING_EFFORT || "high";
const VERBOSITY = process.env.OPENAI_VERBOSITY || "medium";
const MAX_OUTPUT_TOKENS = Number(process.env.OPENAI_MAX_OUTPUT_TOKENS || 6000);
const ALLOW_WEB_SEARCH = String(process.env.ALLOW_WEB_SEARCH || "false").toLowerCase() === "true";
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
const FB_API_KEY = process.env.FIREBASE_API_KEY || "";
const FB_AUTH_DOMAIN = process.env.FIREBASE_AUTH_DOMAIN || "";
const FB_PROJECT_ID = process.env.FIREBASE_PROJECT_ID || "";
const FB_APP_ID = process.env.FIREBASE_APP_ID || "";
const OFFLINE_VENDOR_MODE = String(process.env.OFFLINE_VENDOR_MODE || "true").toLowerCase() === "true";
const MAX_PACKET_CHARS = Number(process.env.MAX_PACKET_CHARS || 220000);
const MAX_CHUNKS_PER_REQUEST = Number(process.env.MAX_CHUNKS_PER_REQUEST || 30);
const MAX_CHUNK_CHARS = Number(process.env.MAX_CHUNK_CHARS || 5000);
const MAX_EXPORT_CHARS = Number(process.env.MAX_EXPORT_CHARS || 500000);
const MODEL_CACHE_TTL_MS = 10 * 60 * 1000;

let modelCache = { at: 0, models: [] };
const requestTimes = new Map();

app.use(helmet({ contentSecurityPolicy: false, crossOriginEmbedderPolicy: false }));
app.use(cors({
  origin: [/^http:\/\/localhost:\d+$/, /^http:\/\/127\.0\.0\.1:\d+$/, ...ALLOWED_ORIGINS],
  credentials: false
}));
app.use(express.json({ limit: "30mb" }));
app.use(express.static(path.join(__dirname, "public")));

// Rate limit local suave: suficiente para evitar loops accidentales.
app.use((req, res, next) => {
  const key = req.ip || "local";
  const now = Date.now();
  const arr = (requestTimes.get(key) || []).filter(t => now - t < 60_000);
  arr.push(now);
  requestTimes.set(key, arr);
  if (arr.length > 90) return res.status(429).json({ ok: false, error: "Demasiadas solicitudes locales en 1 minuto." });
  next();
});

async function readText(relPath) { return fs.readFile(path.join(__dirname, relPath), "utf8"); }
async function readJson(relPath) { return JSON.parse(await readText(relPath)); }

async function openaiFetch(url, options = {}) {
  if (!OPENAI_API_KEY || OPENAI_API_KEY.includes("REEMPLAZA")) {
    const err = new Error("Falta OPENAI_API_KEY en .env");
    err.status = 500;
    throw err;
  }
  const res = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!res.ok) {
    const err = new Error(data?.error?.message || `OpenAI error ${res.status}`);
    err.status = res.status;
    err.details = data;
    throw err;
  }
  return data;
}

function parseGptVersion(modelId) {
  const m = String(modelId).match(/^gpt-(\d+)(?:\.(\d+))?(?:[-_]?([a-z0-9]+))?/i);
  if (!m) return null;
  const major = Number(m[1]);
  const minor = m[2] ? Number(m[2]) : 0;
  const suffix = (m[3] || "").toLowerCase();
  const proBonus = suffix.includes("pro") ? 0.25 : 0;
  return { major, minor, suffix, score: major * 100 + minor + proBonus };
}
function chooseModel(availableIds, policy) {
  if (MODEL_POLICY_MODE === "fixed") {
    return { selected: FIXED_MODEL, reason: "MODEL_POLICY_MODE=fixed", available: availableIds.includes(FIXED_MODEL) };
  }
  for (const p of policy?.model_selection?.priority_list || []) {
    if (availableIds.includes(p)) return { selected: p, reason: `Primer modelo disponible en priority_list: ${p}`, available: true };
  }
  const future = availableIds
    .map(id => ({ id, v: parseGptVersion(id) }))
    .filter(x => x.v && !/mini|nano/i.test(x.id))
    .sort((a, b) => b.v.score - a.v.score);
  if (future.length) return { selected: future[0].id, reason: "Modelo GPT de mayor versión detectado automáticamente", available: true };
  return { selected: FIXED_MODEL, reason: "Fallback por no encontrar modelo prioritario", available: availableIds.includes(FIXED_MODEL) };
}
async function listModels() {
  const now = Date.now();
  if (modelCache.models.length && now - modelCache.at < MODEL_CACHE_TTL_MS) return modelCache.models;
  const data = await openaiFetch("https://api.openai.com/v1/models", { method: "GET" });
  modelCache = { at: now, models: (data.data || []).map(m => m.id).sort() };
  return modelCache.models;
}
async function resolveModel() {
  const policy = await readJson("ai_policy.json");
  if (MODEL_POLICY_MODE === "fixed") return { selected: FIXED_MODEL, reason: "Modo fijo por configuración", available: null, policy };
  const models = await listModels();
  return { ...chooseModel(models, policy), models, policy };
}

function modeDirective(mode = "") {
  const m = String(mode || "").toLowerCase();
  if (/brutal|honesta|opini[oó]n|impacto|beneficia|perjudica|afecta|deber[ií]a hacer|qu[eé] crees|huele mal/.test(m)) {
    return `
MODO ESPECIAL: OPINIÓN ESTRATÉGICA BRUTALMENTE HONESTA.
Debes dar una lectura franca y crítica del documento/caso, separando:
- HECHO SOPORTADO,
- INFERENCIA RAZONABLE,
- HIPÓTESIS INTERNA,
- RIESGO NO PROBADO,
- OPINIÓN ESTRATÉGICA.

Incluye:
1. Opinión brutalmente honesta.
2. Cómo beneficia al denunciado.
3. Cómo perjudica al denunciado.
4. Riesgos ocultos o efectos secundarios.
5. Relación con el caso activo.
6. Qué haría yo en su lugar.
7. Qué NO haría.
8. Nivel de certeza.
9. Citas internas.

Sé directo, pero no afirmes intenciones de terceros sin soporte.`;
  }
  if (/pre-flight|ruido/.test(m)) {
    return `
MODO ESPECIAL: PRE-FLIGHT DE BAJO RUIDO.
Evalúa si enviar el texto puede generar reacción adversa, escalamiento innecesario o decisiones apresuradas.`;
  }
  if (/comparaci[oó]n/.test(m)) {
    return `
MODO ESPECIAL: COMPARACIÓN DOCUMENTAL.
Busca contradicciones, fechas incompatibles, folios, cambios de narrativa, omisiones y variación de litis.`;
  }
  if (/organizaci[oó]n|gobierno documental|clasifica|clasificaci[oó]n|índice|indice|car[aá]tula|expediente|pendiente documental/.test(m)) {
    return `
MODO ESPECIAL: GOBIERNO DOCUMENTAL.
Prioriza orden, clasificación, metadatos, trazabilidad, cotejo OCR, acciones pendientes, vencimientos e índice del caso.
No permitas que la opinión estratégica avance si faltan metadatos críticos.`;
  }
  return "";
}

function extractOutputText(response) {
  if (response.output_text) return response.output_text;
  const chunks = [];
  for (const item of response.output || []) {
    for (const c of item.content || []) {
      if (c.type === "output_text" && c.text) chunks.push(c.text);
      if (c.type === "text" && c.text) chunks.push(c.text);
    }
  }
  return chunks.join("\n").trim();
}
function validateModelOverride(name) {
  if (!name) return "";
  if (!/^gpt-[a-zA-Z0-9._-]+$/.test(name)) {
    const err = new Error("Modelo manual inválido. Usa un identificador tipo gpt-5.5.");
    err.status = 400;
    throw err;
  }
  return name;
}
function trimText(x, max) {
  const s = String(x || "");
  return s.length > max ? s.slice(0, max) + "\n...[TRUNCADO]" : s;
}
function sanitizePacket(packet = {}) {
  if (!packet.selectedCase?.id) {
    const err = new Error("El paquete debe incluir selectedCase.id para evitar mezcla de casos.");
    err.status = 400;
    throw err;
  }
  const chunks = (packet.retrievedChunks || []).slice(0, MAX_CHUNKS_PER_REQUEST).map(c => ({
    id: c.id,
    docId: c.docId,
    caseId: c.caseId,
    fileName: c.fileName,
    folderPath: c.folderPath,
    folio: c.folio,
    authority: c.authority,
    docDate: c.docDate,
    page: c.page,
    chunk: c.chunk,
    reviewed: Boolean(c.reviewed),
    ocrStatus: c.ocrStatus,
    score: c.score,
    sha256: c.sha256,
    notes: trimText(c.notes, 1000),
    docRole: c.docRole,
    stage: c.stage,
    docStatus: c.docStatus,
    priority: c.priority,
    confidentiality: c.confidentiality,
    actionNeeded: trimText(c.actionNeeded, 1000),
    dueDate: c.dueDate,
    tags: c.tags,
    text: trimText(c.text, MAX_CHUNK_CHARS)
  }));
  const documents = (packet.documents || []).map(d => ({
    id: d.id,
    caseId: d.caseId,
    fileName: d.fileName,
    folderPath: d.folderPath,
    folio: d.folio,
    authority: d.authority,
    docDate: d.docDate,
    ocrStatus: d.ocrStatus,
    reviewed: Boolean(d.reviewed),
    sha256: d.sha256,
    notes: trimText(d.notes, 1000),
    pageRange: d.pageRange,
    sourceKind: d.sourceKind,
    docRole: d.docRole,
    stage: d.stage,
    docStatus: d.docStatus,
    priority: d.priority,
    confidentiality: d.confidentiality,
    actionNeeded: trimText(d.actionNeeded, 1000),
    dueDate: d.dueDate,
    tags: d.tags
  }));
  const clean = {
    selectedCase: packet.selectedCase,
    documents,
    retrievedChunks: chunks,
    norms: packet.norms || [],
    ragSettings: packet.ragSettings || {},
    packetWarnings: packet.packetWarnings || []
  };
  const text = JSON.stringify(clean, null, 2);
  if (text.length > MAX_PACKET_CHARS) {
    const err = new Error(`Paquete RAG demasiado grande (${text.length} caracteres). Reduce fragmentos o caracteres por fragmento.`);
    err.status = 413;
    throw err;
  }
  return clean;
}
async function createResponse({ task, userInstruction, packet, conversation, selectedModel, allowWebSearch }) {
  const systemPrompt = await readText("prompts/system_defensaipn.txt");
  const cleanPacket = sanitizePacket(packet);
  const evidence = JSON.stringify(cleanPacket, null, 2);
  const history = (conversation || []).slice(-18).map(m => `${m.role.toUpperCase()} (${m.createdAt || ""}):\n${trimText(m.content, 9000)}`).join("\n\n---\n\n");

  const input = [
    { role: "system", content: [{ type: "input_text", text: systemPrompt }] },
    { role: "user", content: [{ type: "input_text", text:
`TAREA:
${task}

INSTRUCCIÓN ACTUAL:
${userInstruction || ""}

HISTORIAL RECIENTE DEL CHAT DEL CASO:
${history || "[Sin historial previo]"}

PAQUETE RAG DEL CASO SELECCIONADO:
${evidence}

REGLAS DE SALIDA:
- Cita fragmentos internos como [src:...].
- Si no hay fragmentos relevantes, di que no hay soporte documental suficiente.
- Si usas información de normas públicas por web, sepárala de expediente interno.
- No uses información de otros casos.
- Protege al denunciado y minimiza ruido institucional.` }] }
  ];

  const payload = {
    model: selectedModel,
    input,
    reasoning: { effort: REASONING_EFFORT },
    text: { verbosity: VERBOSITY },
    max_output_tokens: MAX_OUTPUT_TOKENS,
    store: false
  };
  if (allowWebSearch && ALLOW_WEB_SEARCH) payload.tools = [{ type: "web_search_preview" }];

  const response = await openaiFetch("https://api.openai.com/v1/responses", { method: "POST", body: JSON.stringify(payload) });
  return {
    model_requested: selectedModel,
    model_returned: response.model || selectedModel,
    response_id: response.id,
    created_at: new Date().toISOString(),
    reasoning_effort: REASONING_EFFORT,
    verbosity: VERBOSITY,
    web_search_allowed: Boolean(allowWebSearch && ALLOW_WEB_SEARCH),
    output_text: extractOutputText(response),
    raw_usage: response.usage || null
  };
}

app.get("/api/health", async (req, res) => {
  try {
    const policy = await readJson("ai_policy.json");
    res.json({
      ok: true,
      api_key_configured: Boolean(OPENAI_API_KEY && !OPENAI_API_KEY.includes("REEMPLAZA")),
      model_policy_mode: MODEL_POLICY_MODE,
      fixed_model: FIXED_MODEL,
      reasoning_effort: REASONING_EFFORT,
      verbosity: VERBOSITY,
      max_output_tokens: MAX_OUTPUT_TOKENS,
      allow_web_search: ALLOW_WEB_SEARCH,
      offline_vendor_mode: OFFLINE_VENDOR_MODE,
      policy_version: policy.policy_version,
      max_packet_chars: MAX_PACKET_CHARS,
      max_chunks_per_request: MAX_CHUNKS_PER_REQUEST,
      max_chunk_chars: MAX_CHUNK_CHARS
    });
  } catch (err) { res.status(500).json({ ok: false, error: err.message }); }
});
app.get("/api/firebase-config", (req, res) => {
  if (!FB_PROJECT_ID || !FB_API_KEY) {
    return res.status(503).json({ ok: false, error: "Firebase no configurado en .env (FIREBASE_PROJECT_ID y FIREBASE_API_KEY requeridos)." });
  }
  res.json({
    ok: true,
    apiKey: FB_API_KEY,
    authDomain: FB_AUTH_DOMAIN || `${FB_PROJECT_ID}.firebaseapp.com`,
    projectId: FB_PROJECT_ID,
    appId: FB_APP_ID
  });
});
app.get("/api/models/resolve", async (req, res) => {
  try {
    const info = await resolveModel();
    res.json({ ok: true, selected: info.selected, reason: info.reason, available: info.available, checked_at: new Date().toISOString(), model_policy_mode: MODEL_POLICY_MODE, models_sample: (info.models || []).filter(m => /^gpt-/.test(m)).slice(0, 100) });
  } catch (err) { res.status(err.status || 500).json({ ok: false, error: err.message, details: err.details || null }); }
});
app.post("/api/ai/chat", async (req, res) => {
  try {
    const { userInstruction, packet, conversation, modelOverride, mode, allowWebSearch } = req.body || {};
    const info = await resolveModel();
    const selectedModel = validateModelOverride(modelOverride) || info.selected;
    const result = await createResponse({ task: `Chat por expediente. Modo: ${mode || "análisis estratégico protegido"}. ${modeDirective(mode)}`, userInstruction, packet, conversation, selectedModel, allowWebSearch });
    res.json({ ok: true, model_resolution: info, result });
  } catch (err) { res.status(err.status || 500).json({ ok: false, error: err.message, details: err.details || null }); }
});
app.post("/api/ai/draft", async (req, res) => {
  try {
    const { userInstruction, packet, conversation, modelOverride, draftType, recipient, allowWebSearch } = req.body || {};
    const info = await resolveModel();
    const selectedModel = validateModelOverride(modelOverride) || info.selected;
    const result = await createResponse({ task: `Genera o mejora borrador versionado. Tipo: ${draftType || "escrito protegido"}. Destinatario: ${recipient || "autoridad competente"}. ${modeDirective(draftType || "")}`, userInstruction, packet, conversation, selectedModel, allowWebSearch });
    res.json({ ok: true, model_resolution: info, result });
  } catch (err) { res.status(err.status || 500).json({ ok: false, error: err.message, details: err.details || null }); }
});

function sanitizeFileName(name = "documento") {
  return String(name).normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^\w.-]+/g, "_").slice(0, 120) || "documento";
}
function limitedExportContent(content = "") {
  const s = String(content || "");
  if (s.length > MAX_EXPORT_CHARS) {
    const err = new Error(`Contenido de exportación demasiado grande (${s.length} caracteres). Límite: ${MAX_EXPORT_CHARS}.`);
    err.status = 413;
    throw err;
  }
  return s;
}
app.post("/api/export/txt", async (req, res) => {
  try {
    const { title = "documento", content = "" } = req.body || {};
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("Content-Disposition", `attachment; filename="${sanitizeFileName(title)}.txt"`);
    res.send(limitedExportContent(content));
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});
app.post("/api/export/html", async (req, res) => {
  try {
    const { title = "documento", content = "" } = req.body || {};
    const safeContent = limitedExportContent(content);
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>${String(title).replace(/[<>&]/g,"")}</title><style>body{font-family:Georgia,serif;max-width:860px;margin:40px auto;line-height:1.55}pre{white-space:pre-wrap}</style></head><body><h1>${String(title).replace(/[<>&]/g,"")}</h1><pre>${safeContent.replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]))}</pre></body></html>`;
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.setHeader("Content-Disposition", `attachment; filename="${sanitizeFileName(title)}.html"`);
    res.send(html);
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});
app.post("/api/export/docx", async (req, res) => {
  try {
    const { title = "documento", content = "" } = req.body || {};
    const { Document, Packer, Paragraph, TextRun, HeadingLevel } = await import("docx");
    const lines = limitedExportContent(content).split(/\n/);
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({ text: title, heading: HeadingLevel.HEADING_1 }),
          ...lines.map(line => new Paragraph({ children: [new TextRun(line || " ")] }))
        ]
      }]
    });
    const buffer = await Packer.toBuffer(doc);
    res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
    res.setHeader("Content-Disposition", `attachment; filename="${sanitizeFileName(title)}.docx"`);
    res.send(buffer);
  } catch (err) {
    res.status(500).json({ ok: false, error: "No se pudo generar DOCX. Ejecuta npm install. " + err.message });
  }
});
app.post("/api/export/pdf", async (req, res) => {
  try {
    const { title = "documento", content = "" } = req.body || {};
    const PDFKitModule = await import("pdfkit");
    const PDFDocument = PDFKitModule.default || PDFKitModule;
    const doc = new PDFDocument({ margin: 54, size: "LETTER" });
    const chunks = [];
    doc.on("data", c => chunks.push(c));
    doc.on("end", () => {
      const pdf = Buffer.concat(chunks);
      res.setHeader("Content-Type", "application/pdf");
      res.setHeader("Content-Disposition", `attachment; filename="${sanitizeFileName(title)}.pdf"`);
      res.send(pdf);
    });
    doc.fontSize(16).text(title, { underline: true });
    doc.moveDown();
    doc.fontSize(11).text(limitedExportContent(content), { align: "left" });
    doc.end();
  } catch (err) {
    res.status(500).json({ ok: false, error: "No se pudo generar PDF. Ejecuta npm install. " + err.message });
  }
});
app.get("/api/doctor", async (req, res) => {
  const checks = [];
  async function exists(rel) {
    try { await fs.access(path.join(__dirname, rel)); return true; } catch { return false; }
  }
  checks.push({ name: "OPENAI_API_KEY", ok: Boolean(OPENAI_API_KEY && !OPENAI_API_KEY.includes("REEMPLAZA")), detail: "Clave API configurada" });
  checks.push({ name: "vendor pdf.js", ok: await exists("public/vendor/pdfjs/pdf.mjs"), detail: "Asset local PDF.js" });
  checks.push({ name: "vendor pdf.worker", ok: await exists("public/vendor/pdfjs/pdf.worker.mjs"), detail: "Worker local PDF.js" });
  checks.push({ name: "vendor tesseract", ok: await exists("public/vendor/tesseract/tesseract.min.js"), detail: "Asset local Tesseract.js" });
  checks.push({ name: "tesseract worker", ok: await exists("public/vendor/tesseract/worker.min.js"), detail: "Worker local Tesseract.js" });
  checks.push({ name: "tesseract core", ok: await exists("public/vendor/tesseract/tesseract-core.wasm.js"), detail: "Core local Tesseract.js" });
  checks.push({ name: "tessdata spa", ok: await exists("public/vendor/tessdata/spa.traineddata.gz"), detail: "Idioma OCR español local" });
  checks.push({ name: "tessdata eng", ok: await exists("public/vendor/tessdata/eng.traineddata.gz"), detail: "Idioma OCR inglés local" });
  res.json({ ok: true, offline_vendor_mode: OFFLINE_VENDOR_MODE, checks });
});

app.listen(PORT, () => console.log(`DefensaIPN.ai v7.1 listo en http://localhost:${PORT}`));
