# Nursery Gold v5 Repository Normalization

This package establishes the official ten-book Nursery catalog, canonical 44-page architecture, prompt identifiers, migration rules, archive policy and release gates.

## Precedence

1. `books/catalog.json`
2. Official book metadata
3. Shared BCube Gold Publishing Standard v5.1
4. Book-specific production prompts
5. Historical development names and branch numbers

No feature branch may introduce a new Nursery title, alter the 44-page architecture or rename an official title without updating the catalog and passing normalization validation.
