# Approved Image Assets

This directory contains only immutable, reviewed production assets that are required to reproduce a release.

## Structure

```text
approved-assets/
├── brand/
│   ├── asset-lock.json
│   ├── logos/
│   └── mascots/
└── <level>/
    └── <book-slug>/
        ├── asset-lock.json
        ├── illustrations/
        ├── pages/
        └── qa/
```

## Admission rule

An image may be committed here only when:

1. it has completed semantic and visual QA;
2. it has zero critical defects and a score of at least 95;
3. its QA record identifies the exact SHA-256 of the file;
4. it was explicitly promoted by `scripts/promote-approved-page.py`;
5. its asset-lock entry is `approved`.

Candidates, rejected pages, previews, contact sheets, PDFs and ZIPs belong outside this directory and are ignored by Git.
