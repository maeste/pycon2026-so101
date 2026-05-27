# Presenter Notes — V2: Balanced + Cyberwave

**Talk:** From LeRobot to Real Robots: What They Don't Tell You About Making a Robot Arm Grab Things
**Speaker:** Stefano Maestri
**Event:** PyCon 2026
**Duration:** 30 minutes (25 min content + 5 min Q&A / optional Cyberwave demo)
**Version:** V2 — Condensed bugs, extended platform section

---

## Timing Overview

| Slide | Time       | Duration | Topic                                |
|-------|------------|----------|--------------------------------------|
| 1     | 0:00       | 0:45     | Title                                |
| 2     | 0:45       | 1:15     | What is LeRobot + SO-101             |
| 3     | 2:00       | 1:30     | Hardware reality check               |
| 4     | 3:30       | 2:00     | Software pipeline                    |
| 5     | 5:30       | 1:30     | Policy options                       |
| 6     | 7:00       | 1:30     | Training on consumer hardware        |
| 7     | 8:30       | 2:30     | The bugs (combined slide)            |
| 8     | 11:00      | 3:00     | Calibration "aha moment" (CLIMAX)    |
| 9     | 14:00      | 1:30     | Diagnostic tools                     |
| 10    | 15:30      | 1:30     | The 15-20% rule                      |
| 11    | 17:00      | 1:00     | Dataset viz demo                     |
| 12    | 18:00      | 1:00     | Robot demo video                     |
| 13    | 19:00      | 1:30     | Lessons learned                      |
| 14    | 20:30      | 1:30     | Cyberwave intro                      |
| 15    | 22:00      | 1:30     | Cyberwave SO-101 example             |
| 16    | 23:30      | 1:30     | Local vs cloud comparison            |
| 17    | 25:00      | 1:30     | When to go local vs cloud            |
| 18    | 26:30      | 3:30     | Thank you + Q&A                      |

**Total content:** ~26:30
**Q&A / demo buffer:** ~3:30

---

## Slide-by-Slide Notes

### Slide 1 — Title (0:00 - 0:45)

Open with energy. "I'm Stefano, and six months ago I decided to teach a robot arm to pick up a block. How hard could it be?" Pause for effect. "Turns out: very." Set expectations: this is a war story with a happy ending — and a glimpse at what the future looks like.

**Key message:** This talk is practical. You will learn from my mistakes.

---

### Slide 2 — What is LeRobot + SO-101 (0:45 - 2:00)

Brief explainer. LeRobot is from Hugging Face — open source, active community, well-maintained. SO-101 is a 6-DOF 3D-printed arm. About $300 in parts. Uses leader-follower teleoperation: you move one arm, the other mimics it.

"The task: pick up a block and put it somewhere else. Show of hands — who thinks this should take a weekend?"

**Key message:** Simple task, accessible hardware. Sounds easy.

---

### Slide 3 — Hardware Reality Check (2:00 - 3:30)

Quick hits. Don't dwell — the audience gets it fast.

- Defective servos: 2 out of 12 DOA. Replacement lead time measured in weeks.
- Wrong motors: STS3215 instead of STS3250. Different calibration. Subtle failures.
- Firmware tool: Windows-only. "I had to find a Windows machine. In 2026."
- Assembly time: 3x the estimate. Always.

Get a laugh on the Windows line. Move on.

**Key message:** Every robotics tutorial starts at step 4. Steps 1-3 are hardware chaos.

---

### Slide 4 — Software Pipeline (3:30 - 5:30)

Walk through the pipeline. Record -> Train -> Evaluate -> Debug. "This looks linear. You will loop through it dozens of times."

Mention the three columns briefly:
- Recording: USB bandwidth limits with 3 cameras. Wayland breaks device ordering. MJPEG vs YUYV codec choice matters for bandwidth.
- Training: GPU memory is the constraint, not model quality. Batch size tuning is trial and error.
- Inference: 30 Hz or failure. If your inference drops to 8 Hz because the model is on CPU, the robot will jerk and miss.

**Key message:** The loop is the product. You will live in debug mode.

---

### Slide 5 — Policy Options (5:30 - 7:00)

Quick comparison table. Three policies available in LeRobot:

- **ACT:** Start here. Fast to train, small, proven. Single-task specialist.
- **SmolVLA:** Level up. Language-conditioned. "Pick up the red one." 500M params means 12GB VRAM.
- **Pi0.5:** Research territory. 3B params. Needs serious hardware. Amazing when it works.

"My recommendation: start with ACT. When your data is bad, you'll find out in 2 hours instead of 12."

**Key message:** Model choice matters less than data quality. Start simple.

---

### Slide 6 — Training on Consumer Hardware (7:00 - 8:30)

RTX 5000 Ada, 16 GB. Good card, still hits limits.

- OOM at batch=32. No warning — process just dies.
- Sweet spot at batch=16 for ACT.
- Each training cycle: 2-4 hours minimum.

Show the loop diagram. "5-10 iterations is normal. That's 20-40 hours of active work before you get a working policy." This is why diagnostics matter — cutting one iteration saves hours.

**Key message:** Time is the real cost. Optimize for fewer iterations.

---

### Slide 7 — The Bugs (8:30 - 11:00)

Three bugs, one slide. Keep it punchy.

**Bug #1 — Silent CPU Fallback:**
"nvidia-smi showed 2% GPU utilization. The model was running on CPU. PyTorch loaded it, happily did inference, but at 8 Hz instead of 30. No error. No warning."
Fix: explicitly call `policy.to("cuda")` and verify with `next(policy.parameters()).device`.

**Bug #2 — Causal Confounding:**
"The policy worked perfectly in recorded video replay. Failed completely on the real robot. Why? The leader arm was visible in the camera frame. The policy learned to follow the leader arm, not to pick up blocks."
Fix: physically remove leader arm from camera field of view.

**Bug #3 — Distribution Shift:**
"Works at 10am. Fails at 3pm. Same robot, same code, same block. The sun moved."
Fix: record across lighting conditions. Enable brightness/contrast augmentation. But disable hue jitter if your task is color-dependent.

**Punchline:** "No errors. No warnings. Just a robot that doesn't work."

**Key message:** The system never tells you something is wrong. You must detect it yourself.

---

### Slide 8 — The Calibration "Aha" Moment (11:00 - 14:00)

**THIS IS THE CLIMAX. SLOW DOWN.**

Build tension: "We had trained six policies. None worked. We were questioning everything — the model architecture, the data quality, the reward function, our career choices."

"Then we wrote a script. A simple Python script that read every episode in our dataset and compared the leader joint positions to the follower joint positions."

Point at the table. "Five joints: fine. Less than 2 degrees of drift. Then: wrist_flex."

Pause. Let them read the number.

"17.5 degrees. Systematic. Every single episode. The follower's wrist was consistently 17.5 degrees off from where the leader was commanding it to go."

"One re-calibration. Same policy, same data, same everything else."

Point at the before/after.

"Zero percent to eighty percent."

Let that sink in for a beat.

"The data to find this was in our dataset all along. We just never looked."

**Key message:** The biggest breakthrough came from a diagnostic script, not a better model.

---

### Slide 9 — Diagnostic Tools (14:00 - 15:30)

Three tools, ~600 lines total.

- **compare_leader_follower:** The one that found the 17.5 degree drift. Reads every episode, computes per-joint statistics.
- **evaluate_dataset_quality:** Flags outlier episodes by trajectory smoothness and completion metrics. Found that 12% of our episodes were corrupted (bumped table, missed grasp).
- **read_*_pos:** Simple real-time readout. Before every recording session, compare leader and follower positions live. Catches drift before it enters your data.

"These aren't sophisticated ML tools. They're data analysis scripts. The hard part isn't the code — it's knowing to look."

**Key message:** Build inspection tools before training tools.

---

### Slide 10 — The 15-20% Rule (15:30 - 17:00)

"We plateaued at 80% success. The remaining 20% was always rotated blocks."

Dataset analysis: only 5% of episodes had rotation. Below the learning threshold.

"If a skill appears in less than 15% of your episodes, the model won't learn it. It's just noise."

Fix: record 15-20 targeted episodes with rotated blocks. Signal rises above threshold. Skill improves.

Augmentation note: enable brightness/contrast/blur for robustness. But hue jitter for color-based tasks teaches the model to ignore color — the opposite of what you want.

**Key message:** Data balance matters more than data volume.

---

### Slide 11 — Dataset Viz (17:00 - 18:00)

**[PLACEHOLDER: Insert Rerun screenshot or prepare live demo]**

Quick visual. Show camera feeds, joint trajectories, episode boundaries in Rerun.

"This is how we spotted the outlier episodes. You can see the joint trajectories diverge right where the operator bumped the table."

Keep brief — 1 minute max. This is a visual breather before the robot demo.

**Key message:** Visualization catches what statistics miss.

---

### Slide 12 — Robot Demo (18:00 - 19:00)

**[PLACEHOLDER: Insert video file or prepare live feed]**

Play the video. Let it breathe.

"After all the debugging, the calibration fix, and the targeted data collection — here it is."

If the video is short, play it twice: once at normal speed, once with commentary pointing out the approach phase, the grasp, and the placement.

**Key message:** It works. The journey was worth it.

---

### Slide 13 — Lessons Learned (19:00 - 20:30)

Summarize the local journey.

"If you take one thing from this talk: build diagnostic tools before you build training pipelines."

Walk through the pattern: every visible symptom had its root cause 2-3 layers below. Policy fails -> data is wrong -> calibration is off. Inconsistent results -> lighting variance -> no augmentation.

Five concrete takeaways. Read them if time allows, or let the audience read while you set up the transition.

**Transition:** "Now — everything I just showed you was the hard way. And the hard way taught us a lot. But what if your goal isn't to learn — what if your goal is to ship?"

**Key message:** Understanding beats brute force. And now let's talk about the shortcut.

---

### Slide 14 — Cyberwave Intro (20:30 - 22:00)

Transition carefully. Don't sound like an ad.

"I found Cyberwave after fighting all these issues. It's a platform that provides one API for any robot — you write Python, it handles infrastructure."

Walk through the architecture diagram:
- Digital twins: pre-configured simulation of your robot
- Cloud training: managed GPUs, no OOM debugging
- Observability: the diagnostic tools we built manually? Built-in here.
- Deployment: OTA updates, fleet management

"I'm not saying don't learn the hard way. I just showed you why that knowledge is valuable. But if your goal is to ship, this exists."

**Key message:** Genuine recommendation, not a sales pitch. Present it as "here's what exists."

---

### Slide 15 — Cyberwave SO-101 Example (22:00 - 23:30)

Show the code. "This is the entire application for the same pick-and-place task we spent months on locally."

Walk through:
- You provide a microphone and speech-to-text (any provider — Whisper, Google, etc.)
- You send a text command: "pick up the red block"
- Cyberwave handles calibration, cameras, policy selection, inference loop, safety monitoring

"The voice control angle is compelling for demos and for accessibility. But the real value is everything you don't see — the infrastructure that just works."

Mention the tutorial link for people who want to try it at home.

**Key message:** Same task, fraction of the effort. The complexity didn't disappear — it moved to the platform.

---

### Slide 16 — Local vs Cloud Comparison (23:30 - 25:00)

Let the table speak for itself. Walk through each row briefly:

- Setup: days/weeks vs minutes
- Recording: manual with USB headaches vs guided dashboard
- Training: local GPU tuning vs cloud GPU with monitoring
- Debugging: our 600 LOC of scripts vs built-in observability
- Deployment: "SSH, systemd, prayer" vs one-click (get a laugh here)
- Scaling: each new robot starts from scratch vs fleet deployment

"All of this local work taught us what matters. Cyberwave automates the hard-won lessons."

**Key message:** The comparison is real. Neither side is dishonest.

---

### Slide 17 — When to Go Local vs Cloud (25:00 - 26:30)

Balanced perspective. Neither approach is wrong.

**Go local when:** Learning, research, budget-constrained, need full control, robot not supported.
**Go cloud when:** Production, team, scaling, time-constrained, want observability.

"Start local to understand. Go cloud to ship."

"The local journey gives you intuition that's invaluable even if you later use a platform. Knowing what calibration drift looks like, knowing what distribution shift feels like — that knowledge makes you better even when a platform handles it for you."

**Key message:** Both paths are valid. Choose based on your goal.

---

### Slide 18 — Thank You + Q&A (26:30 - 30:00)

"Thank you. I'm happy to take questions."

"If anyone wants to see a live Cyberwave demo during the break, come find me — I'll have the robot set up."

Mention:
- All diagnostic tools will be open-sourced (link to GitHub)
- Slides are available at the link on screen
- Happy to chat about hardware, policies, or platform choices

If no questions immediately, have a backup: "One question I often get is..." and address something common like "how many episodes do you actually need?" (Answer: 50-100 for ACT, depends on task complexity, hard examples matter more than volume.)

**Key message:** Approachable. Available. Genuine.

---

## Preparation Checklist

### Before the talk:
- [ ] Test slide navigation (arrows, keyboard, touch)
- [ ] Test speaker notes toggle (N key)
- [ ] Test fullscreen mode (F key)
- [ ] Verify Rerun screenshot is inserted in slide 11
- [ ] Verify demo video is ready for slide 12
- [ ] Test video playback on venue hardware
- [ ] Have backup plan if video fails (describe with screenshots)
- [ ] Test Cyberwave live demo setup for post-talk (optional)
- [ ] Check projector resolution and adjust if needed
- [ ] Have water nearby

### Placeholders to fill:
1. **Slide 11:** Replace placeholder with Rerun dataset visualization screenshot
2. **Slide 12:** Replace placeholder with robot demo video (embed or link)

### Backup materials:
- Screenshots of robot in action (in case video fails)
- Terminal output of compare_leader_follower.py (in case someone asks for details)
- Cyberwave dashboard screenshots (in case live demo isn't available)

---

## Q&A Preparation

### Expected questions and short answers:

**Q: How many episodes do you need?**
A: 50-100 for ACT on a simple task. But quality and balance matter more than quantity. 50 good episodes beat 200 noisy ones.

**Q: Can you use simulation instead of real data?**
A: Sim-to-real transfer is improving but still has a gap. For SO-101 specifically, real data is more reliable. Cyberwave's digital twin approach narrows the gap significantly.

**Q: What about reinforcement learning instead of imitation learning?**
A: RL needs a reward function and many more trials. For tabletop manipulation, imitation learning from demonstrations is more practical. RL shines for tasks where you can't easily demonstrate.

**Q: How do you handle safety during evaluation?**
A: Always supervise. Keep one hand near the emergency stop. Set joint limits in software. Start with slow motion and increase speed gradually.

**Q: What's the cost of Cyberwave?**
A: Refer them to the website. Don't quote prices in the talk — they may change. Focus on the value proposition: time savings, reliability, scaling.

**Q: Why not just use a bigger model?**
A: "That was exactly our instinct. We tried ACT, SmolVLA, even Pi0. None worked — because the data was wrong. A bigger model on bad data just overfits to the noise more expressively."

---

## Live Demo Commands (keep terminal ready)

### Dataset visualization (for dataset-viz slide)
```bash
source .venv/bin/activate
lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=10

# Alternative episodes to show
lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=25
```

In Rerun: show 3 cameras, joint plots, scrub to grasp moment.

### Fallback
Screenshot in `assets/dataset-viz-fallback.png` if Rerun doesn't work on stage.
