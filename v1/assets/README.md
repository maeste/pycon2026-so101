# Assets for this version

Video is embedded from YouTube directly in slides.html — no local video file needed.
The SO101 robot will be on stage — no setup photo needed.

## Required: dataset-viz fallback screenshot

1. **dataset-viz-fallback.png**
   - Screenshot of Rerun (lerobot-dataset-viz) showing:
     - 3 camera views (front, wrist, right) simultaneously
     - Joint position timeline at bottom
     - A "good" episode mid-grasp
   - Capture with:
     ```bash
     source .venv/bin/activate
     lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=10
     # Take screenshot when Rerun shows the grasp moment
     ```
   - This is FALLBACK only — primary plan is live Rerun demo on stage

## Optional

2. **calibration-output.png**
   - Terminal screenshot of compare_leader_follower.py output
   - Showing the 17.5° wrist_flex before fix vs 0.85° after
   - Already visualized as text in the slides, but a real terminal screenshot adds authenticity
