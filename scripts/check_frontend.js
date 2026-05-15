import fs from "fs";
import vm from "vm";
const html = fs.readFileSync("public/index.html", "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");
new vm.Script(scripts);
console.log("Frontend script syntax OK");
