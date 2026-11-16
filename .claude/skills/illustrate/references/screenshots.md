# Screenshots

A drawing shows how something works. A screenshot shows what the reader will actually see, so they can recognise it. Use both.

**Worth a screenshot:** real UI the reader must find or read: a menu path, editor window, details panel, on-screen overlay, game view, Horde or Swarm page, report, Slack message, Output Log with the telling lines.

**Not worth one:** code (use text with `file:line`), mechanisms (draw them), a mock of UI you can really capture, or anything that adds no fact.

## 1. Write the shot list

After the figure plan, list every shot: an id, what it must show, the state needed, the card it belongs to, and how to get it. Each shot gets one of these routes:

| Route | When | How |
|---|---|---|
| **Existing** | The folder already has it, or `{{TEMP_BASE}}/illustrate-scratch/*/screens/` has a recent one that still matches | Copy it to this page's `screens/` |
| **Web page** | Horde, Swarm, Jira, Confluence or any page reachable in Chrome | Claude in Chrome: new tab, `computer` `screenshot` with `save_to_disk: true` and no `scale` (the saved file is scaled too), then copy the returned file to `screens/` and close the tab. It saves a JPEG about 1540 px wide, so for small text use `zoom` on the region with `save_to_disk: true`. Read-only: navigate and scroll, don't submit anything |
| **Open window** | The window is already showing the right state | `scripts/capture_window.py` |
| **PIE or game view** | A PIE session is already running | `scripts/capture_window.py` on the editor or client window. A console command through the `unreal-pie` skill is fine when the user is not playing |
| **Ask the user** | Anything else | Section 3 |

Ask the user when a shot needs:
- the editor launched, PIE started or stopped, or a tab, asset or test opened in an editor someone is using
- a timed or rare moment (a running overlay, a crash dialog, a failure on screen)
- hover states, open dropdowns, or another app such as Slack or P4V
- a blank background capture

Never launch the editor, or interrupt a running session, just to get a picture.

```
python "$KC_PROJECT_ROOT/.claude/skills/illustrate/scripts/capture_window.py" --list --process "{{EDITOR_PROCESS}}"
python "$KC_PROJECT_ROOT/.claude/skills/illustrate/scripts/capture_window.py" --process "{{EDITOR_PROCESS}}" --title "Unreal Editor" --out <page>/screens/editor.png
```

The editor process owns several windows: the main one (`... - Unreal Editor`), detached tabs such as `Project Settings`, and a console whose title is the exe path. So list first, and filter on the title. The script captures one named window, never the whole desktop, and doesn't raise it, so whatever covers the window doesn't show. It skips minimized windows, refuses a blank capture, and exits with 3 when several windows match.

## 2. Look at every shot before using it

Read each image. A picture you haven't viewed never goes on a page.

- **Correct the page from it.** Screenshots catch wrong drawings and text: a menu path, a label, a count. Trust the screenshot over your own notes, and fix the page.
- **Check it's current.** Stale UI is misleading. If the UI has changed, caption the date or ask for a new shot.
- **Blur what the team shouldn't see:** tokens, keys, emails, private messages, personal paths and browser tabs, plus people's names unless they are the point of the shot. The `blur` list does this, and it changes the published pixels. Originals stay in `screens/`, which is not published.

## 3. Ask the user once, in one list

Asking never blocks the page. Build it fully with the shots you have, using a drawing or plain text where a shot is missing. **Never leave an empty placeholder on the page.** Then put the request in your final reply as a numbered list, most valuable first:

```
Screenshots that would improve this page (save anywhere and give me the folder):
1. Tools > Test Automation menu open: shows the real path for card "Run a test".
2. A test running in PIE, whole window with the overlay visible: opening picture.
3. Output Log filtered on LogAutomationController after a run: card "PIE session".
```

Each item says what to show and where it goes. Keep it to the shots that really teach something, normally 8 or fewer. Don't ask when the task says "local only" or runs unattended; list the wanted shots on your notes only.

When a folder comes back:
1. Copy the files into `screens/`. Don't edit or delete the originals.
2. View every one, including any you didn't ask for. Place each where it fits, and say so if one fits nowhere rather than forcing it in.
3. Correct the page from what they show, and say what changed.
4. Say what's still missing, if anything. The user may add more and ask you to re-evaluate; re-check the whole folder each time.

## 4. Crop, blur, highlight

Work in `{{TEMP_BASE}}/illustrate-scratch/<slug>/`: originals in `screens/`, the manifest in `shots.json`, generated fragments in `shotfrags/`. The script's header documents the manifest.

1. **Read coordinates from a grid.** Images you view may be scaled, so don't estimate pixels from them:
   `python "$KC_PROJECT_ROOT/.claude/skills/illustrate/scripts/annotate_shots.py" --grid screens/foo.png --out previews/foo-grid.png`
   View a region at a time when the image is large. Every manifest coordinate is a source-image pixel.
2. **Crop tight** to the part that matters, keeping enough around it that the reader can find it on their own screen.
3. **Highlight only what the text talks about:** red box, numbered circle, short arrow. Use `c` for meaning (`bad` is the default highlight red, `warn` for a warning, `good` for correct, `a` for neutral). Between one and six marks per shot.
4. **Build, then check:** `python "$KC_PROJECT_ROOT/.claude/skills/illustrate/scripts/annotate_shots.py" shots.json`. View each `shotfrags/<id>-preview.png` and fix any box that misses its target. This matters as much as checking a drawing.

## 5. Put it on the page

Paste the fragment `shotfrags/<id>.html` in a figure (`base.html` has the styles and the click-to-zoom script):

```html
<figure>
  <!-- contents of shotfrags/tools.html -->
  <figcaption><b>1</b> Tools menu. <b>2</b> Test Automation opens the Session Frontend.</figcaption>
</figure>
```

- The caption explains each number, because the numbers mean nothing alone. Give the state or date if it can change.
- Highlights are SVG, so they stay sharp and follow the theme. Don't bake them into the image.
- A shot goes **next to** the drawing that explains it, not instead of it: the picture says "this is what you'll see", the drawing says "this is why".
- Size: normally under 150 KB per shot. Lower `q` or `maxw` for big game views. Watch the total: a page must stay under the Artifact limit of 16 MB, and a Confluence HTML macro page has been fine at about 400 KB.
