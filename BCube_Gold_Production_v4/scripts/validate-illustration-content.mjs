#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const [directory, startRaw, endRaw] = process.argv.slice(2);
if (!directory || !startRaw || !endRaw) {
  console.error("Usage: node validate-illustration-content.mjs <directory> <reader-start> <reader-end>");
  process.exit(2);
}
const start = Number(startRaw), end = Number(endRaw);
const forbiddenKinds = /^(text|label|letter|initial|oval|blank|placeholder|generic_icon)$/i;
const failures = [];
const pngs = fs.readdirSync(directory).filter((name) => /\.png$/i.test(name));

for (const pageFile of pngs) {
  const match = pageFile.match(/-P(\d{3})-/i);
  if (!match) continue;
  const packageNumber = Number(match[1]);
  const readerNumber = packageNumber - 1;
  if (readerNumber < start || readerNumber > end) continue;
  const evidencePath = path.join(directory, pageFile.replace(/\.png$/i, ".illustration-evidence.json"));
  if (!fs.existsSync(evidencePath)) {
    failures.push(`${pageFile}: missing illustration evidence`);
    continue;
  }
  let evidence;
  try { evidence = JSON.parse(fs.readFileSync(evidencePath, "utf8")); }
  catch { failures.push(`${pageFile}: invalid evidence JSON`); continue; }

  const required = evidence.required_visual_elements || [];
  const observed = new Set(evidence.observed_visual_elements || []);
  const regions = evidence.illustration_regions || [];
  if (!evidence.canonical_instruction) failures.push(`${pageFile}: missing canonical instruction`);
  if (!evidence.canonical_scene) failures.push(`${pageFile}: missing canonical scene`);
  if (!required.length) failures.push(`${pageFile}: no required visual elements`);
  for (const item of required) if (!observed.has(item)) failures.push(`${pageFile}: required visual not observed: ${item}`);
  if (!regions.length) failures.push(`${pageFile}: no illustration regions`);
  for (const region of regions) {
    if (!region.subject) failures.push(`${pageFile}: unnamed illustration region`);
    if (forbiddenKinds.test(region.kind || "")) failures.push(`${pageFile}: forbidden picture substitute: ${region.kind}`);
    if (!/^(illustration|official_asset)$/i.test(region.kind || "")) failures.push(`${pageFile}: invalid region kind: ${region.kind || "missing"}`);
  }
  if (evidence.contains_text_only_picture_substitutes !== false) failures.push(`${pageFile}: text-only picture substitute not cleared`);
  if (evidence.contains_empty_required_visual_regions !== false) failures.push(`${pageFile}: empty required region not cleared`);
  if (evidence.instruction_supported_by_illustrations !== true) failures.push(`${pageFile}: instruction not supported by illustrations`);
  if (evidence.review_status !== "PASS" || !evidence.reviewed_by) failures.push(`${pageFile}: human illustration review missing or failed`);
}

if (failures.length) {
  console.error(`REJECTED: ${failures.length} illustration-content defect(s)`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log(`PASS: reader pages ${start}–${end} have complete illustration evidence and review approval.`);
