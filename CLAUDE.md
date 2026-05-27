# PyCon 2026 SO101 Talk

Conference talk materials for "From LeRobot to Real Robots" — a 30-minute PyCon 2026 presentation.

## Structure

Three versions of the same talk with different emphasis:
- `v1/` — Technical deep-dive (22 slides, full bug parade)
- `v2/` — Balanced + Cyberwave (18 slides, condensed bugs + platform)
- `v3/` — Personal journey (16 slides, storytelling-first)

## Tech stack

- Pure HTML/CSS/JS (zero build)
- Design system: dark theme, Inter + JetBrains Mono fonts
- Keyboard navigation (arrows, N for notes, F for fullscreen)
- GitHub Pages deployment (.nojekyll)

## Content source

All debugging stories, metrics, and technical details come from a real multi-day session with LeRobot + SO101 robot arm documented in the parent repo's `claudedocs/` folder. Key references:
- `claudedocs/act_plan.md` — ACT training pipeline
- `claudedocs/pi05_versatile_plan.md` — Pi0.5 multi-color plan
- `claudedocs/compare_leader_follower.py` — calibration drift detection tool
- `claudedocs/evaluate_dataset_quality.py` — dataset quality analysis tool

## Assets needed

Before presenting, add to each version's `assets/` folder:
- Robot demo video (~90s)
- Dataset-viz screenshots (Rerun)
- Setup photo
