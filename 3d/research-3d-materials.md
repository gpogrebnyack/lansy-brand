# 3D brand icons for Lansy: materials research

Date: 2026-10-12. Target: Blender (Cycles), 4.x–5.x. Current manual: Blender 5.2 LTS.
Legend: **[V]** URL opened/checked by me. **[S]** found via search, page blocks bots (Dribbble/Behance), content seen only as a search snippet. **[U]** claim not verified.

---

## 1. Trending looks, 2024–2026

| Look | Status | Fit for Lansy | References |
|---|---|---|---|
| **Soft clay / soft-touch matte plastic** | Main "soft 3D" look in app and SaaS work: rounded, tactile, low realism | **Core.** Already the app-icon language | Icons8 clay pack [S] https://dribbble.com/shots/25816127-Playful-3D-icon-set-made-of-clay · Dribbble "3D Clay" feed [S] https://dribbble.com/search/3D-Clay · Mathias Millioud, Blender/Cycles icon [S] https://dribbble.com/shots/16527528-Account-3D-icon-in-Blender · trend write-up [V] https://www.manypixels.co/blog/post/the-key-trends-in-icon-design-in-2022 · puffy/foam/rubber/glossy plastic as a 2026 3D trend [V] https://garagefarm.net/blog/trends-in-3d-art |
| **Frosted / liquid glass** | Boosted by Apple Liquid Glass (WWDC, 9 June 2025) | **High.** Neutral "special" material, picks up the colour of what sits behind it | Apple newsroom [V] https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/ · Icons8 "Liquid Glass Icons", Blender, Nov 2025 [S] https://www.behance.net/gallery/237108261/Liquid-Glass-Icons · "3D Frosted Glass icon – Blender" (sathyasanto) [V] https://dribbble.com/sathyasanto/shots · Liquid Glass as a UI trend [V] https://pixso.net/articles/7-ui-ux-design-trends/ |
| **Glossy candy plastic (clear coat)** | Steady, common in free/paid icon packs | Medium. Good alternative to soft-touch | assetpro "3D Glossy Icons" [S] https://dribbble.com/shots/25193596-Design-assets-3D-Glossy-Icons · "Plastic 3d icons pack" free [S] https://www.behance.net/gallery/168322429/Plastic-3d-icons-pack-for-FREE-30pcs · plastic-style studio [V] https://dribbble.com/plastic3dicons |
| **Jelly / subsurface translucency** | Niche, playful | Low–medium. Accent only; reads poorly at small sizes | Dribbble "subsurface" tag [S] https://dribbble.com/tags/subsurface |
| **Chrome / liquid metal** | Back in 2026 branding (chrome type, embossed badges) | Medium. As a rim or icon on a matte base, not everywhere | 2026 trends (chrome) [V] https://picsart.com/blog/design-trends-2026/ · Fabrizio Boni, glossy/iridescent Blender icons [V] https://dribbble.com/FabrizioBoni/shots |
| **Iridescent / holographic / thin film** | Niche; Cycles has supported it natively since 4.2 | Low. One accent detail per series at most | Dribbble "iridescent" tag [S] https://dribbble.com/tags/iridescent · Blender 4.2 thin film [V] https://developer.blender.org/docs/release_notes/4.2/cycles/ |
| **Brushed / bead-blasted aluminium** | Classic "product" look (Apple hardware) | Medium–high. Neutral base disc or rim | — (product-photography convention, no single source) |
| **Ceramic, felt/fabric, rubber** | Part of the "tactile" trend | Felt/fabric works as ground; rubber in ink #201F1D as a dark icon variant | garagefarm (fuzzy, foam, rubber) [V] link above |
| **Hybrid 2D/3D, painterly 3D** | Strong 2026 signal | Out of scope for this series | Creative Bloq, 2026 3D trends [V URL, body not read] https://creativebloq.com/3d/the-critical-3d-art-trends-that-will-impact-2026 |

Free reference sets in the same genre:
- **3dicons.co** by Vijay Verma: CC0, hand-made 3D icons [V] https://3dicons.co/. Which material styles it offers is **[U]**.
- **Microsoft Fluent Emoji**, which includes a soft 3D style [V repo] https://github.com/microsoft/fluentui-emoji.

Takeaway: soft-touch/clay (brand) plus frosted glass and metal (neutral) is the current mainstream. Iridescence and jelly are accents only.

---

## 2. Free material sources

| Source | What fits | Licence | Import | URLs |
|---|---|---|---|---|
| **Poly Haven** | **HDRIs (the main value here).** 96 studio HDRIs. Textures are mostly scanned and weathered, so they don't suit clean icons. Possible exceptions: `plaster_grey_04` and `white_plaster_02` for a ground. | **CC0**, no attribution [V] | Download .hdr/.exr → World ▸ Environment Texture. The asset-browser add-on is **paid** (Superhive or Patreon $5) | https://polyhaven.com/license · https://polyhaven.com/hdris/studio · add-on https://github.com/Poly-Haven/polyhavenassets |
| **ambientCG** | `Plastic010` (smooth white), `Plastic017A` (green), `Metal051A/B/C` (**circular brushed aluminium**, ideal for a disc), `Metal009` (brushed steel), `Fabric015`, `PaintedPlaster017`, `Rubber001–004` | **CC0**, no attribution [V] | ZIP of maps (1K–8K, JPG/PNG) → Node Wrangler `Ctrl+Shift+T` builds the Principled setup. Blender library only via Patreon [U] | https://docs.ambientcg.com/license/ · https://ambientcg.com/view?id=Metal051A · https://ambientcg.com/view?id=Plastic010 · https://ambientcg.com/view?id=Plastic017A · https://ambientcg.com/view?id=Metal009 |
| **Blendkit** (formerly BlenderKit; renamed June 2026) | Many procedural materials. The pricing page lists **42,019 materials in both Free and Full plans**, so materials are effectively free | **Royalty Free** (commercial use, no attribution, no reselling the asset itself) or **CC0** per asset [V] | Blendkit add-on (Blender 3.0+), drag-and-drop onto an object. Website "Get this" gives a code for the add-on | https://www.blendkit.com/docs/licenses/ · https://www.blendkit.com/plans/pricing/ · https://www.blenderkit.com/articles/goodbye-blenderkit-hello-blendkit/ |
| **Community Material Pack** (Curtis Holt) | Procedural clay (Mel) and a metallic shader | **CC0** [V] | .blend, append | https://curtisjamesholt.gumroad.com/l/community_material_pack |
| **Simple Material Pack** (heypictures) | Basic glass (incl. white+rough), emission | Free tier, Gumroad terms [U] | .blend, Blender 3.0+ | https://heypictures.gumroad.com/l/zwhai |
| **Free Glass shader** (cgandwe) | Glass setup | Gumroad terms [U] | .blend | https://cgandwe.gumroad.com/l/Free_Glass_shader |
| **Superhive free** | ZenShaders Free Library; Advanced Car Paint (flakes plus coat, a candy look); Claymate (one-click clay override for previews) | Superhive product licence [U] | Add-on / .blend | https://superhivemarket.com/products/zenshaders-free-library · https://superhivemarket.com/products/advanced-car-paint-shader-fully-procedural · https://superhivemarket.com/products/claymate |
| **Blender Essentials library** | In 4.x it holds hair node groups and brushes. No material library found | GPL/CC0 [U] | Built into the Asset Browser | https://docs.blender.org/manual/en/latest/files/asset_libraries/introduction.html |
| **Adobe Substance** | .sbsar via the free Substance 3D add-on for Blender (2.0 for Blender 4.0) | Asset licence per Adobe terms [U] | Add-on, needs an Adobe account | https://substance3d.adobe.com/plugins/substance-in-blender/ (bot-blocked) [S] |
| **Sketchfab** | Models only; no proper material library | Per model | — | Not recommended for this task |

### Blendkit picks (all free; all checked [V])

| Look | Material | URL |
|---|---|---|
| Soft-touch / matte plastic | Rough Plastic (623 bookmarks) | https://www.blendkit.com/get-blendkit/eebebd07-b10e-4fa5-ab28-347883b83f68/ |
| | Electronic matte plastic | https://www.blendkit.com/get-blendkit/afeb7064-3901-4cc9-b1f6-755306ba262b/ |
| Clay | Diffused Clay | https://www.blendkit.com/get-blendkit/02e458cd-365f-47c9-855e-fb64371d2c83/ |
| Glossy plastic | Glossy Plastic (985 bookmarks) | https://www.blendkit.com/get-blendkit/00e214e9-9523-419d-888b-b0cc2cbe9497/ |
| Frosted glass | Frosted Glass 02 | https://www.blendkit.com/get-blendkit/2232afbc-29ef-414a-973d-e2770e276f73/ |
| | Azure Frost Glass | https://www.blendkit.com/get-blendkit/e8f42016-3948-48f4-add5-2bd555cf14da/ |
| | Procedural Frosted Glass | https://www.blendkit.com/get-blendkit/2a0813c9-b18c-4977-a3b2-61ae51f87996/ |
| | Frosted Acrylic | https://www.blendkit.com/get-blendkit/fed64bd3-b791-4a92-9095-84335a9b77ac/ |
| Iridescent | Procedural Iridescent plastic (1,538 bookmarks) | https://www.blendkit.com/get-blendkit/b160c63e-6c3d-4745-a0c1-a4e6672baad5/ |
| | Iridescent Gradient Glass | https://www.blendkit.com/get-blendkit/df7e9828-51b2-4c81-b011-3bfcfc92a4ce/ |
| | Procedural Iridescent Shader | https://www.blendkit.com/get-blendkit/c4e02544-820e-44f3-aee7-9c4355f17e72/ |
| Chrome | Car chrome (1,038 bookmarks) | https://www.blendkit.com/get-blendkit/7648d7d0-164b-4e44-9228-1bd0f6f8fc53/ |
| Brushed aluminium | Brushed Aluminum 2 (900 bookmarks) | https://www.blendkit.com/get-blendkit/84aa9a79-50e4-471c-bf48-5c3d3ec17437/ |
| | Brushed Aluminium (CC0) | https://www.blendkit.com/get-blendkit/d9adc4db-ebb4-415f-a5d3-6f7d225775e9/ |
| | Brushed Space Grey Aluminum | https://www.blendkit.com/get-blendkit/84fe8f62-03e0-4f6f-a7c9-2121044bdd30/ |
| Jelly | Gelatin Gummy (726 bookmarks) | https://www.blendkit.com/get-blendkit/b846f9b6-e6af-4107-9873-82aba06eaf77/ |
| Felt | Grey Felt Fabric | https://www.blendkit.com/get-blendkit/e6b0b2de-5640-4455-9d81-1effa63efd8f/ |
| Emissive edge | Edge Emission (1,214 bookmarks) | https://www.blendkit.com/get-blendkit/e429774b-6d15-4152-b347-862d1826a2c2/ |

Ready-made materials carry their own colour and lighting assumptions. Use them as a reference, then rebuild in a single brand Principled setup (section 3).

---

## 3. Procedural recipes (Principled BSDF, Blender 4.x–5.x)

Socket ranges are from the manual [V] https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html.
- Thin Film, Diffuse Roughness, Subsurface IOR/Anisotropy and Specular Anisotropy are **Cycles-only**.
- Thin film arrived in 4.2, dielectrics only [V]. Thin film on metals in 5.0 is reported only by a secondary source [U].
- 5.2 adds a Thin Wall input.

Brand colours (hex is sRGB; Blender's hex field is gamma-corrected, so typing the hex is correct [V] https://docs.blender.org/manual/en/latest/interface/controls/templates/color_picker.html). Linear values for reference:

| Hex | Linear RGB |
|---|---|
| #9CDE45 lime | 0.332, 0.730, 0.060 |
| #33694F deep green | 0.033, 0.141, 0.078 |
| #FCF9F3 off-white | 0.973, 0.947, 0.896 |
| #F2EFE9 off-white 2 | 0.888, 0.863, 0.815 |
| #201F1D ink | 0.014, 0.014, 0.012 |

Unlisted inputs stay at default: Metallic 0, Specular IOR Level 0.5, IOR 1.5.

| # | Look | Recipe |
|---|---|---|
| R1 | **Soft-touch matte plastic** | Base = brand hex · Roughness 0.55–0.65 · IOR Level 0.4 · Sheen 0.1–0.2, sheen rough 0.5, tint white (velvet rim) · Diffuse Roughness 0.3 · optional SSS 0.05, scale ≈1–2% of icon size · micro-grain: Noise (scale 400–800) → Bump 0.02–0.04 |
| R2 | **Clay** | Roughness 0.85–0.95 · IOR Level 0.25–0.3 · Diffuse Roughness 0.6–0.8 · SSS 0.05–0.1, radius (1, 0.6, 0.4) · softer, lower-contrast highlights than R1 |
| R3 | **Glossy candy plastic** | Base hex · Roughness 0.3 (under-layer) · Coat 1.0, coat rough 0.02–0.05, coat IOR 1.5 · optional SSS 0.05–0.1 (inner glow) |
| R4 | **Jelly / gummy** | Transmission 1.0 · Base = tint (lighter than hex) · Roughness 0.1–0.2 · IOR 1.35–1.4 · Coat 1.0 / 0.03 · optional Volume Absorption inside for depth. Alternative: SSS 1.0, Random Walk, radius tinted by hex. Darkens and shifts colour; never matches the hex exactly |
| R5 | **Frosted glass (neutral)** | Base white · Transmission 1.0 · Roughness 0.25–0.45 · IOR 1.45–1.5 · **Coat 1.0, coat rough 0–0.05** (crisp edge highlights over blurred refraction; 4.x trick [V] https://blenderartists.org/t/new-principled-bsdf-in-blender-4/1525005) · optional Noise → Roughness variation 0.3–0.45 |
| R6 | **Clear glass** | Transmission 1.0 · Roughness 0–0.03 · IOR 1.5. Needs a coloured object behind or inside it, or it reads as empty |
| R7 | **Iridescent accent** | R5 or R6 + **Thin Film Thickness 250–600 nm** (0 = off) · Film IOR 1.33–1.5. Cycles only; dielectric only before 5.0. Rims or icons only |
| R8 | **Chrome** | Metallic 1.0 · Base ≈ #F0F0F0 · Roughness 0.02–0.08. Its look *is* the environment; needs a contrasty studio HDRI (section 3.2) or area-light cards |
| R9 | **Brushed aluminium** | Metallic 1.0 · Base ≈ #D9DADB · Roughness 0.25–0.35 · Anisotropic 0.6–0.9 (Cycles) · Tangent node **Radial Z** for circular brushing on a disc, or ambientCG `Metal051A` normal map · fine stretched Noise bump |
| R10 | **Bead-blasted / matte aluminium** | Metallic 1.0 · Base ≈ #D4D6D8 · Roughness 0.4–0.5 · Noise bump 0.01–0.02. **Anodized lime:** Metallic 1, Base #9CDE45 reads darker and more saturated, so raise Base value about 10% or add Coat 0.3 |
| R11 | **Glazed ceramic** | Base #F2EFE9 · Roughness 0.4 · Coat 1.0, coat rough 0.02 · SSS 0.05, warm radius |
| R12 | **Felt / fabric** | Roughness 1.0 · IOR Level 0.2 · **Sheen 0.7–1.0**, sheen rough 0.3–0.5 · Diffuse Roughness 1.0 · fine Noise bump 0.05 |
| R13 | **Rubber (ink)** | Base #201F1D · Roughness 0.65–0.75 · IOR Level 0.3 · Sheen 0.05 |
| R14 | **Gradient emissive** | Emission Color from Color Ramp (lime → deep green) · Strength ≤ 1.0 for exact colour under Standard (values >1 clip); glow via compositor Glare (Bloom) |

### 3.1 Geometry for small sizes
- **Bevel modifier.**
  - Base slab: Amount ≈ 3–6% of icon width, Segments 4–6, Profile 0.5, Limit Method Angle 30°, Harden Normals on.
  - Line icons: bevel the cap and extrusion edges at ≈ 15–25% of stroke width.
  - Bevel is what catches the highlight. Without it, glass and metal read as flat.
  - Manual [V] https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html
- **Shading.** Shade Smooth plus "Smooth by Angle" (modifier since 4.1) or Weighted Normal. Squircle: SubD on a low-poly slab, or a curve plus Geometry Nodes.
- **Hugeicons → 3D.** Stroke width after conversion should be ≥ 6–8% of the base width, or the icon disappears at 48–64 px. Icon height above the base ≈ 25–40% of stroke width. Round caps and joins (the stroke-rounded style) make clean tubes.
- **Readability at small sizes:**
  1. Contrast in value (white icon on lime) and in roughness (matte base vs glossy icon, or the reverse).
  2. No texture detail finer than 1 px at the target size.
  3. Render at 4×, downsample, check at 48/64/128 px.
- **Camera.** One template for the whole series: 85–135 mm, fixed tilt about 25–35°, fixed light rig.

### 3.2 Lighting: Poly Haven studio HDRIs (CC0, all [V])

| Use | HDRI |
|---|---|
| Soft key (umbrella + softbox) | https://polyhaven.com/a/studio_small_09 · https://polyhaven.com/a/studio_small_08 · https://polyhaven.com/a/studio_small_03 |
| Wide, even | https://polyhaven.com/a/photo_studio_01 |
| Crisp strips for chrome and glass | https://polyhaven.com/a/studio_kontrast_04 · https://polyhaven.com/a/monochrome_studio_02 · https://polyhaven.com/a/ferndale_studio_12 · https://polyhaven.com/a/cyclorama_hard_light |

- Rotate the HDRI so a softbox draws a highlight stripe along the bevel.
- Add one large area light (key, top-left, 45°) and a rim light.
- To hide the HDRI in the background: Light Path ▸ Is Camera Ray → Mix with a flat colour.

### 3.3 Colour management: keeping #9CDE45 accurate
- **AgX** (default since 4.0) is not hue-neutral. It desaturates bright saturated colours, so a bright lime drifts duller and yellower.
  - Blender 4.0 notes [V] https://wiki.blender.org/release_notes/4.0/color_management/
  - User measurements of hue shift [V] https://blenderartists.org/t/agx-changes-hue/1527123
- **Filmic** is deprecated.
- **Use one of these:**
  - **Standard**: no tone mapping, only the display conversion. Exact for diffuse and emission, but highlights clip, so keep lighting moderate.
  - **Khronos PBR Neutral**: built so the output sRGB matches the input base colour under grey lighting, with HDR limited to small speculars. This is the best fit for product-style icons.
  - Manual [V] https://docs.blender.org/manual/en/4.5/render/color_management.html. Which Blender version first shipped PBR Neutral is [U].
- **Settings:** Look None, Exposure 0, Gamma 1, Display sRGB. Export PNG 8-bit sRGB; keep EXR if you plan to grade.
- **Calibration test:**
  1. Plane with Emission #9CDE45, Strength 1 → under Standard the pixel is exactly 9CDE45.
  2. Diffuse plane under a white World at Strength 1, face unoccluded → pixel ≈ albedo (sky irradiance = 1).
  3. Tune light intensity so the lit face of the base reads within about ΔE 3 of the hex. Shaded sides will be darker, which is expected.
  4. Check with the Image Editor sample tool on the final PNG.
- **If you must use AgX:** sample the final render and adjust Base or grade in the compositor (Render Raw add-on, paid: https://superhivemarket.com/products/render-raw [V]). Don't assume the hex survives.
- **Ground matching the page:**
  - Mark the ground plane as **Shadow Catcher** and enable Film ▸ Transparent.
  - Export PNG with alpha and place it over the site's #FCF9F3 in HTML or Figma. The background stays exact and only the soft shadow is baked in.
  - Alternative: diffuse cyclorama in #F2EFE9, roughness 1. It will render slightly darker than the hex unless the light is calibrated.
- **Render settings:**
  - Cycles, 256–512 samples, OpenImageDenoise.
  - Transmission bounces ≥ 8 for glass.
  - Caustics off; Clamp Indirect 5–10 against fireflies.
  - Glass noise threads: https://blenderartists.org/t/noise-n-glass-problems/1589976 [V]

---

## 4. Starter set for the try-on stand (12 materials)

| P | Material | Recipe | Part | Ready-made reference |
|---|---|---|---|---|
| **1** | Soft-touch **lime** #9CDE45 | R1 | Base | Blendkit Rough Plastic |
| **1** | Soft-touch **deep green** #33694F | R1 | Base (alt), icon on off-white base | — |
| **1** | Off-white matte clay #FCF9F3 | R2 | Icon (white on lime), neutral base | Blendkit Diffused Clay; Community Pack clay |
| **1** | **Frosted glass**, neutral | R5 | Base (over a lime icon) or icon over a lime base | Blendkit Frosted Glass 02 |
| **1** | **Polished chrome** | R8 | Icon, rim | Blendkit Car chrome |
| **1** | **Ground**: shadow catcher + off-white cyclorama #F2EFE9 | §3.3 | Ground | — |
| 2 | **Circular brushed aluminium** | R9 | Disc base, rim | ambientCG Metal051A; Blendkit Brushed Aluminum 2 |
| 2 | Glossy candy lime (coat) | R3 | Base (glossy variant) | Blendkit Glossy Plastic |
| 2 | Ink rubber #201F1D | R13 | Icon or rim on light bases; dark variant | — |
| 2 | Bead-blasted aluminium / anodized lime | R10 | Base or rim (premium variant) | Blendkit Brushed Space Grey Aluminum |
| 3 | Clear glass + thin film | R6 + R7 | Icon accent, rim | Blendkit Procedural Iridescent plastic |
| 3 | Lime jelly / SSS **or** off-white felt | R4 / R12 | Icon (jelly); ground or base (felt) | Blendkit Gelatin Gummy / Grey Felt Fabric |

Suggested matrix (round one, about 8 renders):
- Base {lime soft-touch, deep green soft-touch, frosted glass, brushed alu}
- × icon {off-white clay, chrome}
- One ground, one HDRI (studio_small_09), Standard or PBR Neutral.

Round two: rims and accents (ink rubber, thin film), plus the glossy variant.
