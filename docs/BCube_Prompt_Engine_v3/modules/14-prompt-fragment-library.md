---
title: "Phase 14 - Prompt Fragment Library"
product: "BCube Prompt Engine v3.0"
edition: "Founder Edition"
version: "3.0.0"
status: "Active"
phase: "14"
owner: "BCube Future Academy"
last_updated: "2026-07-15"
source_documents:
  - BCube_Prompt_Engine_v3_Complete_Production_Standard_Phase_14_Prompt_Fragment_Library.docx
---

# Phase 14 - Prompt Fragment Library

> Normative status: This module is part of the BCube Prompt Engine v3.0 Complete Production Standard. `MUST`, `SHALL`, `SHOULD`, `MAY`, and `MUST NOT` carry their formal specification meanings.

Complete Production Standard Phase XIV – Prompt Fragment Library™

## Purpose

The Prompt Fragment Library™ is the reusable component catalog used by the Prompt Compiler™. Instead of authoring complete prompts from scratch, the compiler assembles validated fragments into a BCube Gold Production Prompt™.

## Publishing Fragments

- PF-PUB-001 Page Geometry

- PF-PUB-002 Safe Margins

- PF-PUB-003 Print Specification

- PF-PUB-004 Branding

## Design Fragments

- PF-DES-001 Grid System

- PF-DES-002 Typography

- PF-DES-003 Whitespace

- PF-DES-004 Layout Zones

## Educational Fragments

- PF-EDU-001 Learning Objective

- PF-EDU-002 Competency Mapping

- PF-EDU-003 Activity Design

- PF-EDU-004 Assessment Evidence

## Teaching Fragments

- PF-TEA-001 Teacher Facilitation

- PF-TEA-002 Question Prompts

- PF-TEA-003 Feedback

- PF-TEA-004 Observation

## Illustration Fragments

- PF-ILL-001 Rendering Style

- PF-ILL-002 Environment

- PF-ILL-003 Lighting

- PF-ILL-004 Props

## Character Fragments

- PF-CHR-001 Star Mascot

- PF-CHR-002 Teacher

- PF-CHR-003 Child

- PF-CHR-004 Parent

## Fragment Record Structure

| Field | Description | Required | Example | Owner |
| --- | --- | --- | --- | --- |
| Fragment ID | Unique reusable block | Yes | PF-ILL-001 | Illustration |
| Purpose | Function of fragment | Yes | Rendering Style | Engine |
| Inputs | Required metadata | Yes | Page type | Compiler |
| Outputs | Generated prompt text | Yes | Prompt block | Compiler |
| Version | Fragment revision | Yes | 3.0.0 | Governance |

## Assembly Principles

- Fragments are immutable once approved.

- The Prompt Compiler selects fragments based on metadata.

- Fragments may inherit global and book-level defaults.

- Fragments never override mandatory safety or QA rules.

- Every compiled prompt records fragment versions for traceability.

## Expansion Roadmap

Future editions will include hundreds of reusable prompt fragments with parameter definitions, placeholders, localization support, examples, anti-patterns, and machine-readable schemas.
