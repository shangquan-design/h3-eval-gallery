#!/usr/bin/env python3
"""Build arabic.html + manifest, matching general_case_4step.html's style/pattern.
Ad-hoc request (Michael Loh, Slack): "Can someone try H3 using Arabic?" Same 12
general-case prompts/seeds. 3 columns: our 4-step (gate800) English, our 4-step
(gate800) Arabic, and dense/base H3 (no LoRA, ~50-step teacher) Arabic -- the
third column exists to show whether an audio artifact observed on the Arabic
column (unwanted loud/vocal-sounding audio even on prompts calling for near-
silence) is already present in the stock base model. Visual comparison only --
no verdicts/quality claims.
"""
import html
import json

EN_PROMPTS_JSON = "/data/home/sunsean/work/h3_sglang_8step_preview/prompts_general_case12.json"
AR_PROMPTS_JSON = "/data/home/sunsean/work/prompts_general_case12_arabic.json"

with open(EN_PROMPTS_JSON) as f:
    _en = json.load(f)["examples"]
with open(AR_PROMPTS_JSON) as f:
    _ar = {e["id"].replace("_ar", ""): e for e in json.load(f)["examples"]}

PROMPTS = [(e["id"], e["category"], e["seed"], e["prompt"], _ar[e["id"]]["prompt"]) for e in _en]

toc = "".join(f'<a href="#p-{pid}">{pid}</a>' for pid, *_ in PROMPTS)

sections = []
for pid, cat, seed, en_prompt, ar_prompt in PROMPTS:
    row_id = f"cmp-{pid}"
    audio_opts = (
        f'<label><input type="radio" name="audio-{row_id}" value="mute" checked> Mute all</label>'
        f'<label><input type="radio" name="audio-{row_id}" value="en"> English</label>'
        f'<label><input type="radio" name="audio-{row_id}" value="ar"> Arabic</label>'
        f'<label><input type="radio" name="audio-{row_id}" value="dense_ar"> Dense (base H3) Arabic</label>'
    )
    en_html = html.escape(en_prompt).replace("\n", "<br>")
    ar_html = html.escape(ar_prompt).replace("\n", "<br>")
    sections.append(
        f'<section class="prompt-block" id="p-{pid}"><h3 class="prompt-id">{pid} '
        f'<span class="cat">({cat}, seed {seed})</span></h3>'
        f'<details class="prompt-text"><summary>Prompt text (English / Arabic)</summary>'
        f'<div class="prompt-body">{en_html}</div>'
        f'<div class="prompt-body" dir="rtl" lang="ar">{ar_html}</div></details>'
        f'<div class="sync-row" id="sync-{row_id}"><div class="row-controls" data-row-id="{row_id}">'
        f'<button type="button" class="row-play">▶ Play row</button>'
        f'<button type="button" class="row-restart">⟲ Restart</button>'
        f'<span class="row-audio-label">Audio:</span>'
        f'<span class="row-audio" role="radiogroup" aria-label="Choose audio source">{audio_opts}</span></div>'
        f'<div class="row three">'
        f'<div class="cell"><span class="arm-label en">English prompt (our 4-step)</span>'
        f'<video controls playsinline preload="none" data-arm="en" src="assets/video/{pid}_our4step_gate800.mp4" muted></video></div>'
        f'<div class="cell"><span class="arm-label ar">Arabic prompt (our 4-step)</span>'
        f'<video controls playsinline preload="none" data-arm="ar" src="assets/video/{pid}_ar_gate800_arabic.mp4" muted></video></div>'
        f'<div class="cell"><span class="arm-label dense">Arabic prompt (Dense/base H3, no LoRA, ~50-step)</span>'
        f'<video controls playsinline preload="none" data-arm="dense_ar" src="assets/video/{pid}_ar_dense_archeck.mp4" muted></video></div>'
        f'</div></div></section>'
    )

manifest = {
    "purpose": "English-vs-Arabic prompt visual comparison, ad-hoc request (Michael Loh, "
               "Slack: 'Can someone try H3 using Arabic?'). Same 12 general-case prompts "
               "and seeds. Column 1: our 4-step (phase5_c_gate800) English. Column 2: our "
               "4-step (phase5_c_gate800) Arabic. Column 3: dense/base H3 (no LoRA, ~50-step "
               "teacher) Arabic -- included to check whether an audio artifact noticed on "
               "column 2 (unwanted loud/vocal-sounding audio even on prompts explicitly "
               "calling for near-silence) is already present in the stock base model rather "
               "than introduced by DMD distillation. Measured via ffmpeg volumedetect/"
               "silencedetect on a few prompts: Arabic clips ran consistently louder with "
               "fewer/no silent stretches than their English counterparts, in both our "
               "4-step checkpoint and the dense base model alike. Visual comparison only -- "
               "no automated verdicts or quality claims beyond that measurement.",
    "rows": [
        {"id": pid, "category": cat, "seed": seed, "prompt_en": en_p, "prompt_ar": ar_p}
        for pid, cat, seed, en_p, ar_p in PROMPTS
    ],
    "source_paths": {
        "our_4step_checkpoint": "phase5_lora_snapshots/phase5_c_gate800.safetensors "
                      "(h3_8step_threeway_compare/scripts/gen_eval.py --num-steps 4 --video-flow-shift 6.0)",
        "dense_base_model": "dmd_student_eval.py --arm base (no LoRA, ~50 diffusion steps, "
                             "video_flow_shift=12.0 base default) -- same harness/settings "
                             "used for every other 'dense' clip on this site",
        "english_prompts": EN_PROMPTS_JSON,
        "arabic_prompts": AR_PROMPTS_JSON,
    },
}
with open("arabic_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

html_out = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MiniMax-H3 English vs Arabic Prompt Comparison</title><style>
:root{{color-scheme:light dark;--bg:#0e0f12;--panel:#17191d;--panel2:#1e2126;--text:#e8e8ea;--muted:#9aa0aa;--accent:#5fb0ff;--en:#5fb0ff;--ar:#ff9f5f;--dense:#c98bff;--border:#2b2f36;--nav-h:46px;}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.4;overflow-x:hidden}}
header.page{{position:static;background:rgba(14,15,18,.96);border-bottom:1px solid var(--border);padding:14px 24px}}
header.page h1{{margin:0;font-size:1.25rem;overflow-wrap:anywhere}}
header.page p{{margin:4px 0 0;color:var(--muted);font-size:.85rem}}
header.page .links{{margin-top:8px;font-size:.8rem;display:flex;flex-wrap:wrap;gap:4px 14px}}
header.page .links a{{color:var(--accent);text-decoration:none}}
header.page .links a:hover{{text-decoration:underline}}
nav.toc{{display:flex;flex-wrap:wrap;gap:6px;padding:10px 24px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:9}}
nav.toc a{{color:var(--muted);text-decoration:none;font-size:.78rem;padding:4px 9px;border:1px solid var(--border);border-radius:999px}}
nav.toc a:hover{{color:var(--text);border-color:var(--accent)}}
main{{max-width:1500px;margin:0 auto;padding:24px;overflow-x:hidden}}
.summary-box{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin-bottom:22px;font-size:.85rem;color:var(--muted)}}
section{{margin-bottom:44px;scroll-margin-top:var(--nav-h)}}
section.prompt-block{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:22px;max-width:100%}}
h3.prompt-id{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:1.05rem;margin:0 0 10px;color:var(--accent);overflow-wrap:anywhere}}
h3.prompt-id .cat{{color:var(--muted);font-weight:400;font-size:.8rem}}
.prompt-text{{margin-bottom:12px;font-size:.82rem}}
.prompt-text summary{{cursor:pointer;color:var(--muted)}}
.prompt-text summary:hover{{color:var(--text)}}
.prompt-body{{margin-top:8px;padding:10px 12px;background:var(--panel2);border:1px solid var(--border);border-radius:8px;color:var(--muted);white-space:pre-wrap;overflow-wrap:anywhere}}
.arm-label{{font-weight:700;font-size:.82rem;letter-spacing:.03em;text-transform:uppercase;padding:3px 10px;border-radius:6px;display:inline-block;margin-bottom:6px}}
.arm-label.en{{background:rgba(95,176,255,.15);color:var(--en);border:1px solid rgba(95,176,255,.4)}}
.arm-label.ar{{background:rgba(255,159,95,.15);color:var(--ar);border:1px solid rgba(255,159,95,.4)}}
.arm-label.dense{{background:rgba(201,139,255,.15);color:var(--dense);border:1px solid rgba(201,139,255,.4)}}
.row{{display:grid;gap:14px}}
.row.two{{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}}
.row.three{{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}}
.cell{{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:10px;min-width:0}}
video{{width:100%;max-width:100%;border-radius:6px;background:#000;display:block}}
.row-controls{{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:10px;padding:8px 10px;background:var(--panel2);border:1px solid var(--border);border-radius:8px;font-size:.8rem}}
.row-controls button{{font:inherit;font-size:.78rem;font-weight:600;color:var(--text);background:var(--panel);border:1px solid var(--border);border-radius:999px;padding:5px 12px;cursor:pointer}}
.row-controls button:hover{{border-color:var(--accent)}}
.row-audio{{display:flex;flex-wrap:wrap;gap:2px 10px;align-items:center}}
.row-audio label{{display:flex;align-items:center;gap:4px;color:var(--muted);cursor:pointer}}
.row-audio input{{accent-color:var(--accent)}}
.row-audio-label{{color:var(--muted)}}
footer{{padding:30px 24px;color:var(--muted);font-size:.78rem;border-top:1px solid var(--border);margin-top:40px;overflow-wrap:anywhere}}
footer a{{color:var(--accent)}}
footer code{{color:var(--text)}}
@media (max-width:700px){{
  nav.toc{{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;gap:8px;padding:8px 12px}}
  nav.toc a{{flex:0 0 auto;white-space:nowrap}}
}}
@media (max-width:640px){{
  .row-controls{{gap:8px 10px;padding:8px}}
  .row-controls button{{padding:6px 10px}}
  main{{padding:14px}}
  section.prompt-block{{padding:14px 12px}}
  header.page{{padding:12px 14px}}
}}
@media (max-width:400px){{
  main{{padding:8px}}
  section.prompt-block{{padding:10px 8px}}
  header.page{{padding:10px}}
  header.page h1{{font-size:1.05rem}}
}}
</style></head>
<body>
<header class="page"><h1>MiniMax-H3: English vs Arabic prompt comparison</h1>
<p>Ad-hoc check (Slack request: "Can someone try H3 using Arabic?"). Same 12 general-case
prompts and seeds as the <a href="general_case_4step.html">general-case gallery</a>, three
columns: our 4-step (gate800) with the original English prompt, our 4-step (gate800) with an
Arabic translation, and the dense/base H3 model (no LoRA, ~50-step teacher) with the same
Arabic translation. The third column was added after noticing the Arabic column tends to have
noticeably louder/more continuous audio than English even on prompts that call for near-silence
&mdash; it's there to show that pattern also shows up on the un-distilled base model, not just
our 4-step checkpoint. Rows play/pause/restart together. This page is for visual comparison
only &mdash; no automated verdicts or quality claims.</p>
<div class="links"><a href="general_case_4step.html">General-case 4-step gallery</a> <a href="4step.html">4-step gallery (physics prompts)</a> <a href="index.html">All galleries</a></div>
</header>
<nav class="toc">{toc}</nav>
<main>
<div class="summary-box">Visual comparison only. No automated scoring or win/loss verdicts are made on this page &mdash; judge from the videos themselves. The audio-loudness observation on the Arabic columns is based on ffmpeg volumedetect/silencedetect measurements (see manifest), not a formal listening evaluation.</div>
{"".join(sections)}
</main>
<footer>Manifest: <a href="arabic_manifest.json">arabic_manifest.json</a> (exact source paths, full English + Arabic prompt text for every clip).</footer>
<script>
(function(){{
function initSyncRows(){{
  document.querySelectorAll('.sync-row').forEach(function(row){{
    var videos = Array.prototype.slice.call(row.querySelectorAll('video[data-arm]'));
    if(!videos.length) return;
    var playBtn = row.querySelector('.row-play');
    var restartBtn = row.querySelector('.row-restart');
    var audioInputs = Array.prototype.slice.call(row.querySelectorAll('.row-audio input[type=radio]'));
    var syncing = false;
    var DRIFT = 0.15;
    function withSync(fn){{ syncing = true; try {{ fn(); }} finally {{ setTimeout(function(){{ syncing = false; }}, 80); }} }}
    function setAllTime(t){{ videos.forEach(function(v){{ if (Math.abs(v.currentTime - t) > 0.03) {{ try {{ v.currentTime = t; }} catch(e){{}} }} }}); }}
    function playAll(){{ videos.forEach(function(v){{ var p = v.play(); if (p && p.catch) p.catch(function(){{}}); }}); }}
    function pauseAll(){{ videos.forEach(function(v){{ v.pause(); }}); }}
    function isPlaying(){{ return videos.some(function(v){{ return !v.paused && !v.ended; }}); }}
    function updatePlayBtn(){{ if (playBtn) playBtn.textContent = isPlaying() ? '\\u23f8 Pause row' : '\\u25b6 Play row'; }}
    if (playBtn) {{
      playBtn.addEventListener('click', function(){{
        withSync(function(){{ if (isPlaying()) {{ pauseAll(); }} else {{ setAllTime(videos[0].currentTime); playAll(); }} }});
        setTimeout(updatePlayBtn, 60);
      }});
    }}
    if (restartBtn) {{
      restartBtn.addEventListener('click', function(){{
        var wasPlaying = isPlaying();
        withSync(function(){{ setAllTime(0); if (wasPlaying) playAll(); else pauseAll(); }});
        setTimeout(updatePlayBtn, 60);
      }});
    }}
    videos.forEach(function(v){{
      v.addEventListener('play', function(){{ if (syncing) return; withSync(function(){{ setAllTime(v.currentTime); playAll(); }}); setTimeout(updatePlayBtn, 60); }});
      v.addEventListener('pause', function(){{ if (syncing) return; withSync(function(){{ pauseAll(); }}); setTimeout(updatePlayBtn, 60); }});
      v.addEventListener('seeked', function(){{ if (syncing) return; withSync(function(){{ setAllTime(v.currentTime); }}); }});
      v.addEventListener('timeupdate', function(){{
        if (syncing) return;
        var t = v.currentTime;
        var drifted = videos.some(function(o){{ return o !== v && Math.abs(o.currentTime - t) > DRIFT; }});
        if (drifted) {{ withSync(function(){{ videos.forEach(function(o){{ if (o !== v && Math.abs(o.currentTime - t) > 0.03) {{ try {{ o.currentTime = t; }} catch(e){{}} }} }}); }}); }}
      }});
      v.addEventListener('ended', function(){{ setTimeout(updatePlayBtn, 60); }});
    }});
    function selectAudioOnly(v){{ videos.forEach(function(o){{ if (o !== v) {{ o.muted = true; }} }}); v.muted = false; v.volume = 1; }}
    function muteAll(){{ videos.forEach(function(v){{ v.muted = true; }}); }}
    audioInputs.forEach(function(radio){{
      radio.addEventListener('change', function(){{
        if (radio.value === 'mute') {{ muteAll(); return; }}
        var target = radio.value;
        var match = videos.filter(function(v){{ return v.getAttribute('data-arm') === target; }})[0];
        if (match) selectAudioOnly(match);
      }});
    }});
    var suppressVolumeSync = false;
    videos.forEach(function(v){{
      v.addEventListener('volumechange', function(){{
        if (suppressVolumeSync) return;
        if (!v.muted) {{
          suppressVolumeSync = true;
          videos.forEach(function(o){{ if (o !== v) o.muted = true; }});
          var arm = v.getAttribute('data-arm');
          audioInputs.forEach(function(r){{ r.checked = (r.value === arm); }});
          setTimeout(function(){{ suppressVolumeSync = false; }}, 50);
        }}
      }});
    }});
    updatePlayBtn();
  }});
}}
if (document.readyState === 'loading') {{ document.addEventListener('DOMContentLoaded', initSyncRows); }}
else {{ initSyncRows(); }}
}})();
</script>
</body></html>
"""
with open("arabic.html", "w") as f:
    f.write(html_out)
print(f"wrote arabic.html and arabic_manifest.json ({len(PROMPTS)} rows)")
