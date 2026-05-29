#!/usr/bin/env python3
"""
Export training loss curves to a self-contained HTML chart styled for the
PyCon talk slides (dark theme, Chart.js, on-brand colors).

Parses the loss time-series directly from each run's output.log (no wandb
auth needed). lerobot logs lines like:
    Training: ... 1000/40000 [...] step:1K ... loss:2.024 grdn:64.730 ...

Emits three story-driven charts:
  1. Loss converging (a healthy training run)
  2. Low loss but the robot fails (the "loss lies" trap)
  3. Pre/post calibration comparison (same loss, different success)

Usage:
    python claudedocs/export_wandb_curves.py
"""

import json
import re
import sys
from pathlib import Path

# job_name → (output.log path, display label)
RUNS = {
    "act_v6": ("outputs/train/act_v6/wandb/latest-run/files/output.log", "v6 (pre-rotation)"),
    "act_v6_rotation": ("outputs/train/act_v6_rotation/wandb/latest-run/files/output.log", "v6 + rotation"),
    "act_v6_robust": ("outputs/train/act_v6_robust/wandb/latest-run/files/output.log", "v6 + augmentation"),
}

# Matches: "1000/40000" (exact step) ... "loss:2.024" ... "grdn:64.730"
STEP_RE = re.compile(r"(\d+)/\d+\s*\[")
LOSS_RE = re.compile(r"loss:([0-9.]+)")
GRDN_RE = re.compile(r"grdn:([0-9.]+)")


def parse_log(path: str):
    p = Path(path)
    if not p.exists():
        print(f"  WARN: {path} not found, skipping", file=sys.stderr)
        return []
    points = []
    for line in p.read_text(errors="ignore").splitlines():
        if "loss:" not in line:
            continue
        loss_m = LOSS_RE.search(line)
        step_m = STEP_RE.search(line)
        grdn_m = GRDN_RE.search(line)
        if loss_m and step_m:
            points.append({
                "step": int(step_m.group(1)),
                "loss": float(loss_m.group(1)),
                "grad": float(grdn_m.group(1)) if grdn_m else None,
            })
    # Dedup by step (keep last), sort
    by_step = {pt["step"]: pt for pt in points}
    return [by_step[s] for s in sorted(by_step)]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Training Curves — PyCon SO101</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
<style>
:root {
  --bg: #0a0a14; --surface: #12121f; --border: #1e1e3a;
  --text: #e2e8f0; --text-muted: #94a3b8;
  --primary: #4f8cff; --secondary: #a855f7;
  --success: #22c55e; --warning: #f59e0b; --danger: #ef4444;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); padding:2rem; }
h1 { font-size:2rem; font-weight:900; background:linear-gradient(135deg,var(--primary),var(--secondary)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.5rem; }
.sub { color:var(--text-muted); margin-bottom:2rem; }
.chart-card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1.5rem 2rem; margin-bottom:2rem; max-width:900px; }
.chart-card h2 { font-size:1.3rem; margin-bottom:0.3rem; color:var(--text); }
.chart-card .note { color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem; }
.chart-wrap { position:relative; height:340px; }
.callout { background:rgba(239,68,68,0.1); border-left:4px solid var(--danger); padding:1rem 1.2rem; border-radius:6px; margin-top:1rem; font-size:0.95rem; }
.callout strong { color:var(--danger); }
.callout-good { background:rgba(34,197,94,0.1); border-left-color:var(--success); }
.callout-good strong { color:var(--success); }
.metric-row { display:flex; gap:2rem; margin-top:1rem; flex-wrap:wrap; }
.metric { text-align:center; }
.metric .v { font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700; }
.metric .l { font-size:0.8rem; color:var(--text-muted); }
.tip { color:var(--text-muted); font-size:0.85rem; margin-top:1rem; font-style:italic; }
</style>
</head>
<body>
  <h1>Training Curves</h1>
  <p class="sub">Parsed from training logs &middot; styled for the talk &middot; screenshot these or embed directly</p>

  <div class="chart-card">
    <h2>1. Loss converges &mdash; training looks healthy</h2>
    <p class="note">train/loss over steps. Smooth descent to a plateau = the model learned the demos.</p>
    <div class="chart-wrap"><canvas id="chartConverge"></canvas></div>
    <div class="callout callout-good">
      <strong>What you'd conclude:</strong> "Training worked. Loss is low (~0.08). Ship it."
    </div>
  </div>

  <div class="chart-card">
    <h2>2. Low loss &mdash; but the robot misses every time</h2>
    <p class="note">Same healthy curve. The robot still missed the block by 6-7cm. Systematically.</p>
    <div class="chart-wrap"><canvas id="chartTrap"></canvas></div>
    <div class="metric-row">
      <div class="metric"><div class="v" style="color:var(--success)">0.078</div><div class="l">final loss (looks great)</div></div>
      <div class="metric"><div class="v" style="color:var(--danger)">6-7cm</div><div class="l">physical miss</div></div>
      <div class="metric"><div class="v" style="color:var(--danger)">0%</div><div class="l">grasp success</div></div>
    </div>
    <div class="callout">
      <strong>The trap:</strong> l1_loss = 0.068 &rarr; ~6.8% of motion range &rarr; ~12&deg; per joint &rarr; ~6-7cm at the gripper. A "good" loss can still mean total failure if calibration is wrong. <strong>The loss curve lies.</strong>
    </div>
  </div>

  <div class="chart-card">
    <h2>3. Same code, same loss &mdash; calibration changes everything</h2>
    <p class="note">Runs before and after fixing the 17.5&deg; wrist_flex drift. Loss curves land in the same place. Success rate: night and day.</p>
    <div class="chart-wrap"><canvas id="chartCalib"></canvas></div>
    <div class="metric-row">
      <div class="metric"><div class="v" style="color:var(--danger)">0%</div><div class="l">before re-calibration</div></div>
      <div class="metric"><div class="v" style="color:var(--success)">80%</div><div class="l">after re-calibration</div></div>
      <div class="metric"><div class="v" style="color:var(--text-muted)">~0.08</div><div class="l">loss (both)</div></div>
    </div>
    <div class="callout callout-good">
      <strong>The lesson:</strong> The fix wasn't in the model or the loss. It was 17.5&deg; of physical calibration drift. Diagnostics &gt; bigger models.
    </div>
  </div>

  <p class="tip">Tip: open in browser, screenshot each card for slides, or copy a &lt;canvas&gt; block (Chart.js is CDN-loaded).</p>

<script>
const DATA = __DATA__;
const gridColor = 'rgba(148,163,184,0.12)';
const tickColor = '#94a3b8';
Chart.defaults.color = tickColor;
Chart.defaults.font.family = "'Inter', sans-serif";

function baseOpts(yLabel, opts={}) {
  return {
    responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{ labels:{ font:{size:13} } } },
    scales:{
      x:{ title:{display:true,text:'training steps',color:tickColor}, grid:{color:gridColor} },
      y:Object.assign({ title:{display:true,text:yLabel,color:tickColor}, grid:{color:gridColor} }, opts.y||{})
    }
  };
}

const main = DATA['act_v6'] || Object.values(DATA)[0];
const mainPts = main ? main.points : [];

if (document.getElementById('chartConverge') && mainPts.length) {
  new Chart(document.getElementById('chartConverge'), {
    type:'line',
    data:{ datasets:[{
      label:'train/loss',
      data: mainPts.map(p=>({x:p.step,y:p.loss})),
      borderColor:'#4f8cff', backgroundColor:'rgba(79,140,255,0.1)',
      borderWidth:2, pointRadius:0, tension:0.3, fill:true
    }]},
    options: baseOpts('loss')
  });
}

// Chart 2: same curve, zoomed to show the plateau "looks great" region
if (document.getElementById('chartTrap') && mainPts.length) {
  // zoom into the converged region (skip the early spike) for dramatic "it's flat and low"
  const tail = mainPts.filter(p=>p.step >= 4000);
  new Chart(document.getElementById('chartTrap'), {
    type:'line',
    data:{ datasets:[{
      label:'train/loss (converged region)',
      data: tail.map(p=>({x:p.step,y:p.loss})),
      borderColor:'#22c55e', backgroundColor:'rgba(34,197,94,0.08)',
      borderWidth:2, pointRadius:0, tension:0.3, fill:true
    }]},
    options: baseOpts('loss (flat & low — looks perfect!)', {y:{suggestedMin:0, suggestedMax:0.3}})
  });
}

const COLORS = {'act_v6':'#ef4444','act_v6_rotation':'#22c55e','act_v6_robust':'#a855f7'};
const LABELS = {'act_v6':'Before fix (0% success)','act_v6_rotation':'After fix (80% success)','act_v6_robust':'+ augmentation'};
if (document.getElementById('chartCalib')) {
  const datasets = Object.keys(DATA).map(job=>({
    label: LABELS[job] || DATA[job].label,
    data: DATA[job].points.map(p=>({x:p.step,y:p.loss})),
    borderColor: COLORS[job] || '#4f8cff',
    backgroundColor:'transparent',
    borderWidth:2, pointRadius:0, tension:0.3
  }));
  new Chart(document.getElementById('chartCalib'), {
    type:'line', data:{datasets}, options: baseOpts('train/loss', {y:{suggestedMax:1.0}})
  });
}
</script>
</body>
</html>
"""


def main():
    histories = {}
    for job, (logpath, label) in RUNS.items():
        pts = parse_log(logpath)
        if pts:
            histories[job] = {"label": label, "points": pts}
            print(f"  {job}: {len(pts)} points, "
                  f"step {pts[0]['step']}->{pts[-1]['step']}, "
                  f"loss {pts[0]['loss']:.3f}->{pts[-1]['loss']:.3f}", file=sys.stderr)

    if not histories:
        print("No logs parsed.", file=sys.stderr)
        sys.exit(1)

    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(histories))
    out = "claudedocs/training_curves.html"
    Path(out).write_text(html)
    print(f"\nWrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
