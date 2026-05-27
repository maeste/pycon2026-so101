# Presenter Notes — V3: Personal Journey

**Talk**: From LeRobot to Real Robots: What They Don't Tell You About Making a Robot Arm Grab Things
**Speaker**: Stefano Maestri
**Event**: PyCon 2026
**Duration**: 25 minutes presentation + 5 minutes Q&A
**Tone**: Honest, self-deprecating, inspiring. You are telling YOUR story. The audience is software engineers who have never touched a robot.

---

## Suggested Opening Hook (First 30 Seconds)

> "Raise your hand if you've ever watched a YouTube video of a robot doing something incredible and thought: I could build that. [pause] Great. Now keep your hand up if you've actually tried. [pause] Yeah. I see the look in your eyes. This talk is for you."

---

## Timing Guide

| Slides   | Topic                        | Time   | Cumulative |
|----------|------------------------------|--------|------------|
| 1        | Title                        | 0:30   | 0:30       |
| 2        | The promise                  | 1:30   | 2:00       |
| 3        | Day 1: Unboxing              | 2:00   | 4:00       |
| 4        | Day 3: It moves!             | 1:30   | 5:30       |
| 5        | Week 1: Recording episodes   | 2:00   | 7:30       |
| 6        | Week 2: Train and deploy     | 2:30   | 10:00      |
| 7        | The investigation            | 2:00   | 12:00      |
| 8        | The 17.5 degrees (CLIMAX)    | 3:00   | 15:00      |
| 9        | The emotional graph          | 1:30   | 16:30      |
| 10       | What I learned               | 2:00   | 18:30      |
| 11       | Tools that saved me          | 1:30   | 20:00      |
| 12       | Robot demo video             | 1:30   | 21:30      |
| 13       | Dataset visualization        | 1:00   | 22:30      |
| 14       | There IS an easier way       | 1:30   | 24:00      |
| 15       | Advice for the brave         | 1:00   | 25:00      |
| 16       | Thank you + Q&A              | 5:00   | 30:00      |

---

## Slide-by-Slide Notes

### Slide 1 — Title

- Deliver the opening hook (see above)
- Let the subtitle land: "A software engineer's honest journey into physical AI"
- Set the tone: this is a war story, not a tutorial
- **Emotional beat**: Warmth, self-deprecation

### Slide 2 — The Promise

- Show enthusiasm about the YouTube videos and papers
- Point to the "weekend timeline" — Friday evening to Sunday done
- The audience should recognize themselves in your optimism
- Get a laugh: "I even told my partner I'd be done by lunch on Saturday"
- **Emotional beat**: Shared optimism, recognition

### Slide 3 — Day 1: The Unboxing

- Describe the physical experience: box arrives, parts everywhere
- Specific details sell the story: the warped 3D-printed piece, the wrong motor model
- The Windows-only firmware tool on Fedora is a laugh line — lean into it
- "I briefly considered installing Windows. That's how desperate I was."
- **Emotional beat**: Mild concern, humor

### Slide 4 — Day 3: It Moves!

- This is a GENUINE high point. Let the excitement show
- The first time the follower arm mirrors your movement IS magical
- Then immediately undercut it: jerky, cameras disconnect, Wayland crashes
- "Welcome to embedded Linux" should land as a knowing groan
- **Emotional beat**: Joy, then reality

### Slide 5 — Week 1: Recording Episodes

- IF RUNNING SHORT: abbreviate this slide (mention the key insight about USB port shuffling and move on)
- The core insight: data collection is the REAL work, not just a prerequisite
- USB port shuffling is relatable to anyone who has debugged device enumeration
- 50 attempts to grab a block means 50 times setting up, pressing record, performing the grab, stopping
- **Emotional beat**: Grinding, determination

### Slide 6 — Week 2: "Just Train and Deploy"

- Build anticipation: training looks great, loss is low, you deploy...
- PAUSE before "and misses. Every. Single. Time."
- The systematically-to-the-right detail is important — it's not random, it's consistent
- "I tried three different models. Same result. The problem isn't the model."
- Let that line sit. The audience should feel the confusion with you
- **Emotional beat**: Excitement crashing into frustration

### Slide 7 — The Investigation

- This is the detective work slide
- nvidia-smi showing 2% GPU usage is a face-palm moment — play it up
- "Nobody told me" is both funny and true
- But fixing the device doesn't fix the accuracy — the mystery deepens
- Build tension: everything LOOKS correct. Timing is fast. Policy is running. WHY doesn't it work?
- **Emotional beat**: Determination, growing confusion

### Slide 8 — The 17.5 Degrees (CLIMAX)

- **THIS IS THE MOST IMPORTANT SLIDE. Take your time.**
- PAUSE before revealing the number
- "I wrote a 40-line Python script to compare leader and follower positions in my dataset"
- "The answer had been sitting in my data the entire time"
- PAUSE again
- "17.5 degrees. The wrist motor was off by 17.5 degrees."
- Let the audience do the math: every single episode was teaching the robot wrong physics
- "Re-calibrate. Re-record. Re-train. Same policy. Same code."
- PAUSE
- "Zero percent to eighty percent."
- **Emotional beat**: Revelation, catharsis. The audience should feel the relief WITH you
- **PAUSE for 3-5 seconds after the reveal before moving on**

### Slide 9 — The Emotional Graph

- This is a breathing slide after the climax
- Walk through the emotional arc — the audience just lived it with you
- Point to the time axis: "estimated: 1 weekend" vs "actual: 3+ weeks"
- Get a laugh: "My partner was not impressed"
- This slide validates everyone who has felt the same frustration with any project
- **Emotional beat**: Reflection, shared experience, humor

### Slide 10 — What I Learned About Physical AI

- IF RUNNING LONG: pick your top 3 points and skip the rest
- The key message: the gap between paper and robot is ALWAYS wider than you think
- "Loss curves lie" is the most counterintuitive point — explain it simply
- "0.08 loss sounds great until you realize it means 6 centimeters of error in the physical world"
- Don't be preachy. You're sharing what you learned, not lecturing
- **Emotional beat**: Wisdom earned through pain

### Slide 11 — Tools That Saved Me

- The meta-lesson: diagnostic code is the most impactful code
- "600 lines of Python" is intentionally small — that's the point
- compare_leader_follower.py found in 3 seconds what I couldn't find in 2 weeks
- This is actionable advice: write diagnostic tools BEFORE you debug
- **Emotional beat**: Practical empowerment

### Slide 12 — Robot Demo

- **[PLAY VIDEO — 90 seconds]**
- Show 2-3 successful grabs with genuine enthusiasm
- Show 1 honest failure — "It's not perfect. It's real."
- If video fails to play: describe what the audience would see, show a photo
- **Emotional beat**: Payoff, satisfaction

### Slide 13 — Dataset Visualization

- **[SHOW SCREENSHOT or live Rerun demo]**
- Quickly contrast a good episode (smooth trajectories, consistent camera angles) vs a bad one (jerky, offset)
- "Once you can SEE your data, you can FIX your data"
- Don't linger — this is a supporting slide
- **Emotional beat**: "Aha" moment

### Slide 14 — There IS an Easier Way

- This must feel NATURAL, not salesy
- Frame it as: "After I went through all of this, I discovered there was a platform that handles most of these issues"
- Be honest: "I wish I had known about this on Day 1"
- Mention Cyberwave's specific advantages that map to YOUR pain points: cloud training (no local GPU), pre-configured pipelines, built-in observability
- The voice-controlled SO101 tutorial is a concrete example the audience can try
- "Hours instead of weeks" — let your genuine surprise show
- **Emotional beat**: Relief, generosity (sharing a resource)

### Slide 15 — Advice for the Brave

- Quick hits. Don't belabor each point
- "Budget 5-10x your optimistic estimate" gets a knowing laugh
- "The robot doesn't care about your loss curve" is the thesis of the talk — deliver it with weight
- End with encouragement: this IS worth doing, despite everything
- **Emotional beat**: Encouragement, solidarity

### Slide 16 — Thank You

- Read the closing quote slowly
- "Robot learning is beautiful BECAUSE it forces you to confront reality"
- Show contact info
- Open for Q&A
- **Emotional beat**: Inspiration, openness

---

## If Running Short (< 22 minutes at slide 13)

- Expand slide 10 (What I Learned) with more examples
- Add a brief live demo of the diagnostic script if set up
- Take more time on Q&A

## If Running Long (> 22 minutes at slide 11)

- Abbreviate slide 10 to 3 points instead of 5
- Skip the "bad episode" part of slide 13
- Combine slides 14 and 15 into a single rapid-fire closing

## Backup Plans

- **Video won't play**: Have 3 still images ready. Describe the motion verbally
- **Projector issues**: The presentation works at any resolution; dark theme is legible on dim projectors
- **Time cut to 20 min**: Drop slides 5, 13; abbreviate 10 and 11

## Key Emotional Beats to Hit

1. **Recognition** (slide 2): "That's me! I've felt that optimism"
2. **Cringe** (slide 3): "Oh no, I know where this is going"
3. **Joy** (slide 4): "It works! Maybe it'll be fine!"
4. **Frustration** (slide 6): "WHY doesn't it work?"
5. **Revelation** (slide 8): "17.5 DEGREES. That was it. That was the whole problem."
6. **Relief** (slide 8): "Zero to eighty percent."
7. **Reflection** (slide 9): "We've all been there"
8. **Empowerment** (slides 11, 14, 15): "I can do this. There are tools. There is a path."

## Remember

- You are telling YOUR story. Use "I", not "we" or "one"
- Specific details > general principles (the warped 3D print, the Windows-only EXE, the 17.5 degrees)
- Humor comes from honesty, not jokes
- The audience is rooting for you. Let them

---

## Live Demo Commands (keep terminal ready)

### Dataset visualization (for the Rerun slide)
```bash
source .venv/bin/activate
lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=10

# Show a different episode if needed
lerobot-dataset-viz --repo-id=maeste/record-v6_20260525_083437 --episode-index=25
```

Walk through: "This is what a recording session looks like from the inside. Three cameras, six joints, 30 frames per second. Every frame is data the policy learns from."

### Fallback
Screenshot in `assets/dataset-viz-fallback.png` — pre-captured before the talk.
