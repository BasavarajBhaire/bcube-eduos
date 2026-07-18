# BCube Publishing Handbook (BPH)

**Status:** Active implementation guide  
**Companion standard:** [BCube Publishing Standard v1.0](../BCube_Publishing_Standard/BCube_Publishing_Standard_v1.0.md)

The BPH explains how to apply BPS in day-to-day production. BPS contains mandatory rules; BPH contains practical procedures, examples, checklists, and troubleshooting guidance.

## Standard page workflow

1. Read the exact canonical page source from the repository.
2. Confirm page identity, type, title, visible wording, learning objective, and activity.
3. Resolve the exact versioned template.
4. Resolve only certified Gold assets.
5. Generate illustration candidates without logo, typography, page number, or invented text.
6. Select and certify the approved illustration asset.
7. Compose the page deterministically.
8. Run educational, visual, brand, technical, and publishing QA.
9. Reject and correct any critical defect.
10. Add the approved page to the book proof only after it reaches Gold status.

## Illustration request checklist

An illustration request must define:

- page ID and page type;
- exact educational purpose;
- required subjects and exact count;
- approved character asset IDs or locked character descriptions;
- scene and action;
- age and complexity constraints;
- composition needs for the assigned layout region;
- explicit exclusions: no text, no logo, no page number, no watermark, no multi-page collage.

## Page review checklist

### Source fidelity

- Exact repository title and visible wording
- Correct book, level, page ID, and page type
- No invented content

### Educational quality

- One clear learning purpose
- Child action is obvious
- Nursery complexity is appropriate
- Teacher and parent guidance is usable where required

### Visual quality

- One dominant focal point
- Consistent recurring characters
- No overcrowding or tiny details
- Illustration supports rather than decorates the activity

### Brand and production

- Official logo asset only
- Correct template and typography tokens
- Correct page-number policy
- A4 portrait, 300 DPI, safe margins
- No clipping, overflow, substitution, or missing assets

## Rejection examples

Reject an output when it:

- turns the BCube logo into the main illustration;
- generates several pages in one image;
- writes incorrect or malformed educational text inside artwork;
- changes Star, the teacher, or children between pages without an approved version change;
- includes decorative worksheet elements on a cover;
- uses a guessed book or page name;
- appears attractive but does not communicate the learning activity.

## Approval record

Each approved page should record:

- source commit;
- BPS version;
- manifest ID;
- template ID;
- asset IDs and checksums;
- QA score and critical-gate result;
- reviewer and approval date;
- output hashes.

## Production priority

The current production priority is the official Nursery portfolio from the repository. `Communication Champions` is the active reference book, but all other Nursery titles and their production order must be read from the canonical repository sources rather than recalled or inferred.
