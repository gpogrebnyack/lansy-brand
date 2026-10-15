# 3D icon compositions from a line-icon set: research for Lansy rubrics

Date: 2026-10-12. Scope: composition (how the icon sits in 3D space), not material.

**Verification legend**
- **[seen]**: I opened the page and viewed the cover image in a browser. The date is the Dribbble post date.
- **[page]**: I read the page text but did not view the image.
- **[listed]**: the URL showed up in search results or a category listing. I did not inspect it.
- **[unverified]**: a claim I could not confirm.

---

## 1. Composition approaches

### A. Squircle slab with the icon on its face (app-icon sibling)
- **Build:** A squircle slab with continuous corners, about 15–25% as deep as it is wide, with a soft round bevel. The line icon is either raised as stroke tubes with round caps standing about 2–4% above the face, or inset as a shallow channel. Lansy's own icon is already built this way.
- **Why it works:** The slab is a fixed silhouette, so each icon only changes the glyph. Hugeicons strokes map directly to tubes (one radius, round caps).
- **Risks:** Rubric icons can look like separate apps and compete with the Lansy mark. On a lime slab, a white glyph loses contrast under strong highlights. At 32–48 px the raised relief disappears and the result reads as a flat tile.
- **References:**
  - Arman Gevorkian, "3D icons": four coloured squircle slabs in isometric view, each with a white glyph on its face. Aug 2026 [seen]. https://dribbble.com/shots/27657041-3D-icons
  - moein sheydaee, "Time Clock Icons, Glassmorphism Style": tilted squircle slabs with white line icons on the face, each tile at a slightly different tilt. Oct 2025 [seen]. https://dribbble.com/shots/26610392-Time-Clock-Icons-Glassmorphism-Style
  - Tornike Uchava, "S Monogram App Icon": a tilted squircle slab with a white extruded glyph, very close to the Lansy construction. Sep 2026 [seen]. https://dribbble.com/shots/27763064-S-Monogram-App-Icon
  - Icons8, "3D icons": a white squircle with a green extruded glyph. Feb 2024 [seen]. https://dribbble.com/shots/23567764-3D-icons
  - Odama, "Convocons Icon Concept": a series of squircle tiles with inset glyphs. Dec 2023 [seen]. https://dribbble.com/shots/23299961-Convocons-Icon-Concept
  - Yasir Eryilmaz, "Frame.io Big Sur app icon exploration": a line icon (sound wave) extruded as tubes on a white squircle. May 2021 [seen]. https://dribbble.com/shots/15678303-Frame-io-Big-Sur-app-icon-exploration
  - Leonid Skadniev, "App Logo Collection": squircle slabs with extruded glyphs [seen thumbnail]. https://www.behance.net/gallery/220515343/App-Logo-Collection-App-Logofolio

### B. Disc / coin / medallion
- **Build:** A round, shallow cylinder (depth about 10–15% of the diameter), often with a raised rim. The icon is embossed as tubes or a raised plateau inside the rim, or engraved into the face.
- **Why it works:** The circle is the most neutral silhouette, and any glyph centres well in it. A disc stays distinct from a squircle brand mark while sharing its build.
- **Risks:** It reads as gamification (achievements, crypto, medals). A raised rim adds a second ring of highlights that competes with a thin stroke. Wide icons, such as a bed for hotels, waste the circle's area.
- **References:**
  - mena, "Social Media Icons 3D Embossed": discs with a rim and embossed line icons in the centre. Aug 2024 [seen]. https://dribbble.com/shots/24770110-Social-Media-Icons-3d-Embossed
  - Ben Kókolas, "3D achievement badges" and "Football Achievement Badges": a badge series with embossed glyphs on a shared base. Mar 2024 and Feb 2025 [seen]. https://dribbble.com/shots/23844453-3D-achievement-badges · https://dribbble.com/shots/25552575-Football-Achievement-Badges
  - Hesam Sanei, "Flipping Coins". Feb 2022 [seen]. https://dribbble.com/shots/17558182-Flipping-Coins
  - Apple Activity awards, a 3D medal form in the Fitness app [page, secondary source]. https://9to5mac.com/2021/12/13/apple-watch-activity-awards/

### C. Free-standing extruded stroke (tube icon, no base)
- **Build:** Each stroke of the SVG becomes a tube with one radius and round caps. Fills become shallow pillowed slabs. The object stands on the floor or floats, with a contact shadow. In Blender: curve, then bevel depth, then convert to mesh. Strokes must be outlined or kept as open curves with caps.
- **Why it works:** It is the most literal 3D version of a Hugeicons stroke, carrying the brand's "line" language with no extra geometry.
- **Risks:** The silhouette is weak and airy, so it reads poorly on busy backgrounds and at small sizes. Visual mass varies a lot between icons (a coffee cup is dense, a scissors-like glyph is sparse). Thin tubes alias at 48 px. Each icon also needs a hand-set rotation so overlapping strokes do not merge.
- **References:**
  - Eugen Eşanu, "CLAY 3D Icon Set": monochrome glyphs extruded as clay objects, free-standing, one colour across the set. Mar 2026 [seen]. https://dribbble.com/shots/27039624-CLAY-3D-Icon-Set
  - J. Pavel, "Basket 3D glass icon": a cart line icon extruded as tubes, floating over a frosted glass squircle (a hybrid of C and F). Dec 2024 [seen]. https://dribbble.com/shots/25392227-Basket-3D-glass-icon
  - Streamline, "Frosted neon icons in FLEX": a 2D line set rendered as a glowing stroke behind a frosted tile, showing that a line library can carry a "lit tube" style. Nov 2024 [seen]. https://dribbble.com/shots/25224891-Frosted-neon-icons-in-FLEX-Photography
  - Workflow: BlenderNation, "GeoNodes: Bevel Engraved SVG Logos", 2024 [listed]. https://www.blendernation.com/2024/09/12/geonodes-bevel-engraved-svg-logos/
  - I found no strong 2025–26 series of pure white stroke tubes without a base. That gap is an opening for Lansy.

### D. Stacked plates / exploded layers
- **Build:** A base slab, then one or two thin plates (glass or solid), then the icon on the top layer. The layers are separated in Z by a small gap, which closes on hover or tap. This is the native model for Apple icons: a background plus one or two foreground layers, with the system adding depth, shadows and specular light.
- **Why it works:** The line icon becomes the top layer, so no new modelling is needed per icon. It animates well, with layers parting and closing, and matches the Liquid Glass era.
- **Risks:** It looks busy at small sizes, and multiple translucent layers turn lime muddy. Gaps must be identical across the set. Apple's guidance favours simple shapes and avoiding "extremely thin line weights" in layered icons.
- **References:**
  - Vibhansh Alok, "Glass App Icon, Layer-by-Layer Construct": an exploded squircle with stacked layers. Oct 2026 [seen]. https://dribbble.com/shots/27765190-Glass-App-Icon-Layer-by-Layer-Construct-Computer
  - Alla Medvedieva, "Liquid Glass Icons in Icon Composer": glass squircles with white line icons as the foreground layer. Jul 2025 [seen]. https://dribbble.com/shots/26255800-Liquid-Glass-Icons-in-Icon-Composer
  - Apple HIG, App icons: the layer model, visionOS "background layer and one or two layers on top", and light and highlights handled by the system [page]. https://developer.apple.com/design/human-interface-guidelines/app-icons
  - Apple Icon Composer: per-layer specular, refraction and translucency, and a "vertical light angle shines from above" [page]. https://developer.apple.com/icon-composer/

### E. Glass card with the icon behind or inside
- **Build:** A frosted squircle or plate in front, with a coloured tube icon (or a blob plus icon) behind it, blurred through the glass. In a variant, the icon sits on the glass plate.
- **Why it works:** The glass hides small stroke differences between icons, which helps consistency. It feels current.
- **Risks:** Saturated in 2021–26, so it is generic. Blur kills a thin stroke. Glass needs a dark or colourful backdrop to read, and Lansy's off-white pages flatten it. It is heavy to render and to deliver for the web.
- **References:**
  - Heli Studio, "Continuing the 3D Icon System, HOP VPN": soft frosted objects. May 2026 [seen]. https://dribbble.com/shots/27361295-Continuing-the-3D-Icon-System-HOP-VPN
  - Dmitrii Mikhailov, "3D Frosted Glass Icon Design": a coloured shape behind a frosted shape on a white tile. Feb 2026 [seen]. https://dribbble.com/shots/27053356-3D-Frosted-Glass-Icon-Design
  - BigLoong, "3D Frosted Glass Texture Icon": stacked glass plates with glyphs. Aug 2024 [seen]. https://dribbble.com/shots/24643939-3D-Frosted-Glass-Texture-Icon
  - Hesam Sanei, "Stack Glass Icons". Feb 2023 [seen]. https://dribbble.com/shots/20758758-Stack-Glass-Icons
  - Figma Community, "Free 400+ 3D Glass Icons" (opaque "liquid glass"), late 2025 [page]. https://www.figma.com/community/file/1564238050974308122/free-400-3d-glass-icons

### F. Inflated / puffy form
- **Build:** The glyph's outline is inflated into a cushion, or a puffy squircle cushion has the icon debossed or stitched into it. In Illustrator: 3D Inflate. In Blender: a cloth/pressure sim, or remesh plus smooth.
- **Why it works:** It is soft and tactile, a natural fit for a "clay / soft plastic" brand.
- **Risks:** Thin line icons inflate into blobs, so it suits filled glyphs better than strokes. It reads as childish or Y2K. Silhouettes drift between icons.
- **References:**
  - Zulfa Mahendra, "Fluffy 3D Icons": a monochrome puffy set. Oct 2024 [seen]. https://dribbble.com/shots/24985360-Fluffy-3D-Icons
  - Kirk Wallace, "Inflated Icons". Dec 2022 [seen]. https://dribbble.com/shots/20080355-Inflated-Icons
  - Kevin Moran, "Balloon Icons" (Skillshare class). Sep 2024 [seen]. https://dribbble.com/shots/24839284--Balloon-Icons-NEW-Skillshare-Class

### G. Icon on a pedestal / plinth / mini-ground
- **Build:** A low cylinder or disk under a free-standing icon (approach C), sometimes glowing or with a tiny terrain base.
- **Why it works:** The plinth gives sparse tube icons a shared visual mass and a consistent baseline.
- **Risks:** It looks like e-commerce or crypto product shots. It adds height, which makes a row of icons look tall and busy, and it dates quickly.
- **References:**
  - EGO Creative Innovations, "3D Icons": glyphs on glowing disc bases. Apr 2024 [seen]. https://dribbble.com/shots/23781954-3D-Icons
  - Hana Youssef, "Orbit, Space Exploration Icon Set": objects on small ground bases. Sep 2026 [seen]. https://dribbble.com/shots/27763882-Orbit-Space-Exploration-Icon-Set
  - Dribbble tag "3d_podium" [listed]. https://dribbble.com/tags/3d_podium

### H. Object icon / mini-scene (pictogram becomes a real object, plus a secondary prop)
- **Build:** The subject is modelled as a stylised object (a cup, a bell, a tiny massage table), sometimes with a small second object or scene. No base, and one shared camera angle.
- **Why it works:** Highest recognition and warmth. This is the current big-brand direction (Airbnb 2025).
- **Risks:** It is no longer derived from Hugeicons, because each icon is a bespoke model. Consistency rests entirely on style rules. Cost is high, and AI-generated imitations flood this look.
- **References:**
  - Airbnb 2025 redesign: in-house 3D iconography, "slowly built up over the last couple of years" [page]. https://www.itsnicethat.com/articles/airbnb-app-redesign-140525
  - Airbnb Newsroom product releases [listed]. https://news.airbnb.com/product-releases/
  - Shanks, "Airbnb-Style 3D Icons". Jun 2025 [seen]. https://dribbble.com/shots/26160199-Airbnb-Style-3D-Icons
  - Microsoft Fluent Emoji: one source offered as 3D, Color, Flat and High Contrast assets, under an MIT licence (checked via the GitHub API). https://github.com/microsoft/fluentui-emoji
  - 3dicons (Vijay Verma, CC0): free-standing objects in 3 fixed angles and 4 colour styles [page]. https://3dicons.co · case study: https://www.smashingmagazine.com/2022/05/3dicons-open-source-library-case-study-download/

### I. Pill / capsule badge (icon + label)
- **Build:** A horizontal capsule slab with the icon on the left (raised tubes) and the rubric name as a debossed label, or the label kept as live HTML next to it.
- **Why it works:** It is a UI-native format for chips and filters, and it reuses the squircle build stretched into a capsule.
- **Risks:** Text in 3D cannot be localised (Apple HIG advises against text in icons). It is a UI element rather than an icon.
- **References:** I found no strong verified 3D icon series in this format. Apple HIG's note on text is [page] (see D). Treat this as derived from A, not a primary composition.

### J. Icon breaking out of the frame
- **Build:** The icon starts inside a squircle or frame and part of it (steam, a handle) pokes out past the edge or the front plane.
- **Why it works:** Adds energy, and works well for hero moments.
- **Risks:** Each icon needs a bespoke breakout, so the set loses its rhythm. Breakouts also crop badly in grids.
- **References:** I found no verified 2023–26 icon series. Apple warns that tvOS and visionOS crop foreground layers more than the background [page, HIG]. **[unverified as a series pattern]**

---

## 2. Where trends are heading (2025 → 2026)
- **Layered, system-lit icons.** Apple Liquid Glass and Icon Composer (2025) make icons a stack of layers lit from above, with depth effects added by the system. Many 2025–26 Dribbble icons are layered glass squircles: NotePlan, Safari, Majik, Mirano and Layer-by-Layer.
  - https://dribbble.com/shots/26703329-NotePlan-Liquid-Glass-App-Icon
  - https://dribbble.com/shots/27768564-Mirano-Liquid-Glass-App-Icon
- **Soft and matte rather than glossy.** Airbnb's 2025 icons pushed a tactile clay, softly lit look, and commentary calls it a shift toward "texture and form". Single-colour clay sets show the same move (Eşanu 2026, Mahendra 2024).
- **Motion as part of the icon.** Airbnb's animated icons and "breathing" app icons point the same way. One example: George MadeToBeTapped, "Alpina", Oct 2026 [seen]. https://dribbble.com/shots/27776055-Alpina-3D-Skier-App-Icon-with-Breathing-Animation
- **AI saturation.** Free "glass" and "Airbnb-style" packs are now often AI-generated, for example Spacekayak's 16-icon pack (Figma Community [page]). What sets a set apart now is strict system rules (one build, one camera) and brand-specific geometry, not the material.
- **Monochrome, brand-colour sets.** One material and one colour per set (Eşanu, Mahendra) is more common than rainbow sets. That fits a lime/green brand.

---

## 3. Recommendations for Lansy (ranked)

Aim: the rubric icons should be siblings of the lime squircle palm icon, not clones of it.

1. **Squircle slab in a neutral or deep-green colour, with a raised Hugeicons stroke (A).**
   - Same slab profile, bevel, tube radius and camera as the Lansy icon.
   - Change the slab colour so the brand icon stays the only lime one:
     - Off-white slab (#F2EFE9) with a lime icon (#9CDE45), or
     - Deep green slab (#33694F) with a white icon.
   - This gives the strongest family resemblance at the lowest per-icon cost, since only the glyph changes.
2. **Disc slab (B), same build as the Lansy icon.**
   - The circle against the squircle marks the hierarchy: the brand is a squircle, a rubric is a disc.
   - Keep it rimless (the Lansy face is flat) so it does not drift into medals or gamification.
3. **Free-standing white tube icon with no base (C), casting a soft contact shadow.**
   - This is the "the palm left the slab" idea: the same white extrusion as the palm, standing alone.
   - It is the lightest option on off-white pages and still rare as a series.
   - Needs mass balancing: tweak the tube radius or add a small fill to sparse glyphs.
4. **Two-layer exploded squircle (D).**
   - The lime or neutral slab sits below, and the icon floats a few mm above it on its own thin plate or with no plate.
   - Use it for hero and hover states: the layers part on hover and settle into option 1 at rest. That gives one asset family with two states.
5. **Rubric icon plus a small "conversation" accent (modifier on 1 or 2).**
   - A small lime speech-bubble or waveform chip on the slab's corner.
   - Ties every rubric to Lansy's job (analysing conversations), and it is the same prop on every icon, so consistency is free.
   - Optional. Test whether it clutters at small size.
6. **Puffy squircle cushion with a debossed icon (F)**, as a softer alternative only if the clay feel needs to be pushed. It is lower priority because inflated forms smear thin strokes.

**Not recommended for this set:**
- **Pedestal (G):** product-shot feel, too much height.
- **Breaking out of the frame (J):** bespoke per icon.
- **Glass card (E):** generic, and weak on off-white.
- **Object/mini-scene (H):** leaves Hugeicons behind. Revisit only if budget allows bespoke modelling.
- **Pill (I):** better as an HTML chip with a 2D icon.

---

## 4. Consistency rules (camera, light, geometry)
- **One master scene.** Duplicate the Lansy icon's scene and swap only the glyph and colour. 3dicons used shared camera and light rigs per angle plus a two-cube bounding guide for size and position. https://www.smashingmagazine.com/2022/05/3dicons-open-source-library-case-study-download/
- **Camera.**
  - Copy the Lansy icon's yaw and pitch exactly. All rubric icons use the same angle; do not vary the tilt per icon.
  - Use a long lens (about 85–135 mm equivalent) or near-orthographic, so the slab edges stay parallel and the set tiles cleanly in a row.
  - Optional: one "front" variant for small sizes. 3dicons ships Front, Dynamic and ISO.
- **Light.**
  - The key light comes from above and slightly to the front-left, matching Apple's "light from above" convention.
  - Use a large soft area light, a weak fill, and a thin rim light to separate the white tubes from the slab.
  - Use one HDRI and a fixed exposure.
  - Keep the same contact shadow for every icon: same softness, same offset, no coloured bounce that varies by icon.
- **Glyph geometry.**
  - Take all icons from one Hugeicons style (Stroke Rounded) at the same 24 px grid. Do not resize individual SVGs.
  - Convert at a single world-space tube radius, with round caps and joins.
  - Keep relief height and bevel identical.
  - The glyph fills about 55–65% of the slab face. Optically correct dense or sparse icons by small scale nudges (±5%), not by changing stroke radius.
- **Material.** One roughness and subsurface preset each for the slab and for the glyph. Colour is the only variable.
- **Small sizes.**
  - Below about 64 px, use a 2D export (a flat render or the Hugeicons SVG on a coloured squircle). 3D relief and bevels drop below a pixel.
  - Apple advises against "extremely thin line weights" at small icon sizes. Consider a slightly heavier stroke for 3D (about 2 px equivalent instead of 1.5) and check it [unverified: the Hugeicons default stroke weight].
- **QA.** Lay all 7 renders in one row, on both #FCF9F3 and #201F1D. Check that the silhouettes, baselines and shadow weights match before final render.

## 5. Tooling notes
- Spline's own guidance: define proportions, corner radii, palette and material first, then use one shared material set and one lighting setup for all icons. https://spline.design/solutions/3d-icons
- Converting SVG to 3D in Blender: import the SVG as a curve, set extrude and bevel depth, then convert to mesh. The paid "Vector to 3D" add-on automates this [listed]. https://superhivemarket.com/products/vector-to-3d
