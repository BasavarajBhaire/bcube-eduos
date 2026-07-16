---
rule_id: PE-GEO-002
title: Safe-Area Protection
engine: Publishing
version: 3.0.0
status: Active
severity: Critical
owner: BCube Publishing Lead
---

# PE-GEO-002 — Safe-Area Protection

## Purpose

Prevent trim loss, binding obstruction, and unusable child-response areas by protecting all essential content inside the approved live area.

## Normative requirement

All essential text, faces, hands, learning objects, response spaces, logos, page numbers, and instructional cues **MUST** remain inside the calculated safe area.

## Essential content

The following are always treated as essential:

- page title
- child-facing instructions
- official BCube logo
- target learning object
- teacher and child faces
- hands performing the learning action
- tracing, matching, colouring, writing, or cutting spaces
- page number
- required legal or publisher text

## Inputs

- resolved geometry from `PE-GEO-001`
- component bounding boxes
- activity-space metadata
- binding edge

## Outputs

- safe-area compliance status
- violating component list
- recommended correction

## Validation

A component fails when any essential portion crosses the safe-area boundary. Decorative backgrounds MAY extend through bleed, but decorative elements MUST NOT create a false activity boundary or obscure essential content.

## Failure severity

Critical for essential content; Major for nonessential content that materially harms readability.

## Repair strategy

1. Move the component inward.
2. Reduce scale without violating readability rules.
3. Recompose the scene.
4. Increase template-safe spacing.
5. Reject the generated artwork when repair would damage the learning objective.

## Compiler mapping

The final prompt SHALL state that all essential content remains within the live area and that the activity zone is protected from overlap.

## Gold example

A child traces a large curved line positioned well inside the safe area, with the teacher and Star nearby but not covering the path.

## Anti-patterns

- cut line inside bleed
- face near outer trim
- activity box hidden by a speech bubble
- page number touching the edge
- logo placed partly outside the live area

## Change history

- 3.0.0 — Initial active rule.
