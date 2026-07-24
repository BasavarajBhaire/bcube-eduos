# BCube Publishing Web Console

Local browser interface for `scripts/bcube_publish.py`.

## Install

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m pip install -r tools/publishing-console/requirements.txt
```

## Run

```bash
python tools/publishing-console/app.py
```

Open `http://127.0.0.1:5050`.

## Features

- Loads Nursery, LKG, and UKG books from `bcube-publishing-sdk/books/cover-books.json`.
- Supports Cover, About, Copyright, Contents, Welcome, Meet Star, Module Intro, Learning, Assessment, Certificate, and Back Cover selections.
- Maps Cover to `--page cover` and every other type to `--page activity`.
- Uploads and validates a manual illustration through the existing publishing CLI.
- Automatically derives the page ID when left blank.
- Captures the exact command, stdout, and stderr in the browser.
- Supports the existing approval and reviewer flags.

## Important

The console runs only on `127.0.0.1` and is intended as a local production tool. It does not replace the CLI or change the page-composition rules. Non-cover page categories still use the current activity pipeline underneath.
