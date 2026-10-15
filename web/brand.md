# Lansy brand rules for agents

Use these rules whenever you make anything that carries the Lansy brand: a page, a post, a slide, an image prompt. Values live in `tokens.json`, files in `assets/manifest.json`. If a rule here and a picture you saw disagree, the rule wins.

Status: version 2026-10-15. Colour, type, logo, icon, marker, blob, dots, 3D and the square post are settled. Proposals are marked as such.

## Hard rules

1. **Two greens only:** Primary Light `#9CDE45` and Primary Dark `#33694F`. Never use another green, a tint of these, or a gradient between them.
2. **Warm neutrals only:** everything else is a grey from the neutral scale below. Never use cool greys (`#8A8A8F`, `#E6E6E8`…), pure greys or black `#000000`.
3. **One typeface:** Struve for all text, in three weights only: 400, 500, 600. Never bold (700) or italic Struve. JetBrains Mono only for small uppercase labels. IBM Plex Sans Arabic only for Arabic. Supermarker Italic only for the marker phrase and the industry chip (see Marker).
4. **Logo files as they are:** take the logo and icon from `assets/`. Never redraw, recolour, stretch, rotate, outline, shadow or crop them, and never let an image model generate them.
5. **Minimum size:** the mark is at least 24px tall, alone or inside the full logo. For the full logo that means a box at least 27.2px tall: the mark is 120 of its 136 units, and the y descends below it.

## Colour

Neutrals share one warm temperature (OKLCH hue 85°, chroma 0.0086).

| Token | Hex | Use |
|---|---|---|
| ink | `#201F1D` | Text, dark buttons, logo on light |
| dark | `#2A2926` | Dark surfaces |
| text-2 | `#75736F` | Leads, secondary text (4.7:1 on white) |
| grey | `#8D8A86` | Mono labels only (3.4:1: never body text) |
| line | `#E9E6E0` | Rules, outlines |
| sand | `#F2EFE9` | Cards, plates |
| paper | `#FCF9F3` | Light surfaces |
| white | `#FFFFFF` | Page background |

Brand pair:

| Token | Hex | Text on it | Use |
|---|---|---|---|
| primary-light | `#9CDE45` | ink `#201F1D` | Lime fills: the main button, highlight plates, a live dot in the interface (never in the dotted pictures) |
| primary-dark | `#33694F` | white | Accent text on white or paper, dark plates |

Never put white text on lime, and never put lime text on white (1.6:1).

Surfaces are gradients, top to bottom:

- **Floor** (a whole section): sand → paper → white.
- **Card:** sand → paper. If the card holds a picture, the sand end sits next to the picture.

Proportions (proposal): the page is mostly white and warm greys. Lime is an accent, about one area per screen or post. Primary Dark is for text accents and the occasional dark plate.

## Type

| Style | Desktop | Phone | Weight | Line height | Tracking |
|---|---|---|---|---|---|
| h1 | 72 | 40 | 500 | 1.04 | −2.5% |
| h2 | 56 | 34 | 400 (phone 600) | 1.08 | −1.5% |
| manifesto | 46 | 24 | 400 | 1.18 | −1.5% |
| title | 24 | 24 | 600 | 1.25 | −1% |
| lead | 18 | 17 | 400, text-2 | 1.5 | 0 |
| body | 17 | 17 | 400–600 | 1.5 | 0 |
| small | 15 | 15 | 400–500 | 1.45 | 0 |
| label | 11–12 mono | 11–12 mono | 500, uppercase, grey | 1.6 | +6% |

- One h1 per page.
- Headings use sentence case, never all caps. Only labels are uppercase.
- Don't add sizes between the steps: pick the nearest one.
- A square post has its own two headline sizes: see Square post.

## Logo

- **Files:** use `logo-ink` on white, paper, sand, lime and the surface gradients. Use `logo-white` on Primary Dark, ink, dark and dark photos. Paths are in `assets/manifest.json`.
- **Mark alone:** use it where the full logo doesn't fit, or when the name "Lansy" is already written nearby.
- **Clear space** (proposal): half the mark's height on every side. Keep text and edges out of it.
- The word is always lowercase "lansy" inside the logo. In running text, write "Lansy".

## Icon

- **Flat** (`icon-flat`): an ink squircle with a white palm. Use it for favicons, avatars and interface icons.
- **3D** (`icon-3d`): the squircle in lime frosted glass with a porcelain palm, on transparency. Use it for promo, posts and close-ups. Rules for 3D are under **3D**.
- **The shape is a squircle** with continuous corners, not a rounded rectangle. When a frame or plate should echo the mark, use `assets/icon/squircle-ref.svg`.

## Marker

One phrase in a hand-written face inside a line of Struve. When the text carries the whole message, our line underlines it. Page: `marker.html`; examples: `assets/examples/marker-*.webp`.

### The marker

- **Face:** Supermarker Italic. It never stands alone; it always sits inside a line of Struve. One exception: the industry chip (below).
- **Same size, weight, tracking and baseline** as the Struve around it. Struve 400 takes Italic, 500 Medium Italic, 600 Bold Italic. Never scale it up.
- **One phrase per text,** one to three words, on the words that carry the meaning.
- **It shares its line with Struve:** never a whole line, never a line of its own. It may break across lines like any words.
- **Colour:** the text's colour, on every ground.
- **English only:** Supermarker has no Arabic glyphs. In Arabic, keep IBM Plex Sans Arabic and leave the marker out.
- **Display sizes only:** it is an accent for a headline or a quote. In a small line, a caption or a card's text it doesn't read: leave it out.
- **Words, not numbers:** figures stay in Struve; if anything, mark a word next to them.

### The industry chip

An industry's name in a white pill, in Supermarker Italic, after its Hugeicons line icon (stroke as heavy as the letters): Cafés, Retail, Clinics, Schools, Hotels. It labels a post or a card; one chip per layout, in a corner on the margin, or a row of all of them in their strip. The only place the marker face stands alone. Code: `labs/ui/badges.js`.

### The line under the marker

- **When:** the text carries the whole message (a quote, a number, a statement). Leave it out when a picture leads.
- **The tool:** the Underline path `assets/line/underline.svg`, drawn with the broad-nib pen (see Blob → the pen). Never a text underline, never a brush.
- **Build:** measure the phrase from its first letter to its last; stretch the path to that width plus 0.1 em on each side; centre it 0.14 em above the baseline; draw it 55–70% of the type size thick; put it behind the letters. A phrase that breaks gets a piece per line.
- **Colour:** `#9CDE45` on white, Floor and Card; `#FFFFFF` on Lime; no line on Primary Dark (the marker alone carries the accent there). The letters keep the text colour.

## Blob

A scribble drawn with our pen, filled with a place, with people coming out of it. Examples: `assets/examples/blob-*.webp`.

- **Shapes:** `assets/line/scribble-a.svg`, `scribble-b.svg`, `blob-1876.svg`. Each is a path; the blob is that path swept by the pen. New shapes come from the generator in `labs/line-lab.html` (variations of A and B): keep one by its seed and save its path.
- **The pen:** a broad nib shaped as a superellipse (n = 8), width 27% of the shape's height, thickness 0.12 of its width, held at 35°. Ends are cut square to the stroke, leaning up to 45° toward the pen angle. Path smoothing 0.5. Never use a generic brush, never draw it by hand, never let an image model make it.
- **People, two ways:** out of the blob (they stand inside and come up over its top edge, the neck entering at that edge; the blob cuts them only along its lower edge, nothing above it) or in front of it (cut by the bottom of the frame, never by the blob).
- **Never cut the top:** the whole head, hair included, stays in the frame and below the top margin. Only the bottom of a person is cut, by the blob or the frame.
- **Fill:** the other green (lime blob on Primary Dark, Primary Dark on Lime), never the ground's own; or a photo of the place where the talk happens (café for a barista, store, lobby), blurred by 0.5% of the post's width. Never sharp, never a place that doesn't match.
- **Size:** a big blob is 75–95% of the post's width; the person 60–75% of the post's height, so the face reads at feed size, in the upper half. Centre the person on the blob or shift them away from the text; the text sits on the opposite margin. Two people are in a conversation: turned to each other, close enough to touch, cut as one.
- **Layers:** ground, blob, headline, people. A head may cross the headline; the text never covers a face.
- **Small blobs:** 1.3–1.7× the type size, in a line like a word, on the baseline; people rise only into free space (above the text, or under the end of a shorter line), never over a word. One per line, two per post at most.
- One or two blobs per post. Never mirror a person.

## Dots

One small dot draws the technical side of the product: a voice, a day of talks, the Gulf on the globe. Page: `dots.html`; examples: `assets/examples/dots-*.webp`; live code: `labs/canvas.html`.

- **One signal per picture,** something people already read as data: a waveform on an arc (the voice line), a ring of bars (a day of talks), a dotted globe or map.
- **Simple forms only:** an arc, a sphere, a ring, a map. Never an icon or an object drawn in dots: thin lines fall apart. Use 3D for those.
- **Spatial:** every picture lies on a surface in space and is seen in perspective. Depth is shown by alpha only.
- **The dot:** 2.4 px at 1× (scale it with the layout), the same size in every picture; ~7 px apart along a line, ~9 px across a surface. Never bigger dots, accent dots, a second colour or shading.
- **Colour by the ground:** ink on white, Floor and Card (it reads grey through its alpha); white on Primary Dark; Primary Dark on Lime.
- **No fades or vignettes.** The picture stops at its own edge or the card's.
- **Motion:** still, or slow and steady: a globe turns once in two minutes, a ring in ninety seconds, a voice flickers like speech.
- **In a card:** text (a title, a line, a link, no marker) on one side; the picture on the other, running off the edge.

## 3D

Our icons as objects, in a few real materials, one studio light and one way of moving. Page: `3d.html`; files: `assets/3d/`; the Blender scripts: `3d/` in the repository.

- **Materials, one job each:** brushed aluminium (brushing 0.4) for the industry icons and coins; lime frosted glass, 80% transmission, for the Lansy squircle; porcelain for its palm; unglazed ceramic to try for calm surfaces. Free BlenderKit materials, applied as they are. Nothing else.
- **Lime is calibrated:** a lime render is measured and lands on `#9CDE45`.
- **Industry icons** are Hugeicons line icons (stroke 2.4 on the 24 grid) turned into round tubes; the same mesh stands alone or sits in relief on a coin. Never generate a logo or an icon with an image model, never redraw them.
- **Small sizes keep the flat icon:** in tabs and chips use the Hugeicons line icon with its stroke as heavy as the letters next to it.
- **One studio:** BlenderKit's material-preview light, the same for every render, so a material looks as on its preview.
- **Renders are on transparency,** laid on a flat brand ground (Lime, Primary Dark, Card, white). The object casts no shadow on the ground. A render faces left; to face it the other way, turn the scene in 3D, never flip the picture.
- **One way of moving:** the Lansy icon's own turn — a rest, one full turn about the vertical axis, a small overshoot, a settle (5 s at 30 fps; the curve is `3d/lansy_spin_curve.json`). The coin swirl is that turn, coin after coin round the ring (a 6 s loop). Every animation is built from this turn.
- **One 3D object per layout:** one icon, one coin, or the ring. The whole set of icons appears only in its strip.
- **No marker or blob inside a render:** the text and the blob stay on the page, around it.

## Square post

- Margin 6% on every side.
- Headline: Struve 500, leading 1.0, −2.5%, on the top or the bottom margin. Two sizes only: large, 15% of the square (162 px at 1080), when every line fits between the margins (88%, 950 px at 1080); otherwise regular, 11% (119 px). Regular may also be chosen on purpose, when the picture should lead. As many lines as the text needs; nothing in between the two sizes.
- Logo: box 5% of the square, on the edge opposite the headline; the site address `lansy.ai` (Struve 500, 3%) on its baseline, across.
- Info cards (quote, factoid) carry no logo. A factoid signs with the icon, at least 32 px, next to a mono source line.
- Grounds: Floor, Card, Lime, Primary Dark. Grey text (`#75736F`) only on Floor and Card; on Lime and Dark, secondary text keeps the text colour and differs by weight.
- Wide posts (2:1): margins and logo by the short side.

## For image models

When you write an image prompt:

- Attach the PNG from `assets/` as a reference for any logo or icon, and tell the model to keep it unchanged. Better: leave the space empty and place the logo yourself afterwards.
- Name colours by hex: "lime #9CDE45", "deep green #33694F", "warm off-white #FCF9F3". Avoid "neon green" or "mint".
- Ask for warm, soft daylight and warm greys. Avoid cool blue-grey grading.
