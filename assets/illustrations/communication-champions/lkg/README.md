# Communication Champions — LKG approved illustration sheets

Place one approved PNG asset sheet per learning page in this folder:

`CC-LKG-V4-P008.png` through `CC-LKG-V4-P043.png`.

Use the matching illustration-only prompt files in:

`production-prompts/communication-champions/lkg/v4/phase2-illustration-prompts/pages/`

The asset sheet filenames and internal extraction order are locked by:

`production-prompts/communication-champions/lkg/v4/phase2-illustration-prompts.json`

Render the full learning-page scope with:

```powershell
python scripts/render_communication_champions_full_book.py `
  --logo "BCube_Gold_Production_v4/approved-assets/brand/Thumbnail_BCube_Academy_logo.png" `
  --illustrations-dir "assets/illustrations/communication-champions/lkg" `
  --output-dir "Communication-Champions-P008-P043-verified-PNGs" `
  --evidence-dir "Communication-Champions-P008-P043-verified-evidence"
```

The renderer fails clearly when a required page sheet is missing. It never substitutes generic artwork.
