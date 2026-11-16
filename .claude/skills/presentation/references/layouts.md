# Layouts — copy from the reference deck

Every file in `{{PROJECT_ROOT}}\.claude\skill-fixtures\presentation\example-deck\` (if present; else read the reference deck artifact) is one finished slide in the Slides type's HTML subset, Editor Grey colours already applied. Copy the closest one, change `id`, text, page number and notes. The design system's `project/layouts.md` lists more layout types (section header, big number, quote, comparison, table, chart); build those from the same tokens and snippets below.

| Layout | Example file | Use for |
| --- | --- | --- |
| Cover (name strip) | `cover.html` | Slide 1. Name strip `{{UE_PROJECT_NAME}} . Talk . <Area> . <TitleAsTestName>`, title 120px, subtitle 44px muted, meta line `<team> · <presenter> · [Talk date]`, blue → green line at the bottom. |
| Agenda + GIF | `agenda.html` | Slide 2. 5–7 rows: slide number (mono 28 bold green) + topic (34px); looping GIF 900×487 on the right with a 24px caption. |
| Cards 2 × 2 | `why.html` | "Why" / benefits. One card title may be green. One line under the grid. |
| Topic with code | `topic-code.html`, `topic-code-2.html` | One kind/concept per slide: name strip with labels (Tier · System · Concept · Test), code panel left (960–1016 wide), side column: 36–40px bold line, "Rules like" with real calls (`Func(args) → result` + a plain line under each). |
| Code + steps + clip | `code-steps-clip.html` | Code panel, step cards (S0/S1/S2 in green) under it, a GIF on the right (406×440, cropped to one client). |
| Screenshot anatomy | `window.html` | Screenshot in a `position:relative` host with 56px side gutters; orange numbered markers in the gutters or empty areas with 3px leader lines to each control; numbered legend on the right. |
| Two screenshots + cards | `two-shots.html` | Two images at the same height (956 + 676 at 443), one short card under each. Crop empty sides off first. |
| Screenshots + timeline | `shots-timeline.html` | Two stacked screenshots left, a 4-step vertical timeline right (left border + coloured label per step). |
| Decision flowchart | `decide.html` | 5-column grid (440 · 160 · 440 · 160 · 464): question boxes, Yes (pass green) → arrows, No (red) ↓ arrows, answer boxes (red-tint, or panel with red outline). One highlight line + an image (e.g. the ini lines) at the bottom. |
| Sprint results | `sprint-results.html` | One-slide sprint summary. Eyebrow `Sprint results · <dates> · <Area>`, claim title, 64px gap, 3 equal columns: looping GIF (533×551) · **New** cards · **Fixed** cards. Card = panel, 3px left edge in the tier colour, name strip `New`/`Fixed`/`Tools` (green / blue / violet `#B48CF2`) `.` theme chip, 3 verb-first 24px bullets. GIF: one clip per card with a lower-third caption (that card's chips + bullet); see `references/media.md`. Its `/_blob/` id belongs to the sprint deck: upload your own GIF. |
| Sprint results, tall media | `sprint-results-tall.html` | Variant: a 533-wide media column the full slide height (533×765, portrait clip such as one client window) on the left; eyebrow, a 44px title and two card columns on the right. Bullets ≈ 30 characters to fit. |
| Sprint results, corner media | `sprint-results-corner.html` | Variant: a small 16:9 clip (400×225) top right beside the 64px title; two full-width card columns under it, room for the longest bullets. For a supporting clip, not the main proof. |
| Closing / Q&A | `docs.html` | `ground-deep` background, "Questions?" 120px, the guide link 44px blue, its path with the key word in green, docs screenshot on a white card. |

## Fixed snippets

Colours (scheme 29, see the design system `tokens.json`): ground `#1C1F24`, ground-deep `#14171B`, panel `#23272E`, chip `#2C313A`, line `#3A404B`, ink `#E1E6EE`, muted `#98A1AE`, blue `#3D8BFD`, green `#8BE04E` (text on it `#151515`), orange `#F08A24`, pass `#5BC27A`, red `#F06A6A`, code string `#9CC3FF`, code text `#E6EBF5`.

Content slide section:
```html
<section id="ID" data-transition="fade" style="background:#1C1F24;color:#E1E6EE;font-family:'Roboto', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:28px">
```

Header (add `;padding:0 0 40px 0` to the div when dense content follows):
```html
<div style="display:flex;flex-direction:column;gap:12px">
<p style="font-size:24px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#3D8BFD">EYEBROW</p>
<h2 style="font-size:64px;font-weight:700;letter-spacing:-1px;line-height:1.15;color:#E1E6EE">Topic: claim</h2>
</div>
```

Page number (last element before `<aside>`; none on the cover or section headers):
```html
<p style="position:absolute;right:128px;bottom:64px;width:240px;text-align:right;font-family:'JetBrains Mono', 'Courier New', monospace;font-size:24px;color:#98A1AE"><span style="color:#8BE04E;font-weight:700">04</span> / 11</p>
```

Card: `background:#23272E;border-top:3px solid #3D8BFD;border-radius:4px;padding:32px 40px` — no other border (the format allows one border colour per element).

Code panel: `background:#14171B;border-radius:4px;padding:40px`, one `<p>` in JetBrains Mono 24px, `line-height:1.5`, `white-space:nowrap`, lines joined with `<br>`, indents as `&#160;&#160;`, strings in `<span style="color:#9CC3FF">`, the line that matters (step labels, the key comment) in `#8BE04E`. Max ~65 characters per line.

Name strip chip: mono 28px; tier chip `background:#8BE04E;color:#151515;font-weight:700`, other chips `background:#2C313A`; a `.` `<p>` between chips; labels under chips 24px muted (tier label green bold).

Marker + leader line (inside a `position:relative` host; ≤ 24 pinned children per host):
```html
<div style="position:absolute;left:46px;top:49px;width:26px;height:3px;background:#F08A24"></div>
<p style="position:absolute;left:6px;top:30px;width:40px;height:40px;background:#F08A24;color:#FFFFFF;border-radius:50%;font-size:24px;font-weight:700;line-height:40px;text-align:center;box-shadow:0 0 0 2px #FFFFFF">1</p>
```
Place the circle off the control (gutter or empty area), the line ending at the control's edge. Compute positions from the image's pixel coordinates × display scale; no negative offsets.

Images: `<img src="/_blob/<id>" alt="what it shows" style="width:…px;height:…px;object-fit:cover;border-radius:6px;box-shadow:0 8px 32px rgba(0,0,0,0.45)">`. Set width and height to the crop's aspect ratio.
