# BCube Publishing Web Console

Local browser interface for `scripts/bcube_publish.py`.

## Start

```bash
python -m pip install -r requirements.txt
python tools/publishing-console/app.py
```

Open `http://127.0.0.1:5050`.

## Features

- Loads Nursery, LKG and UKG books from `bcube-publishing-sdk/books/cover-books.json`.
- Supports cover and activity-backed page types.
- Generates the page ID from level, book and physical page.
- Uploads PNG, JPG or WEBP illustrations locally.
- Runs the existing BCube publishing CLI and shows stdout/stderr.
- Supports review-candidate generation and approved production output.

The console binds only to `127.0.0.1`. Uploaded files are stored under `production-renders/web-console/uploads`.
