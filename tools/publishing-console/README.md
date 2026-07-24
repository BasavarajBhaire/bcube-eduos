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
- generates page IDs automatically;
- supports cover, front-matter, learning, assessment, certificate and back-cover selections;
- uploads a manual PNG/JPG/WEBP illustration;
- delegates rendering and QA to the existing publishing CLI;
- shows stdout and errors in the browser;
- can approve a page when a reviewer name is supplied.

The server binds only to localhost. Uploaded files are staged under `production-renders/v5/console-uploads`.
