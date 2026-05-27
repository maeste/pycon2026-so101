# Pre-conference checklist

## 1 week before

- [ ] Decide which version to OPEN with (V1/V2/V3) — you'll ask the audience to choose live
- [ ] Record final robot demo video and upload to YouTube (current: `hs3DzuAmxSQ`)
- [ ] Capture `dataset-viz-fallback.png` screenshot for each version's `assets/` folder:
  ```bash
  source .venv/bin/activate
  lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=10
  # Screenshot Rerun at the grasp moment → save as dataset-viz-fallback.png
  ```
- [ ] Optionally capture `calibration-output.png` (terminal showing 17.5° drift)
- [ ] Print QR code handouts (optional): `assets/qr-slides.png` + `assets/qr-homepage.png`
- [ ] Practice talk with timer — target 25 min content + 5 min Q&A
- [ ] Review presenter-notes.md for your chosen starting version

## 1 day before

- [ ] Test GitHub Pages is live: https://maeste.it/pycon2026-so101/
- [ ] Test all 3 slide versions load in browser (keyboard nav, YouTube embed)
- [ ] Test offline fallback: download slides.html locally, verify it works without internet (except YouTube)
- [ ] Prepare backup PDF: open slides in browser → Ctrl+P → Save as PDF
- [ ] Charge laptop fully
- [ ] Pack: laptop, charger, USB-C/HDMI adapter, robot SO101 (if bringing to stage)

## Day of — at the venue

### 2 hours before
- [ ] Test venue WiFi — YouTube embed needs internet
- [ ] Test projector connection (HDMI/USB-C) — verify slides display correctly
- [ ] Test projector resolution — slides are designed for 16:9, check for cropping
- [ ] Set up robot on stage (if bringing) — verify it's visible to audience

### 30 minutes before
- [ ] Open browser with homepage: https://maeste.it/pycon2026-so101/
- [ ] Open all 3 version tabs ready to switch:
  - Tab 1: V1 slides → https://maeste.it/pycon2026-so101/v1/presentation/slides.html
  - Tab 2: V2 slides → https://maeste.it/pycon2026-so101/v2/presentation/slides.html
  - Tab 3: V3 slides → https://maeste.it/pycon2026-so101/v3/presentation/slides.html
- [ ] Open terminal with venv activated for live dataset-viz demo:
  ```bash
  source .venv/bin/activate
  # Pre-test that dataset-viz works
  lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=10
  # Close it, but keep terminal ready
  ```
- [ ] Verify YouTube video loads in the slides (play/pause test)
- [ ] Disable notifications on laptop (Do Not Disturb mode)
- [ ] Set screen to NOT sleep/dim during presentation

### During the talk
- [ ] Show QR code slide at the beginning (audience scans to follow along)
- [ ] Ask audience: "Which perspective? Technical deep-dive, balanced, or personal journey?"
- [ ] Switch to chosen version tab
- [ ] When reaching dataset-viz slide: switch to terminal, run command, show Rerun
- [ ] If Rerun crashes: switch back to slides, show fallback screenshot
- [ ] If YouTube doesn't load: describe what the video shows, keep moving
- [ ] Watch the clock — if behind schedule, see "if running long" notes in presenter-notes.md

### After the talk
- [ ] Share QR code / URL one more time
- [ ] Stay for hallway questions
- [ ] Tweet/post about the talk with link to slides
- [ ] Push any last-minute slide fixes to GitHub

## Emergency fallbacks

| Problem | Fallback |
|---------|----------|
| No internet | Slides work offline (self-contained HTML). YouTube won't play → describe verbally |
| Projector fails | Present from laptop screen, audience follows on phones via QR |
| Rerun crashes | Show `assets/dataset-viz-fallback.png` |
| Robot doesn't work on stage | "This is exactly what the talk is about — hardware fights back" (genuine!) |
| Running long | Skip slides marked "if running long" in presenter-notes.md |
| Running short | Expand on lessons learned, take more Q&A |
