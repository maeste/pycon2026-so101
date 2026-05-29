# From LeRobot to Real Robots

**PyCon 2026 Talk — 30 minutes**

> What they don't tell you about making a robot arm grab things

## About

This repository contains the presentation materials for my PyCon 2026 talk about my journey with [LeRobot](https://github.com/huggingface/lerobot) and the SO101 robot arm — from hardware assembly nightmares to working grasp policies, and everything that went wrong in between.

## Three versions

The talk has three versions with different emphasis. Pick the one that matches your audience:

| Version | Focus | Slides | Best for |
|---------|-------|--------|----------|
| [**V1 — Technical Deep-Dive**](v1/) | Full bug parade, all diagnostics | ~22 | ML/robotics engineers |
| [**V2 — Balanced + Cyberwave**](v2/) | Key bugs + cloud platform comparison | ~18 | Mixed technical audience |
| [**V3 — Personal Journey**](v3/) | Storytelling, emotional arc | ~16 | General software engineers |

## Quick start

```bash
# Just open in browser — zero build required
open index.html

# Or serve locally
python -m http.server 8000
# → http://localhost:8000
```

## Keyboard shortcuts (in slides)

| Key | Action |
|-----|--------|
| `→` / `←` | Next / Previous slide |
| `N` | Toggle speaker notes |
| `F` | Fullscreen |

## Assets needed before presenting

The `assets/` folder in each version needs:
- **Robot video** (~90 seconds): 2-3 successful grabs + 1 honest failure
- **Dataset-viz screenshot**: Rerun showing episode with 3 cameras + joint positions
- **Setup photo**: Your SO101 + laptop + cameras on desk

See `assets/README.md` in each version for details.

## The story in brief

1. Ordered SO101 kit. Defective part. Motors on mismatched firmware. Firmware update tool: Windows only.
2. Set up LeRobot on Fedora + Wayland. pynput doesn't work. Wrote stdin alternative.
3. Trained ACT policy. Loss looks great (0.08). Robot misses by 6-7cm. Every time.
4. Tried Pi0.5 (3B params). Same result. Tried SmolVLA. Same.
5. Wrote diagnostic scripts. Discovered: **17.5° calibration drift on wrist_flex motor**.
6. Re-calibrated. Re-recorded. Same policy. **0% → 80% success rate**.
7. The data to find this was in the dataset **all along**.

## Tools created during debugging

| Script | What it does |
|--------|-------------|
| `compare_leader_follower.py` | Detects calibration drift from existing dataset (no new recording needed) |
| `evaluate_dataset_quality.py` | Identifies outlier episodes via statistical analysis |
| `read_leader_pos.py` / `read_follower_pos.py` | Static calibration verification |

## Links

- [LeRobot](https://github.com/huggingface/lerobot)
- [Cyberwave](https://cyberwave.com/) — cloud robotics platform
- [SO101 Voice Pick & Place Tutorial](https://docs.cyberwave.com/tutorials/so101-voice-pick-and-place)

## License

Apache 2.0
