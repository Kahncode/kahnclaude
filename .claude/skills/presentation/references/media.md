# Media — screenshots and GIFs

## Where to find real captures

1. `{{TEMP_BASE}}\illustrate-scratch\<topic>\screens\` — source captures of Confluence user guides (editor windows, Horde Test tab / New Job / Test Automation Hub, Slack red posts, report.html). Look at them with Read before asking for new ones.
2. Images the user pastes into the chat (`…/images/N.png`) or files in `{{DOWNLOADS}}\`.
3. Otherwise put it on the draft board's capture list: what to capture, at what size, where it goes. Until it exists, the slide shows a dashed placeholder labelled "to capture".

Copy anything you use into a working folder first (`{{TEMP_BASE}}\claude-scratch\<deck>\img\`), never edit the original.

## Cropping (without Pillow)

PowerShell + System.Drawing:
```powershell
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($in); $bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.DrawImage($img, (New-Object System.Drawing.Rectangle 0,0,$w,$h), (New-Object System.Drawing.Rectangle $x,$y,$w,$h), [System.Drawing.GraphicsUnit]::Pixel)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); $img.Dispose()
```
Read a size with `[System.Drawing.Image]::FromFile($p).Width/Height`. Screenshots are often 2560 wide shown at 2000: multiply displayed coordinates by the factor the Read tool reports. Crop empty margins off; look at every crop once before using it.

Rendering text as an image (e.g. ini lines in an editor look): write a small HTML file and screenshot it with headless Edge:
`& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=1100,250 "--screenshot=<out.png>" "file:///<page.html>"`. Say on the slide or in the notes that it is rendered from the real file.

## GIFs and video

- Limit: **15 MB per uploaded file**. A screen-capture GIF is often 30–50 MB.
- ffmpeg: use the one on `PATH`, or a copy bundled with a screen-capture or video tool.
- Smaller GIF (keeps animation in .pptx and Google Slides):
  `ffmpeg -y -i in.gif -vf "fps=8,scale=560:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" out.gif`
- Crop one half (e.g. client 0 of a split PIE view): prefix the filter with `crop=iw/2:ih:iw/2:0,` (right half) or `crop=iw/2:ih:0:0,` (left half).
- Poster / check frame: `ffmpeg -y -i in.gif -vframes 1 -vf "select=eq(n\,30)" frame.png`, then Read it.
- MP4 (much smaller, fine for HTML draft boards, not for the Slides deck): `-movflags +faststart -pix_fmt yuv420p -c:v libx264 -crf 26 -an`.
- Run long conversions with a 300000 ms timeout.
- winget ffmpeg (`winget install Gyan.FFmpeg`) lands in `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*\bin\`. Drive it from Python `subprocess` with Windows paths; Git Bash `/c/...` paths with spaces or brackets fail. `drawtext` needs `fontfile=`; for styled text, draw a PNG with Pillow and `overlay` it. Odd sizes break `yuv420p`, so use even ones (534 × 552 for a 533 × 551 box).
- **Captioned GIF** (the Sprint results layout): first make a contact sheet per clip (`fps=1,scale=640:-1,tile=4x4`) to pick cut points and crops. Then per clip: `-ss/-t` trim, `crop` to the box aspect, `scale`, `fps=10`, `setpts=PTS-STARTPTS`. Overlay a lower-third PNG (the card's chips + bullet, `ground-deep` panel, tier-colour left edge). Slide it in with `overlay=x='if(lt(t,0.4),X-overlay_w+(overlay_w+X)*t/0.4,X)'`. Fit screenshots with `force_original_aspect_ratio=decrease` + `pad` away from the banner, then `concat`.
- **Pin the UI colours** or small flat areas drift (violet `#B48CF2` came out `#9699D7`): `palettegen=max_colors=104:stats_mode=diff`, append the slide's hex colours to that palette as a 16 × 16 PNG with Pillow, then `paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle`. Check by sampling a chip pixel from a frame of the GIF. About 31 s at 534 × 552 and 10 fps ≈ 14.4 MB.

## Uploading to the deck

`Artifact` publish with `url` = the deck, `asset: true`, `file_paths: [...]` (up to 25). Use each returned `/_blob/<id>` verbatim in `<img src>`. Every image needs `alt` text saying what it shows.
