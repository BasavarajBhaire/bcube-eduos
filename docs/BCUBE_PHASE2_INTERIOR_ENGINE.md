# BCube Publishing Engine — Phase 2 Interior Pages

Phase 2 adds a deterministic, data-driven activity-page pipeline for Nursery, LKG and UKG. It does not generate complete pages with AI. AI or a designer supplies only the clean activity illustration. The engine owns branding, typography, layout, official assets, guidance panels, page numbering and QA evidence.

## Supported activity types

`observe`, `match`, `trace`, `colour`, `draw`, `speak`, `listen`, `count`, `connect`, `complete`, `maze`, `explore`, `think`, `reflect`, `sequence`, `sort`, `circle`, `assessment`.

## Components rendered by the engine

- Official BCube logo
- Page title
- Learning goal
- Student instruction
- Main illustration/activity frame
- Teacher Guidance panel
- Parent Partnership panel
- Official Star mascot
- Printed page number
- Composition evidence and input QA report

## Canvas contract

- A4 portrait
- 2480 × 3508 pixels
- 300 DPI
- One physical page per output
- Safe margins and locked component bounds
- No generated branding or generated mascot

## Command

```bash
python scripts/run_bcube_activity_pipeline.py \
  --level nursery \
  --book communication-champions \
  --physical-page 7 \
  --page-number 6 \
  --activity-type speak \
  --title "Speak and Share" \
  --objective "Speak clearly and listen while others share." \
  --instruction "Look at the picture. Tell the group one idea, then listen to a friend." \
  --teacher-prompt "Model one complete sentence. Invite each child to speak in turn and acknowledge every response." \
  --parent-prompt "At home, ask the child to describe one favourite object using a complete sentence." \
  --illustration "D:\\BCube\\illustrations\\CC-NURSERY-V4-P007.png"
```

## Outputs

```text
production-renders/activity/page-data/<PAGE_ID>.json
production-renders/activity/illustrations/<PAGE_ID>.png
production-renders/activity/pages/<PAGE_ID>.png
production-renders/activity/evidence/<PAGE_ID>.json
validation/rendered-pages/<PAGE_ID>.activity-input.json
```

## Separation of responsibilities

The illustration must contain no BCube logo, no official Star mascot, no page title, no page number, no teacher panel, no parent panel and no complete page layout. The engine adds those deterministically.

## Phase 2 completion criteria

- Universal template and activity-type registry
- Structured input validation
- Deterministic A4 composer
- Official asset composition
- Teacher and parent components
- Evidence manifest
- Cross-level regression coverage
- Stable command-line runner
