# BCube Gold Production Prompt™ — Final Compiled Template

Status: Active  
Version: 3.0.0  
Owner: Prompt Compiler™

## Purpose

This template defines the only prompt form permitted for image generation. The compiler may use modular rules, fragments, schemas and templates internally, but the emitted prompt MUST be fully expanded, page-specific and understandable without access to the repository.

## Required compiled sections

1. **Compiler metadata**
   - Prompt ID
   - Book ID and version
   - Page number and exact page title
   - Target level and age
   - Template ID
   - Engine versions

2. **Technical and publishing specification**
   - Exact trim size and orientation
   - Resolution and print requirements
   - Bleed, safe area and binding margin
   - Logo, title and page-number positions
   - Background, contrast and whitespace rules

3. **Educational specification**
   - One primary learning objective
   - Competency and expected child outcome
   - Activity evidence and success indicator
   - Developmental constraints

4. **Exact page content**
   - Exact visible title
   - Exact child-facing instruction
   - Exact teacher prompt
   - Exact parent prompt when present
   - Exact labels and speech text when present

5. **Page-specific illustration direction**
   - Main scene and focal point
   - Character identities, actions, expressions and placement
   - Teacher–child interaction
   - Star mascot action and purpose
   - Required objects, environment and composition
   - Protected child activity area

6. **Character continuity block**
   - Complete Star mascot appearance
   - Complete teacher and child requirements
   - Diversity, anatomy and safe-behaviour constraints

7. **Visual grammar block**
   - Primary and secondary focal points
   - Eye-flow sequence
   - Visual-to-text ratio
   - Cognitive-load and clutter limits

8. **Negative constraints**
   - No watermarks or unrelated logos
   - No gibberish or unintended text
   - No distorted anatomy or extra limbs/fingers
   - No cropped faces, hands, learning objects or activity areas
   - No photorealism, dark background or decorative clutter
   - No unresolved variables, rule IDs or repository references

9. **Final validation declaration**
   - Self-contained prompt check passed
   - Exact-text check passed
   - Page-specificity check passed
   - Publishing, educational, illustration, character and safety checks passed

## Prohibited output

A final prompt MUST NOT contain statements such as:

- “Use the common publishing module.”
- “Apply CE-STR-001.”
- “Follow the attached character bible.”
- “Use the same teacher as before.”
- “Insert page-specific content here.”
- `{{placeholder}}`, `${variable}`, `<TBD>` or equivalent unresolved markers.

## Compilation rule

The Prompt Compiler™ SHALL inline the full meaning of every selected rule and fragment. Repetition inside the compiled prompt is intentional when required for reliable image generation.