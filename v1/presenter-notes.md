# Presenter Notes: From LeRobot to Real Robots (V1 -- Full Bug Parade)

**Total time: 30 minutes**
**Format: Technical deep-dive**
**Speaker: Stefano Maestri**

---

## Timing Budget Overview

| Block            | Slides   | Duration  | Cumulative |
|------------------|----------|-----------|------------|
| Opening + Setup  | 1-6      | 7:00      | 7:00       |
| Policy + Training| 7-8      | 2:30      | 9:30       |
| Bug Parade       | 9-14     | 10:00     | 19:30      |
| Tools + Metrics  | 15-17    | 4:30      | 24:00      |
| Demos            | 18-19    | 3:00      | 27:00      |
| Closing          | 20-22    | 3:00      | 30:00      |

---

## Slide 1 -- Title (TIME: 00:00 - 00:30)

Welcome everyone. I am Stefano, a software engineer who spent the last several months trying to make a budget robot arm grab a red block. Spoiler: it was much harder than the tutorials make it look.

This talk is the full unfiltered story. Five real bugs, five real fixes, and one robot that eventually learned to grab things.

**Transition:** "Let me show you what we are going to cover."

---

## Slide 2 -- Agenda (TIME: 00:30 - 01:15)

Walk through the four-block structure quickly. Emphasize: this is not a tutorial. This is a field report. We will cover real bugs with real debugging sessions.

Point out the tags at the bottom: 5 bugs, 5 fixes, 1 robot, and the magic number 17.5 degrees that you will understand by slide 13.

**Transition:** "First, let's meet our tools."

---

## Slide 3 -- What is LeRobot + SO101 (TIME: 01:15 - 02:30)

LeRobot is HuggingFace's open-source PyTorch library for real-world robotics. Datasets, pretrained policies, training and evaluation tools. Three CLI commands matter for us: lerobot-record for data collection, lerobot-train for training, lerobot-rollout for deployment.

The SO101 is a budget 6-DOF arm. About 300 euros total. 3D-printed structural parts, STS3215 servo motors, leader-follower setup for teleoperation.

Point to the SVG: our task is dead simple to describe. "Grab the red block and put it in the box." Simple description, nightmarish execution.

**Transition:** "Before we even get to software, let's talk about what happened with the hardware."

---

## Slide 4 -- Hardware Journey (TIME: 02:30 - 04:00)

Go through each card:

1. Defective 3D-printed shoulder bracket: layer adhesion failure caused binding under load. Had to reprint with higher infill percentage. If you are buying pre-printed parts, inspect every structural joint.

2. Wrong motors: SCS3215 vs STS3215. Different serial protocol. If the motors do not respond to commands, check the model number physically printed on the motor housing. Not just the label on the box.

3. Firmware tool: the FD debug software for updating motor firmware only runs on Windows. If you are a Linux-only shop, you need a Windows VM or a friend with a Windows machine. This is not documented well.

4. Calibration: every joint has an absolute encoder that needs a zero reference. The procedure requires manual alignment with millimeter precision. One wrong offset propagates through the entire kinematic chain.

Read the callout: expect 2-3 weeks of hardware debugging before writing any ML code.

**Transition:** "Once the hardware works, you need cameras."

---

## Slide 5 -- Camera Setup & USB (TIME: 04:00 - 05:15)

Three cameras: front (top-down), right (side angle), wrist (gripper-mounted). All 640x480 at 30Hz.

The USB topology diagram is important. All three cameras plus both robot arms share USB 2.0 Bus 001 with a theoretical max of 480 Mbps. Three uncompressed VGA streams at 30fps need about 830 Mbps. The math does not work.

Solution: enable MJPEG compression at the camera hardware level, and if your machine has multiple USB controllers, spread the cameras across different buses. Use `lsusb -t` to check the actual topology.

**Transition:** "Cameras working. Now we record."

---

## Slide 6 -- Recording Pipeline (TIME: 05:15 - 07:00)

The recording flow: teleoperate, save episode, reset scene, repeat. Standard lerobot-record loop.

The problem: on Wayland (which is default on modern Fedora, Ubuntu 24.04+), pynput's keyboard listener silently fails. It does not crash, it just does not receive any key events. So the arrow-key controls for ending episodes early and the escape key for stopping recording simply do not work.

Our fix, which we contributed upstream: an interactive stdin prompt between episodes. Three choices: Y or Enter to keep the episode and continue, n to re-record, q to quit. Plus a SIGQUIT handler on Ctrl+backslash for ending the current episode early during recording.

Key design decisions: zero new threads (the signal handler runs on the main thread between bytecode instructions), and a sentinel value of reset_time_s equals negative one to activate this mode.

Show the code example. This was merged into LeRobot main.

**Transition:** "Data recorded. Now, which policy do we train?"

---

## Slide 7 -- Policy Landscape (TIME: 07:00 - 08:15)

The bubble chart shows three families. Size = parameters, vertical position = generalization capability.

ACT at 80 million parameters: a specialist. You train it for one task, it does that task. chunk_size=100 means it predicts 100 future actions in one forward pass. Our pick because it fits on 16GB VRAM.

SmolVLA at 500 million: language-conditioned, meaning you can describe the task in natural language. More flexible but needs more compute.

Pi0 and Pi0-FAST at 3 billion: foundation models pretrained on large multi-robot datasets. Most capable, but far beyond our 16GB budget. The dashed red line shows our VRAM limit.

Point: for budget hardware, ACT is the practical choice. Do not chase the biggest model.

**Transition:** "ACT it is. Let's train it."

---

## Slide 8 -- Training on 16GB GPU (TIME: 08:15 - 09:30)

RTX 5000 Ada Laptop. Batch size 32 causes immediate OOM. Batch size 16 with AMP fits, peaking at 14.2 GB.

Total training time for 100k steps: about 28 minutes. That is fast. ACT is a small model.

Show the training command. Critical flag: --policy.device=cuda. We will come back to why this matters on the next slide.

The nvidia-smi watch command in a second terminal is essential. Always monitor VRAM during your first training run.

**Transition:** "Training done. We deploy. And then things get weird."

---

## Slide 9 -- Bug #1: Policy on CPU (TIME: 09:30 - 11:00)

This is the most embarrassing bug. After training on GPU, we deploy with lerobot-rollout. The robot moves, but it is stuttery and slow. We check nvidia-smi: GPU utilization 2%, VRAM usage 46 MB. The policy silently defaulted to CPU.

Why: without an explicit --policy.device=cuda flag, the rollout script does not automatically move the model to GPU. It loads on CPU.

Before: 17 Hz inference. After adding one flag: stable 30 Hz. The fix is literally one command-line argument.

Emphasize: always check nvidia-smi during deployment. If GPU util is low, you are probably running on CPU.

**Transition:** "OK, policy on GPU. But then we see something else weird: GPU utilization is spiky."

---

## Slide 10 -- Bug #2: Action Chunking (TIME: 11:00 - 12:30)

This is the not-a-bug bug. GPU utilization spikes briefly then drops to near-zero for several seconds. We spent 2 days trying to fix a performance problem that was actually correct behavior.

Explain the timeline diagram: ACT predicts 100 actions in one forward pass. Then it replays those cached actions one per step for 100 steps at 30Hz. That is 3.3 seconds of robot motion from one inference call. GPU idle 90% of the time is by design.

The sporadic "running slower than requested fps" warnings in the logs are timing jitter from OS scheduling, not a real performance problem.

Cost us 2 days. Lesson: read the model architecture documentation before profiling.

**Transition:** "With the performance non-issue resolved, the robot moves smoothly. But it misses the block. Every time."

---

## Slide 11 -- Diagnostic Flow (TIME: 12:30 - 14:00)

To understand why, we profiled the 30Hz control loop. We added temporary logger.info calls to every stage of the pipeline.

Walk through the pipeline diagram: get_observation costs 2ms, preprocessing is near-zero, policy inference is 3ms when using cached actions or 22ms for a real forward pass, send_action is 0.2ms. Total per step: about 5ms, well under the 33ms budget for 30Hz.

Point to the budget bar: we use 5ms out of 33ms available. The bottleneck is absolutely not compute.

Read the conclusion box: "Performance is fine. The robot misses because the POLICY learned wrong things." This shifts our focus from performance debugging to data debugging.

**Transition:** "The policy learned wrong things. What exactly did it learn?"

---

## Slide 12 -- Bug #3: Causal Confounding (TIME: 14:00 - 15:30)

Bug three is subtle. During teleoperation recording, the leader arm is visible in the camera frame. The policy learns a shortcut: instead of looking at the red block to determine where to reach, it watches the leader arm. The leader arm literally shows where to go.

At inference, the leader arm is disconnected and removed. The policy sees an unfamiliar scene and outputs erratic, random movements.

Walk through the SVG: training frame shows the leader arm in view with the attention arrow pointing to it. Inference frame shows the empty space where the leader used to be, with confused motion.

Fix: reposition cameras so the leader arm is physically out of frame during recording. This means re-recording the entire dataset.

Detection method: scrub through the dataset in the Rerun visualizer and look for the leader arm in the camera feeds.

**Transition:** "We re-recorded. Robot still misses. Consistently. By exactly the same amount."

---

## Slide 13 -- Bug #4: Calibration Drift -- AHA MOMENT (TIME: 15:30 - 17:30)

This is the moment that changed everything. We built compare_leader_follower.py, which reads the existing dataset and computes per-joint position offset between the leader and follower arms.

Read the output table slowly. Most joints are fine: 1 to 2 degrees offset. Then wrist_flex: 17.5 degrees mean offset, 22.3 degrees maximum. That is massive.

Do the math out loud: 17.5 degrees at the wrist translates to approximately 6 to 7 centimeters of systematic error at the gripper tip. The block is 3 centimeters wide. The gripper was consistently missing by twice the block's width.

Show the results table: after recalibration (a 10-minute procedure), the wrist_flex offset drops to 0.85 degrees. Gripper accuracy goes from plus/minus 6-7 cm to plus/minus 0.3 cm. Success rate goes from 0% to 80%.

Read the lesson callout with emphasis: "No amount of training, bigger models, or more epochs can fix a calibration error. Always verify hardware first."

We spent 3 weeks on software debugging. The answer was a 10-minute recalibration.

**Transition:** "80% success. But not 100%. What about the remaining 20%?"

---

## Slide 14 -- Bug #5: Distribution Shift (TIME: 17:30 - 19:00)

Same robot, same block, same position. But morning training versus afternoon deployment. The lighting changes: color temperature, shadows, white balance.

The policy overfitted to morning lighting conditions. It does not generalize to different lighting.

Fix: LeRobot has built-in ImageTransformsConfig with brightness, contrast, saturation, hue, and sharpness jitter. Enable it with one training flag.

Important caveat: if your task depends on color discrimination (like "grab the RED block"), disable hue jitter. Otherwise the model becomes color-invariant and cannot distinguish the red block from other objects.

**Transition:** "Let me show you the tools that helped us find all these bugs."

---

## Slide 15 -- Tools We Built (TIME: 19:00 - 20:30)

Four tools, about 600 lines of Python total, zero additional dependencies beyond what LeRobot already requires.

Go through each card:
- compare_leader_follower.py: the hero tool. Reads the dataset, computes per-joint offsets. This found the 17.5 degree calibration drift.
- evaluate_dataset_quality.py: IQR-based outlier detection on joint velocities. Flags noisy episodes.
- read_leader_pos.py and read_follower_pos.py: static calibration checks. Put the arm in a known position, read the encoders, verify.

Read the callout: "The dataset is your ground truth. If the recorded data is wrong, no model can fix it."

**Transition:** "Beyond tools, you need to read your training metrics correctly."

---

## Slide 16 -- Reading Training Metrics (TIME: 20:30 - 22:00)

Many people look at the training loss curve going down and think "great, it's learning." But what does the number actually mean for the robot?

l1_loss of 0.068 means: average prediction error is 6.8% of the joint motion range. For a typical servo with 180 degree range, that is about 12 degrees per joint. Through the kinematic chain, that becomes 6-7 cm of positional error at the gripper.

Walk through the loss scale bar: under 0.03 is reliable grasp territory. Our initial 0.068 was in the "close but unreliable" zone. Above 0.10 is essentially random motion.

The conversion formula at the bottom: l1_loss times servo_range gives per-joint error, then kinematic chain multiplication gives gripper error. This mental model lets you translate abstract loss numbers into physical robot behavior.

**Transition:** "We got the loss down. But some scenarios were still hard."

---

## Slide 17 -- Hard Example Mining (TIME: 22:00 - 24:00)

After fixing calibration and adding augmentation: 80% success on horizontal grasps, but only 20% on rotated blocks. Why?

Analysis of the dataset: only 5% of episodes involved block rotation. The rule of thumb from the robotics learning community is that a scenario needs 15-20% representation in the dataset for the policy to learn it reliably.

We added 25 rotation-focused episodes, bringing rotation representation from 5% to 17%. Success on rotated blocks jumped from 20% to about 70%.

Point to the bar chart: the visual difference between 5% and 17% is small, but the behavioral impact is massive.

Read the rule of thumb callout. This is one of the most practical takeaways from the talk.

**Transition:** "Let me show you these tools in action."

---

## Slide 18 -- Dataset Viz Demo (TIME: 24:00 - 25:30)

**[LIVE DEMO or screenshot]**

Switch to Rerun visualization. Show:
1. Three camera streams synchronized
2. Joint position plots over time
3. Scrubbing through an episode timeline
4. Pointing out where you can spot calibration errors (joint position mismatch between leader/follower traces)
5. Pointing out where you can see the leader arm in the camera frame (if you have a "before" dataset)

This is the single most useful debugging tool in the pipeline. If you take away one tool from this talk, make it dataset visualization.

The command is simple: lerobot-dataset-viz with repo-id and episode-index.

**Transition:** "And now, the moment you have been waiting for."

---

## Slide 19 -- Robot Demo (TIME: 25:30 - 27:00)

**[PLAY VIDEO -- approximately 30 seconds]**

First clip: successful grasp. The arm reaches for the block, closes the gripper, lifts, moves to the box, opens gripper, releases. Clean execution.

Second clip: failure case. Block is rotated 45 degrees. The gripper approaches at the wrong angle and pushes the block instead of grasping it. This is from before we added the rotation examples.

Showing both success and failure is intentional. Honesty about failure modes is how the community learns.

Pause briefly for audience reaction.

**Transition:** "So what did we learn from all of this?"

---

## Slide 20 -- Lessons Learned (TIME: 27:00 - 28:30)

Two columns. Walk through each card in the "What Worked" column first, then "What Didn't."

What Worked:
- Profile first: the 30Hz loop breakdown told us compute was not the problem.
- Dataset as ground truth: every single bug was found by interrogating the data, not the model.
- Image augmentation: one flag fixed lighting sensitivity.
- Diagnostic tools: 600 lines of Python saved weeks of guesswork.

What Didn't Work:
- Bigger models: we switched to SmolVLA when the real problem was 17.5 degrees of calibration drift. Model size does not fix data quality.
- More epochs: trained for 200k steps, loss plateaued. The problem was data distribution, not underfitting.
- Removing wrist camera: we thought fewer inputs would simplify learning. Wrong. The wrist perspective is critical for grasping.
- Ignoring hardware: spent 3 weeks on software when the answer was a 10-minute recalibration.

**Transition:** "For those of you thinking 'this sounds painful,' there is an easier path."

---

## Slide 21 -- Cyberwave (TIME: 28:30 - 29:30)

Cyberwave is a platform that handles the painful parts we just talked about. Pre-configured digital twins for simulation, cloud training pipelines so you do not need to worry about GPU memory, and automated deployment from simulation back to real hardware.

Walk through the comparison table: what took us weeks, Cyberwave automates. Calibration is auto-detected, cameras are pre-configured, training runs on cloud GPUs, augmentation is built-in, deployment is one-click, and there is a diagnostic dashboard.

They have a specific SO101 tutorial for voice-controlled pick-and-place.

This is not about skipping the learning. Understanding the fundamentals is valuable. But when you need production results, platforms like this let you focus on the task instead of the plumbing.

Links on screen: cyberwave.com and the tutorial URL.

**Transition:** "And with that..."

---

## Slide 22 -- Thank You & Q&A (TIME: 29:30 - 30:00)

Thank the audience. Read the closing tagline: "Built with love, frustration, and a 17.5 degree calibration drift."

Key takeaways to repeat:
1. Hardware first. Always.
2. Profile before optimizing.
3. Your dataset is your ground truth.
4. Sometimes the answer is a 10-minute recalibration, not a bigger model.

Open for questions. Repo link on screen.

---

## Backup Notes

### If running short on time (< 3 minutes remaining at slide 18):
- Skip live demo on slide 18, use the screenshot only
- Compress slide 17 (hard example mining) to 60 seconds
- Keep video on slide 19 to one clip (success only)

### If running long (> 5 minutes remaining at slide 20):
- Expand lessons learned with audience interaction: "Who has had a similar experience with calibration?"
- Add detail about the specific STS3215 motor calibration procedure
- Take 1-2 inline questions before slide 21

### Common anticipated questions:
1. "Why ACT over diffusion policies?" -- ACT is smaller, fits on 16GB, trains in 28 minutes. Diffusion policies (like Diffusion Policy or DDPM variants) are more expressive but need more VRAM and training time. For a budget setup, ACT is the practical starting point.

2. "How many episodes did you record total?" -- About 75 episodes of 10-15 seconds each. Roughly 15 minutes of robot teleoperation data total. ACT is data-efficient for single-task learning.

3. "Does temporal ensembling help?" -- We did not use it (n_action_steps=100 with temporal_ensemble_coeff=None). It can improve smoothness but requires n_action_steps=1, which means a forward pass every step and higher GPU utilization. Worth trying if you have the compute budget.

4. "What about sim-to-real?" -- We went pure real-world data. Sim-to-real with a digital twin of the SO101 is possible (and is what Cyberwave offers), but the domain gap between simulation and a 3D-printed robot with servo compliance is nontrivial.

5. "How do you handle gripper force control?" -- We do not. The STS3215 servos provide position control only. Gripper force is determined by the compliance of the 3D-printed gripper fingers. This limits us to rigid objects of predictable size.

---

## Live Demo Commands (keep terminal ready)

### Dataset visualization (for dataset-viz slide)
```bash
# Show a good episode (pick one you've verified looks clean)
source .venv/bin/activate
lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=10

# Fallback: show a different episode if 10 doesn't look good
lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=25
```

In Rerun:
- Use timeline scrubber to show the full episode
- Point out the 3 camera views (front/wrist/right)
- Point out joint position plots at bottom
- Scroll to the grasp moment — show how wrist cam sees the block up close

### Fallback
If Rerun doesn't launch or crashes: switch to the screenshot in `assets/dataset-viz-fallback.png`
