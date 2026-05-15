# DefensaIPN.ai v7.1 — Offline Profesional Auditada y Corregida

Esta versión corrige fallos reales detectados en la auditoría de v7 y endurece el uso documental.

## Correcciones críticas v7.1

- Se restauró `ocrPdf()`, que faltaba en v7 aunque era llamada por `ocrFile()`.
- Se agregó extracción de texto nativo en PDFs antes de aplicar OCR.
- Se restauraron utilidades faltantes: `splitPages`, `normalize`, `tokens`, `downloadText`.
- Se agregaron `deleteDoc()` y `deleteCaseDocs()`.
- Se agregó `renderStorage()` para evitar error de arranque.
- Se agregó `importBackupObject()` para que el respaldo cifrado pueda restaurarse.
- El backend ahora conserva metadatos de gobierno documental en el paquete IA:
  - rol documental,
  - etapa,
  - estado,
  - prioridad,
  - confidencialidad,
  - acción pendiente,
  - vencimiento,
  - etiquetas.
- Se corrigió duplicación de historial en el prompt enviado a IA.
- Se reforzó `prepare:offline` para copiar worker/core de Tesseract.
- Se agregaron límites de exportación.

## Instalación

```bash
npm install
cp .env.example .env
```

Edita `.env`:

```text
OPENAI_API_KEY=tu_llave_real
```

Prepara assets offline:

```bash
npm run prepare:offline
npm run check
npm run doctor
```

Inicia:

```bash
npm start
```

Abre:

```text
http://localhost:8787
```

## Uso recomendado

1. Crear caso.
2. Importar carpeta completa.
3. Extraer texto/OCR.
4. Cotejar OCR.
5. Clasificar documentos.
6. Generar índice maestro.
7. Preguntar con RAG.
8. Guardar borrador.
9. Exportar respaldo cifrado.

## Advertencia

La app ya es mucho más robusta, pero sigue requiriendo prueba local con tus documentos reales.
