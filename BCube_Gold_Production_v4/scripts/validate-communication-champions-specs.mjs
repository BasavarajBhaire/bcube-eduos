import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const sourceDir = path.join(root, "production-prompts/communication-champions/nursery/v3/pages");
const productionDir = path.join(root, "BCube_Gold_Production_v4/production/nursery/communication-champions/pages");
const manifestPath = path.join(root, "BCube_Gold_Production_v4/manifests/nursery/communication-champions.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const failures = [];
let checked = 0;

for (const [pageNumber, promptId, title, slug] of manifest.jobs) {
  const basename = `${promptId}-${slug}`;
  const jsonPath = path.join(sourceDir, `${basename}.json`);
  const markdownPath = path.join(sourceDir, `${basename}.md`);
  const productionPath = path.join(productionDir, `${basename}.md`);

  for (const requiredPath of [jsonPath, markdownPath, productionPath]) {
    if (!fs.existsSync(requiredPath)) failures.push(`${promptId}: missing ${path.relative(root, requiredPath)}`);
  }
  if (!fs.existsSync(jsonPath) || !fs.existsSync(productionPath)) continue;

  const source = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
  const page = source.page_data;
  const production = fs.readFileSync(productionPath, "utf8");
  const exactValues = [
    source.prompt_id,
    page.title,
    page.learning_objective,
    page.activity.instruction,
    page.activity.evidence,
    page.teacher_prompt.facilitation,
    page.parent_prompt.home_activity,
    page.illustration.scene,
    page.individual_specification.visible_text,
    page.individual_specification.response_space,
    page.individual_specification.page_specific_prohibition,
  ];

  if (source.prompt_id !== promptId) failures.push(`${promptId}: source prompt ID mismatch`);
  if (page.page_number !== pageNumber) failures.push(`${promptId}: source page-number mismatch`);
  if (page.title !== title) failures.push(`${promptId}: manifest/source title mismatch`);

  for (const value of exactValues) {
    if (!production.includes(value)) failures.push(`${promptId}: production specification omitted canonical value: ${value}`);
  }

  const requiredRules = [
    "Exactly one flat, front-facing A4 portrait page.",
    "Official BCube logo reserved at top left",
    page.page_type === "cover"
      ? "No visible page number or interior-page footer on the cover."
      : `Page number ${pageNumber} at bottom right.`,
    "No collage, contact sheet, mockup, extra page, extra activity or unrelated decoration.",
  ];
  for (const rule of requiredRules) {
    if (!production.includes(rule)) failures.push(`${promptId}: missing v4 production rule: ${rule}`);
  }

  if (pageNumber === 2) {
    const metadata = [
      "© 2025 BCube Future Academy. All rights reserved.",
      "BCube Future Skills Learning Series™",
      "407, DSMAX Sky Supreme KST Bangalore - 560060",
      "info@bcubefutureacademy.in",
      "bcubefutureacademy.in",
      "First Edition 2025",
    ];
    for (const value of metadata) {
      if (!production.includes(value)) failures.push(`${promptId}: missing locked publication metadata: ${value}`);
    }
  }

  if (pageNumber === 3) {
    for (const [contentsPage, , contentsTitle] of manifest.jobs) {
      const row = `| ${contentsPage} | ${contentsTitle} |`;
      if (!production.includes(row)) failures.push(`${promptId}: missing canonical contents row: ${row}`);
    }
  }

  checked += 1;
}

if (checked !== 41) failures.push(`Expected 41 specifications, checked ${checked}`);

if (failures.length > 0) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log(`PASS: all ${checked} Communication Champions specifications (P001–P041) match the canonical manifest and page packages.`);
