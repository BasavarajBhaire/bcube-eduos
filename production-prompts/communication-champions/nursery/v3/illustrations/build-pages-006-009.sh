#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ART="$ROOT/artwork"
OUT="$ROOT/final"
LOGO="$ROOT/assets/BCube_Academy_approved_logo.png"
POPPINS="/tmp/bcube-fonts/Poppins-Bold.ttf"
NUNITO="/tmp/bcube-fonts/Nunito-SemiBold.ttf"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

make_caption() {
  local width="$1" height="$2" size="$3" colour="$4" font="$5" text="$6" out="$7"
  convert -background none -fill "$colour" -font "$font" -pointsize "$size" \
    -gravity center -size "$width"x"$height" "caption:$text" "$out"
}

build_page() {
  local id="$1" page="$2" title="$3" instruction="$4" response="$5" teacher="$6" home="$7"
  local source="$ART/$id-artwork.png"
  local target="$OUT/$id.png"

  convert "$source" -resize '2480x3508^' -gravity center -extent 2480x3508 "$TMP/base.png"
  make_caption 1780 230 126 '#1E4E8C' "$POPPINS" "$title" "$TMP/title.png"
  make_caption 2060 255 58 '#163A67' "$NUNITO" "$instruction" "$TMP/instruction.png"
  make_caption 1020 300 46 '#163A67' "$NUNITO" "Teacher: $teacher" "$TMP/teacher.png"
  make_caption 1020 300 46 '#245C31' "$NUNITO" "Home connection: $home" "$TMP/home.png"
  make_caption 1960 170 54 '#6B459B' "$POPPINS" "$response" "$TMP/response.png"
  make_caption 120 120 64 '#FFFFFF' "$POPPINS" "$page" "$TMP/page.png"

  convert "$TMP/base.png" \
    -fill 'rgba(255,255,255,0.96)' -stroke '#2BB3A3' -strokewidth 8 \
    -draw 'roundrectangle 35,30 2445,335 42,42' \
    -fill 'rgba(255,255,255,0.95)' -stroke '#F5C242' -strokewidth 7 \
    -draw 'roundrectangle 150,340 2330,625 38,38' \
    -fill 'rgba(255,255,255,0.96)' -stroke '#8E6CCF' -strokewidth 7 \
    -draw 'roundrectangle 210,2590 2270,2810 34,34' \
    -fill 'rgba(255,255,255,0.97)' -stroke '#1E4E8C' -strokewidth 8 \
    -draw 'roundrectangle 50,2870 1205,3350 38,38' \
    -fill 'rgba(255,255,255,0.97)' -stroke '#6CBF5F' -strokewidth 8 \
    -draw 'roundrectangle 1275,2870 2430,3350 38,38' \
    -fill '#1E4E8C' -stroke none -draw 'circle 2320,3400 2390,3400' \
    \( "$LOGO" -resize '250x205' \) -geometry +65+70 -composite \
    "$TMP/title.png" -geometry +420+70 -composite \
    "$TMP/instruction.png" -geometry +210+355 -composite \
    "$TMP/response.png" -geometry +260+2615 -composite \
    "$TMP/teacher.png" -geometry +115+2960 -composite \
    "$TMP/home.png" -geometry +1340+2960 -composite \
    "$TMP/page.png" -geometry +2260+3340 -composite \
    -alpha remove -alpha off -units PixelsPerInch -density 300 -colorspace sRGB "PNG24:$target"
}

build_page "CC-NURSERY-V3-P006" "6" "My Name" \
  "Say: My name is ________. Trace or write your name in the space." \
  "My name is ____________________." \
  "Point to the name space, model the sentence once, then invite the child to say their name." \
  "Say each family member’s name together and clap its syllables."

build_page "CC-NURSERY-V3-P007" "7" "My Photo" \
  "Paste your photo inside the frame. Point to it and say: This is me!" \
  "This is me!" \
  "Invite the child to point to the photo and say their name or the model phrase." \
  "Look at a family photo and name one familiar person together."

build_page "CC-NURSERY-V3-P008" "8" "My Feelings" \
  "Point to a feeling. Circle how you feel today. Tell a friend or teacher." \
  "I feel ____________________." \
  "Name the pictured feelings, model one choice, and accept a point, word, or short sentence." \
  "During a familiar routine, ask: How do you feel? Listen without correcting the feeling."

build_page "CC-NURSERY-V3-P009" "9" "My Birthday" \
  "How old are you? Circle your age from 1–5. Draw or colour the same number of candles." \
  "I am ______ years old." \
  "Count the first candle together, then let the child continue and say their age." \
  "Count birthday candles, steps, or safe household objects from 1 to 5."
