// Entry program for the 26 November 2026 news image (Node 22, standard
// library only). It places the finished front-page PNG, entry.png, at
// /output/entry.png. Running it twice writes the same bytes both times.
//
// Local check: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
writeFileSync(
  join(outDir, "entry.png"),
  readFileSync(join(here, "entry.png")),
);
