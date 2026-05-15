import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import https from "https";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");

async function ensureDir(p) { await fs.mkdir(p, { recursive: true }); }
async function exists(p) { try { await fs.access(p); return true; } catch { return false; } }
async function copyIfExists(src, dst) {
  if (!(await exists(src))) {
    console.warn("WARN missing", src);
    return false;
  }
  await ensureDir(path.dirname(dst));
  await fs.copyFile(src, dst);
  console.log("OK copied", path.relative(root, dst));
  return true;
}
function download(url, dest, maxRedirects = 8) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        if (maxRedirects <= 0) return reject(new Error("Demasiados redireccionamientos: " + url));
        return download(res.headers.location, dest, maxRedirects - 1).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode} ${url}`));
      const chunks = [];
      res.on("data", c => chunks.push(c));
      res.on("end", async () => {
        await ensureDir(path.dirname(dest));
        await fs.writeFile(dest, Buffer.concat(chunks));
        console.log("OK downloaded", path.relative(root, dest));
        resolve();
      });
    }).on("error", reject);
  });
}
async function copyFirst(candidates, dest) {
  for (const rel of candidates) {
    if (await copyIfExists(path.join(root, rel), dest)) return true;
  }
  return false;
}

await ensureDir(path.join(root, "public/vendor/pdfjs"));
await ensureDir(path.join(root, "public/vendor/tesseract"));
await ensureDir(path.join(root, "public/vendor/tessdata"));

await copyIfExists(
  path.join(root, "node_modules/pdfjs-dist/build/pdf.mjs"),
  path.join(root, "public/vendor/pdfjs/pdf.mjs")
);
await copyIfExists(
  path.join(root, "node_modules/pdfjs-dist/build/pdf.worker.mjs"),
  path.join(root, "public/vendor/pdfjs/pdf.worker.mjs")
);

await copyFirst([
  "node_modules/tesseract.js/dist/tesseract.min.js",
  "node_modules/tesseract.js/dist/tesseract.esm.min.js",
  "node_modules/tesseract.js/src/index.js"
], path.join(root, "public/vendor/tesseract/tesseract.min.js"));

await copyFirst([
  "node_modules/tesseract.js/dist/worker.min.js",
  "node_modules/tesseract.js/src/worker-script/browser/index.js"
], path.join(root, "public/vendor/tesseract/worker.min.js"));

await copyFirst([
  "node_modules/tesseract.js-core/tesseract-core.wasm.js",
  "node_modules/tesseract.js-core/tesseract-core-simd.wasm.js"
], path.join(root, "public/vendor/tesseract/tesseract-core.wasm.js"));

await copyFirst([
  "node_modules/tesseract.js-core/tesseract-core.wasm",
  "node_modules/tesseract.js-core/tesseract-core-simd.wasm"
], path.join(root, "public/vendor/tesseract/tesseract-core.wasm"));

const langs = ["spa", "eng"];
for (const lang of langs) {
  const dest = path.join(root, `public/vendor/tessdata/${lang}.traineddata.gz`);
  if (await exists(dest)) { console.log("OK exists", path.relative(root, dest)); continue; }
  const url = `https://tessdata.projectnaptha.com/4.0.0/${lang}.traineddata.gz`;
  try { await download(url, dest); } catch (e) { console.warn("WARN no se pudo descargar", lang, e.message); }
}

console.log("\nPreparación offline terminada. Ejecuta npm run doctor y luego npm start.");
