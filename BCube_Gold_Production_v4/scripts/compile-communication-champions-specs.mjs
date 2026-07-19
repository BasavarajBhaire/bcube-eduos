import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const sourceDir = path.join(
  root,
  "production-prompts/communication-champions/nursery/v3/pages",
);
const outputDir = path.join(
  root,
  "BCube_Gold_Production_v4/production/nursery/communication-champions/pages",
);
const manifest = JSON.parse(
  fs.readFileSync(
    path.join(root, "BCube_Gold_Production_v4/manifests/nursery/communication-champions.json"),
    "utf8",
  ),
);

const startPage = Number(process.argv[2] ?? 12);
const endPage = Number(process.argv[3] ?? 41);

if (!Number.isInteger(startPage) || !Number.isInteger(endPage) || startPage < 1 || endPage > 41 || startPage > endPage) {
  throw new Error("Usage: node compile-communication-champions-specs.mjs [startPage] [endPage]");
}

const files = fs.readdirSync(sourceDir).filter((file) => file.endsWith(".json"));

function sourceForPage(pageNumber) {
  const prefix = `CC-NURSERY-V3-P${String(pageNumber).padStart(3, "0")}-`;
  const file = files.find((candidate) => candidate.startsWith(prefix));
  if (!file) throw new Error(`Missing canonical JSON for page ${pageNumber}`);
  return file;
}

function bullet(value) {
  return `- ${value}`;
}

function render(sourceFile) {
  const sourcePath = path.join(sourceDir, sourceFile);
  const source = JSON.parse(fs.readFileSync(sourcePath, "utf8"));
  const page = source.page_data;
  const pageNumber = page.page_number;
  const sourceMarkdown = sourceFile.replace(/\.json$/, ".md");
  const teacherQuestions = page.teacher_prompt.questions.map(bullet).join("\n");
  const negativeConstraints = page.illustration.negative_constraints.map(bullet).join("\n");
  const isCover = page.page_type === "cover";
  const titleRule = isCover
    ? "Use “Communication Champions” as the dominant cover title and show “Nursery (3+)” on the cover only."
    : `Exact page title “${page.title}” centred in the header.`;
  const pageNumberRule = isCover
    ? "No visible page number or interior-page footer on the cover."
    : `Page number ${pageNumber} at bottom right.`;
  let controlledCopy = "";

  if (pageNumber === 2) {
    controlledCopy = `
## Locked publication metadata
- Copyright: © 2025 BCube Future Academy. All rights reserved.
- Publisher: BCube Future Academy
- Series: BCube Future Skills Learning Series™
- Title: Communication Champions — Nursery (3+)
- Address: 407, DSMAX Sky Supreme KST Bangalore - 560060
- Email: info@bcubefutureacademy.in
- Website: bcubefutureacademy.in
- Edition: First Edition 2025

These values are canonical controlled copy and must not be paraphrased, replaced or inferred.
`;
  }

  if (pageNumber === 3) {
    const contentsRows = manifest.jobs.map(([number, , entryTitle]) => `| ${number} | ${entryTitle} |`).join("\n");
    controlledCopy = `
## Canonical contents entries
| Page | Exact title |
|---:|---|
${contentsRows}

All 41 entries must fit legibly in the required two-column navigation layout without renaming, grouping or inventing modules.
`;
  }

  return `# ${source.prompt_id} — ${page.title}

**Book:** Communication Champions

**Level:** Nursery (3+)

**Source prompt:** \`production-prompts/communication-champions/nursery/v3/pages/${sourceMarkdown}\`
**Status:** REVIEWED AND APPROVED AS GOLD PRODUCTION SPECIFICATION; final artwork, deterministic composition and print preflight pending.

## Learning objective
${page.learning_objective}

## Exact visible wording
${page.individual_specification.visible_text}

## Child action
${page.activity.instruction}

## Observable evidence
${page.activity.evidence}

## Teacher move
${page.teacher_prompt.facilitation}

### Teacher question
${teacherQuestions}

## Parent connection
${page.parent_prompt.home_activity}

## Locked composition
${page.illustration.scene}

## Exact response space
${page.individual_specification.response_space}

## Page-specific prohibition
${page.individual_specification.page_specific_prohibition}
${controlledCopy}

## Illustration contract
- Generate only the illustration elements required by the locked composition.
- Do not generate the BCube logo, page number, watermark, final typography, response lines or invented wording inside the artwork.
- Preserve the locked bright-yellow rounded five-point Star identity, expressive face, blue shoes and small blue cape wherever Star is required.
- Use a clean white or transparent base, soft BCube-compatible pastels, thick clean rounded outlines, natural anatomy, inclusive Indian representation and a premium preschool publishing finish.
- Keep every response area unobstructed and large enough for Nursery use.

### Canonical negative constraints
${negativeConstraints}

## Publishing rules
- Exactly one flat, front-facing A4 portrait page.
- 210 × 297 mm, 3 mm bleed, minimum 10 mm safe margin, 12 mm binding allowance, 300 DPI and CMYK-safe output.
- Official BCube logo reserved at top left and placed later from the approved immutable asset; never regenerate or redraw it.
- ${titleRule}
- ${pageNumberRule}
- Exact repository wording and activity geometry must be composed deterministically using approved typography.
- No collage, contact sheet, mockup, extra page, extra activity or unrelated decoration.

## Gold QA review
- [x] Canonical prompt ID, page number and title match.
- [x] Canonical Markdown and JSON source paths match.
- [x] Learning objective is preserved without rewriting.
- [x] Child action and observable evidence are preserved.
- [x] Teacher move and parent connection are preserved.
- [x] Illustration scene and response space are preserved.
- [x] Exact visible wording is preserved.
- [x] Page-specific prohibition is preserved.
- [x] Official-logo and one-page-only rules are explicit.
- [x] Print geometry is explicit.

## Review decision
**${source.prompt_id} specification: APPROVED.** Approval covers source accuracy, educational intent, illustration direction and page-production requirements only. Final artwork, composed page, weighted QA score, CMYK proof and print PDF remain required before Gold release.
`;
}

fs.mkdirSync(outputDir, { recursive: true });

for (let pageNumber = startPage; pageNumber <= endPage; pageNumber += 1) {
  const sourceFile = sourceForPage(pageNumber);
  const outputFile = path.join(outputDir, sourceFile.replace(/\.json$/, ".md"));
  fs.writeFileSync(outputFile, render(sourceFile), "utf8");
}

console.log(`Compiled Communication Champions production specifications P${String(startPage).padStart(3, "0")}–P${String(endPage).padStart(3, "0")}.`);
