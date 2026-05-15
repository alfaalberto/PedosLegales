import fs from "fs/promises";
const files = [
  "server.js",
  "public/index.html",
  "prompts/system_defensaipn.txt",
  "ai_policy.json",
  "public/vendor/pdfjs/pdf.mjs",
  "public/vendor/pdfjs/pdf.worker.mjs",
  "public/vendor/tesseract/tesseract.min.js",
  "public/vendor/tessdata/spa.traineddata.gz"
];
for (const f of files) {
  try {
    const st = await fs.stat(f);
    console.log("OK", f, `${(st.size/1024).toFixed(1)} KB`);
  } catch {
    console.log("MISSING", f);
  }
}
console.log("\nSi faltan vendor/tessdata, ejecuta: npm run prepare:offline");
