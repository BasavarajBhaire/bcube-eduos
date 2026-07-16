# Wave 2 — Self-Contained Production Prompt Policy

## Purpose

Wave 2 converts the repository foundation into production-ready prompt assets. Its most important requirement is that every final page prompt must be self-contained and directly usable by an image-generation system.

## Core decision

Shared rules, fragments and templates are maintained as reusable source assets for governance and consistency. They are **not** passed to the image model as unresolved references.

The Prompt Compiler must expand every referenced rule, fragment and template into one complete page-specific prompt before generation.

## Mandatory output rule

A final BCube Gold Production Prompt must contain, in full:

1. technical and publishing specification;
2. exact page title and page number;
3. age and developmental requirements;
4. learning objective and child action;
5. page-specific teacher-child interaction;
6. page-specific parent or home-learning support where applicable;
7. complete illustration scene description;
8. exact character appearance, pose, expression and interaction;
9. visual hierarchy, focal point and protected activity zones;
10. typography and text requirements;
11. all negative constraints;
12. final validation checklist.

The prompt must never say only:

- “apply the common publishing module”;
- “use Character Engine rules”;
- “follow template TPL-ACT-001”;
- “inherit the standard teacher interaction”; or
- “refer to the global negative prompt.”

Those references are valid inside the repository and compiler, but they must be expanded before the prompt is sent to image generation.

## Page-specific dominance

Shared content provides consistency, but page-specific instructions control the final scene. The compiler must preserve the unique learning objective, activity, teacher interaction, child response, object placement, writing area and micro-story for each page.

A compiled page prompt must not become a generic picture prompt with only the title changed.

## No-loss compilation

Compilation fails when any mandatory page-specific field is empty, ambiguous, contradictory or replaced by a generic fragment.

Critical fields include:

- `page_title`
- `page_number`
- `learning_objective`
- `child_action`
- `teacher_action`
- `primary_scene`
- `activity_space`
- `text_content`
- `star_role`
- `negative_constraints`

## Text strategy

Final educational text must be supplied exactly. Image generation should not invent instructional wording. When reliable text rendering is unavailable, the illustration prompt must preserve clearly marked text-safe zones and the publishing workflow must place exact text during layout.

## Validation requirement

Before generation, the compiled prompt must pass:

- self-contained prompt validation;
- page-specific completeness validation;
- contradiction detection;
- activity-space validation;
- exact-text validation;
- teacher-child interaction validation;
- character continuity validation; and
- publication safety validation.

## Acceptance test

A reviewer who sees only the final compiled prompt, without access to repository modules, must be able to understand and generate the intended complete workbook page.
