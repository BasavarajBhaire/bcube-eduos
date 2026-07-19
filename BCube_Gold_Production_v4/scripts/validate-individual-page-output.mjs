#!/usr/bin/env node

import fs from "node:fs";

const [directory, expectedRaw] = process.argv.slice(2);
if (!directory || !expectedRaw) {
  console.error("Usage: node validate-individual-page-output.mjs <directory> <expected-count>");
  process.exit(2);
}

const expected = Number(expectedRaw);
if (!Number.isInteger(expected) || expected < 1) {
  console.error("Expected count must be a positive integer.");
  process.exit(2);
}

const forbidden = /(contact[-_ ]?sheet|montage|collage|overview|grid|composite)/i;
const entries = fs.readdirSync(directory, { withFileTypes: true });
const files = entries.filter((entry) => entry.isFile()).map((entry) => entry.name);
const forbiddenFiles = files.filter((name) => forbidden.test(name));
const pages = files.filter((name) => /\.png$/i.test(name) && !forbidden.test(name));

const failures = [];
if (forbiddenFiles.length) {
  failures.push("forbidden composite/QA files present: " + forbiddenFiles.join(", "));
}
if (pages.length !== expected) {
  failures.push("expected " + expected + " individual PNG pages, found " + pages.length);
}

if (failures.length) {
  console.error("REJECTED: " + failures.join("; "));
  process.exit(1);
}

console.log("PASS: " + pages.length + " individual page files; no combined-page artifacts.");
