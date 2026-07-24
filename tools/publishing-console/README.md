# BCube Publishing Console

Local browser interface for `scripts/bcube_publish.py`.

## Install

```bash
python -m pip install -r requirements.txt
```

## Start

```bash
python tools/publishing-console/app.py
```

Open `http://127.0.0.1:5050`.

The console:

- loads Nursery, LKG and UKG books from `bcube-publishing-sdk/books/cover-books.json`;
- loads all 44 finalized page records from each book's `production-prompts/<book>/<level>/v4/release-manifest.json`;
- reads the page-owned JSON package selected by the manifest;
- auto-fills the page ID, page type, printed number, title, objective, instruction, teacher guidance and parent partnership text;
- supports cover, front-matter, learning, assessment, certificate and back-cover pages without manual metadata entry;
- uploads a manual PNG/JPG/WEBP illustration;
- delegates rendering and QA to the existing publishing CLI;
- routes About This Book to its locked `BOOK_HEADER` composer instead of the lesson/activity composer;
- routes Publisher/Copyright to its illustration-free `MINIMAL_HEADER` composer;
- shows stdout and errors in the browser;
- can approve a page when a reviewer name is supplied.

The server binds only to localhost. Uploaded files are staged under `production-renders/v5/console-uploads`.

## Page-data workflow

The user selects only:

1. Level
2. Book
3. Physical page
4. Illustration, except for Publisher/Copyright where artwork is prohibited
5. Optional approval and reviewer

The browser shows the resolved metadata for verification, but does not submit editable copies of it. On publish, the server resolves the same physical page again from the finalized release manifest. Client-supplied titles, prompts, page IDs, or page types are not accepted as authoritative data.

The request fails closed if a manifest, page package, book identity, physical-page mapping, prompt ID, or required instructional field is missing or inconsistent.

About pages use the official logo, the book-title colour convention, `About This Book` as the secondary title, the uploaded book-specific illustration, six learning outcomes, five core pillars and the standard footer. They never show the series banner, age badge, visible page number, teacher panel, parent panel or Star mascot.

Publisher/Copyright pages require no uploaded illustration. The console hides the
illustration field and the instructional metadata panels for physical page 3.
The deterministic page contains the official logo, book identity, publisher
contact details, BCube Publication Code, Document ID, pre-print maturity label,
rights notice and print country. It never displays an ISBN unless one is
officially assigned.

Older finalized packages sometimes store a technical production paragraph in the instruction field or omit dedicated teacher/parent keys. The page-data adapter removes the technical wrapper for the visible instruction and applies the approved facilitation fallback when a dedicated key is absent. The exact original instruction remains available in the API response as `source_instruction`, alongside the repository source path.

## Validate

```bash
python -m unittest discover -s tools/publishing-console/tests -v
```

The suite verifies all 1,320 registered physical pages, server-side metadata resolution, hidden numbering, dedicated About and Publisher routing, optional approval, and rejection of client-supplied metadata overrides.
