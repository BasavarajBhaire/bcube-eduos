# Early Maths Adventures LKG — Wave 1 refinement checklist

Scope: `EM-LKG-V4-P009` through `EM-LKG-V4-P019`.

## Contract rules

- One exact page contract per page ID.
- No generic response controls.
- No Parent Panel or Home Connection.
- `allow_fallback` remains false.
- Every response count comes from `activity.mechanics`.
- Every named asset must have one named crop.
- The renderer uses contain-fit only.

## Page acceptance checks

### P009 Numbers 11–20
- Five cards are not forced into five narrow columns.
- Each full set remains visible.
- Choices are exactly quantity minus one, quantity, quantity plus one.

### P010 Count & Match
- Four quantity groups appear on the left.
- Four numeral assets appear on the right in deranged order.
- Match dots are aligned and no answer line is pre-drawn.

### P011 Count & Circle
- Six count cards.
- Three numeral choices beneath each card.
- No cropped object groups.

### P012 More or Less
- Each row contains one left and one right group.
- Each row visibly says `Circle more.` or `Circle less.`
- One response target per pair.

### P013 Equal Groups
- Each row contains one pair.
- Visible `YES` and `NO` choices replace unexplained circles.

### P014 Missing Numbers
- Exactly one write slot per sequence.
- No three generic boxes on the right.

### P015 Join Groups
- Two groups, plus sign, equals sign and three total choices per problem.

### P016 Take Away
- Starting set remains intact in the artwork.
- The child crosses out the separated taken-away objects.
- Three remaining-number choices appear.

### P017 Before & After
- Exactly two response slots per row.
- No extra choice boxes.

### P018 Number Order
- Response slot count matches token count: 3, 4 and 4.

### P019 Number Line
- Start point, jump arcs and landing choices are visible.
- Number line artwork remains unobstructed.

## Test command

```bash
python scripts/render_book_from_illustrations.py \
  --level lkg \
  --book early-maths-adventures \
  --illustrations-dir "D:\BCube\Books_desing\Best_designed\Learning_Illustration\LKG\Early Maths Adventures" \
  --logo "D:\BCube\Brand\BCube_Logo.png" \
  --output-dir "D:\BCube\Books\Early Maths Adventures\completed-pages" \
  --evidence-dir "D:\BCube\Books\Early Maths Adventures\evidence"
```

Wave 1 is accepted only when all available P009–P019 pages render with zero failures and satisfy the checks above.
