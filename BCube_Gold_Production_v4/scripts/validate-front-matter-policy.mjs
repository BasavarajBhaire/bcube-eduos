import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const policyPath = path.join(root, "BCube_Gold_Production_v4/portfolio-front-matter-policy.json");
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));
const failures = [];

function requireCondition(condition, message) {
  if (!condition) failures.push(message);
}

requireCondition(policy.total_books === 30, "Portfolio must contain 30 books");
requireCondition(policy.packages_per_book === 43, "Each migrated book must contain 43 packages");
requireCondition(policy.total_packages === 1290, "Portfolio total must be 1,290 packages");
requireCondition(policy.total_books * policy.packages_per_book === policy.total_packages, "Portfolio arithmetic mismatch");
requireCondition(policy.last_production_position === 43, "Final production position must be 43");
requireCondition(policy.last_logical_page === 42, "Final logical page must be 42");

const expected = [
  [1, "cover", null, false],
  [2, "about_this_book", 1, false],
  [3, "copyright", 2, false],
  [4, "contents_part_1", 3, false],
  [5, "contents_part_2", 4, false],
  [6, "welcome", 5, true],
];

for (const [position, role, logical, visible] of expected) {
  const actual = policy.front_matter.find((entry) => entry.production_position === position);
  requireCondition(Boolean(actual), `Missing front-matter position ${position}`);
  if (!actual) continue;
  requireCondition(actual.role === role, `Position ${position} must have role ${role}`);
  requireCondition(actual.logical_page === logical, `Position ${position} logical-page mismatch`);
  requireCondition(actual.printed_number_visible === visible, `Position ${position} visibility mismatch`);
}

requireCondition(JSON.stringify(policy.contents.production_positions) === JSON.stringify([4, 5]), "Contents must occupy positions 4 and 5");
requireCondition(policy.contents.first_listed_production_position === 6, "Contents must begin by listing Welcome at P006");
requireCondition(policy.contents.first_listed_logical_page === 5, "Contents must begin at reader page 5");

const index = fs.readFileSync(path.join(root, "BCube_Gold_Production_v4/CANONICAL_BOOK_AND_PAGE_INDEX.md"), "utf8");
const linkedBooks = [...index.matchAll(/^\d+\. \[/gm)].length;
requireCondition(linkedBooks === 30, `Canonical index must list 30 books; found ${linkedBooks}`);

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("PASS: portfolio front-matter policy covers 30 books, 43 packages per book and 1,290 packages total.");
