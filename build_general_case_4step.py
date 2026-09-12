#!/usr/bin/env python3
"""Build general_case_4step.html + manifest, matching 4step.html's style/pattern."""
import html
import json

PROMPTS_JSON = "/data/home/sunsean/work/h3_sglang_8step_preview/prompts_general_case12.json"
with open(PROMPTS_JSON) as f:
    _examples = json.load(f)["examples"]
PROMPTS = [(e["id"], e["category"], e["seed"], e["prompt"]) for e in _examples]

ARMS = [
    ("gate800", "Our 4-step (gate800)", "our4step_gate800", "ours4"),
    ("turbo8", "LightX2V Turbo8", "turbo8", "turbo8"),
    ("vdn", "VDN-H3 8-step", "vdn_h3_8step", "vdn"),
]

SOURCE_PATHS = {
    "gate800": "phase5_lora_snapshots/phase5_c_gate800.safetensors "
               "(h3_8step_threeway_compare/scripts/gen_eval.py --num-steps 4 --video-flow-shift 6.0)",
    "turbo8": "public_turbo/minimax_h3_fl2v_turbo_8step_v1.0_768p_bf16.safetensors "
              "(h3_8step_threeway_compare/scripts/gen_eval.py --num-steps 8 --video-flow-shift 6.0, auto-detected LoRA scale)",
    "vdn": "openvdn_compare checkpoint=ckpts/stage-dmd-step-250, config=configs/inference/8nfe.yaml, "
           "VDN_OFFLOAD_MODE=shard2 (2-GPU weight-sharded), num_frames=107, warmup_steps=2",
}

VERDICTS = {
    "g_two_friends_cafe_chat":     ("tie", "vdn"),
    "g_city_street_walk":          ("tie", "tie"),
    "g_dog_park_play":             ("tie", "tie"),
    "g_kitchen_chopping_veg":      ("gate800", "gate800"),
    "g_jogger_park_path":          ("tie", "gate800"),
    "g_cyclist_road":              ("tie", "tie"),
    "g_train_window_countryside":  ("turbo8", "tie"),
    "g_living_room_reading":       ("tie", "gate800"),
    "g_mountain_landscape_pan":    ("tie", "tie"),
    "g_hands_pouring_coffee":      ("turbo8", "tie"),
    "g_office_typing":             ("gate800", "gate800"),
    "g_market_stall_browsing":     ("tie", "gate800"),
}
VERDICT_LABEL = {"gate800": "gate800 wins", "turbo8": "Turbo8 wins", "vdn": "VDN-H3 wins", "tie": "tie"}
VERDICT_CLASS = {"gate800": "v-ours4", "turbo8": "v-turbo8", "vdn": "v-vdn", "tie": "v-tie"}

toc = "".join(f'<a href="#p-{pid}">{pid}</a>' for pid, _, _, _ in PROMPTS)

sections = []
for pid, cat, seed, prompt_text in PROMPTS:
    row_id = f"cmp-{pid}"
    audio_opts = "".join(
        f'<label><input type="radio" name="audio-{row_id}" value="{key}"'
        f'{" checked" if key == "mute" else ""}> {label}</label>'
        for key, label in [("mute", "Mute all")] + [(a[0], a[1]) for a in ARMS]
    )
    cells = ""
    for key, label, suffix, cls in ARMS:
        fname = f"{pid}_{suffix}.mp4"
        cells += (
            f'<div class="cell"><span class="arm-label {cls}">{html.escape(label)}</span>'
            f'<video controls playsinline preload="none" data-arm="{key}" '
            f'src="assets/video/{fname}" muted></video></div>'
        )
    vs_turbo, vs_vdn = VERDICTS[pid]
    verdict_html = (
        f'<span class="verdict-chip {VERDICT_CLASS[vs_turbo]}">vs Turbo8: {VERDICT_LABEL[vs_turbo]}</span>'
        f'<span class="verdict-chip {VERDICT_CLASS[vs_vdn]}">vs VDN-H3: {VERDICT_LABEL[vs_vdn]}</span>'
    )
    prompt_html = html.escape(prompt_text).replace("\n", "<br>")
    sections.append(
        f'<section class="prompt-block" id="p-{pid}"><h3 class="prompt-id">{pid} '
        f'<span class="cat">({cat}, seed {seed})</span></h3>'
        f'<div class="verdict-row">{verdict_html}</div>'
        f'<details class="prompt-text"><summary>Prompt text</summary><div class="prompt-body">{prompt_html}</div></details>'
        f'<div class="sync-row" id="sync-{row_id}"><div class="row-controls" data-row-id="{row_id}">'
        f'<button type="button" class="row-play">▶ Play row</button>'
        f'<button type="button" class="row-restart">⟲ Restart</button>'
        f'<span class="row-audio-label">Audio:</span>'
        f'<span class="row-audio" role="radiogroup" aria-label="Choose audio source">{audio_opts}</span></div>'
        f'<div class="row three">{cells}</div></div></section>'
    )

manifest = {
    "purpose": "Generalization spot-check: 12 prompts deliberately outside the fire/physics/impact "
               "training distribution, comparing our 4-step DMD LoRA (gate800) against LightX2V Turbo8 "
               "and OpenVDN VDN-H3 (both 8-step).",
    "resolution": "1344x768, 24fps",
    "frame_count_note": "VDN outputs probe at 107 frames; gate800/turbo8 outputs probe at 106 frames "
                        "-- consistent with the same muxer/container-level cosmetic difference already "
                        "documented for the sglang-vs-diffusers comparison; not a content-duration issue.",
    "summary": {
        "gate800_vs_turbo8": {"wins": 2, "losses": 2, "ties": 8},
        "gate800_vs_vdn_h3": {"wins": 5, "losses": 1, "ties": 6},
        "overall": "gate800 is roughly on par with Turbo8 and slightly ahead of VDN-H3 on this "
                   "12-prompt qualitative spot-check. gate800 is not claimed to be globally better "
                   "than either baseline.",
        "caveat": "Qualitative generalization check on 12 clips across three different distillation "
                  "efforts at different step counts (4 vs 8) -- not a rigorous benchmark.",
    },
    "per_prompt_verdicts": {
        pid: {"vs_turbo8": VERDICTS[pid][0], "vs_vdn_h3": VERDICTS[pid][1]} for pid, _, _, _ in PROMPTS
    },
    "prompts": [{"id": pid, "category": cat, "seed": seed, "prompt": text} for pid, cat, seed, text in PROMPTS],
    "arms": {key: {"label": label, "source": SOURCE_PATHS[key]} for key, label, _, _ in ARMS},
}
with open("general_case_4step_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

html_out = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MiniMax-H3 General-Case 4-step Comparison Gallery</title><style>
:root{{color-scheme:light dark;--bg:#0e0f12;--panel:#17191d;--panel2:#1e2126;--text:#e8e8ea;--muted:#9aa0aa;--accent:#5fb0ff;--turbo:#ff9d4d;--vdn:#c98bff;--ours4:#ffd24d;--ours8:#5fd97a;--border:#2b2f36;--nav-h:46px;}}
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
.summary-box{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin-bottom:22px}}
.summary-box h2{{margin:0 0 12px;font-size:1.05rem}}
.summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-bottom:12px}}
.summary-card{{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:12px 14px}}
.summary-card .label{{color:var(--muted);font-size:.75rem;text-transform:uppercase;letter-spacing:.03em;margin-bottom:6px}}
.summary-card .score{{font-size:1.15rem;font-weight:700}}
.summary-card .score .w{{color:var(--ours8)}}
.summary-card .score .l{{color:#ff8080}}
.summary-card .score .t{{color:var(--muted)}}
.summary-box .verdict{{font-size:.92rem;margin:10px 0}}
.summary-box .caveat{{font-size:.8rem;color:var(--muted);border-top:1px solid var(--border);padding-top:10px;margin-top:10px}}
section{{margin-bottom:44px;scroll-margin-top:var(--nav-h)}}
section.prompt-block{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:22px;max-width:100%}}
h3.prompt-id{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:1.05rem;margin:0 0 10px;color:var(--accent);overflow-wrap:anywhere}}
h3.prompt-id .cat{{color:var(--muted);font-weight:400;font-size:.8rem}}
.verdict-row{{margin-bottom:10px;display:flex;flex-wrap:wrap;gap:8px}}
.verdict-chip{{font-size:.72rem;font-weight:600;padding:3px 10px;border-radius:999px;border:1px solid var(--border)}}
.v-ours4{{color:var(--ours4);background:rgba(255,210,77,.12);border-color:rgba(255,210,77,.4)}}
.v-turbo8{{color:var(--turbo);background:rgba(255,157,77,.12);border-color:rgba(255,157,77,.4)}}
.v-vdn{{color:var(--vdn);background:rgba(201,139,255,.12);border-color:rgba(201,139,255,.4)}}
.v-tie{{color:var(--muted);background:rgba(154,160,170,.1);border-color:var(--border)}}
.prompt-text{{margin-bottom:12px;font-size:.82rem}}
.prompt-text summary{{cursor:pointer;color:var(--muted)}}
.prompt-text summary:hover{{color:var(--text)}}
.prompt-body{{margin-top:8px;padding:10px 12px;background:var(--panel2);border:1px solid var(--border);border-radius:8px;color:var(--muted);white-space:pre-wrap;overflow-wrap:anywhere}}
.arm-label{{font-weight:700;font-size:.82rem;letter-spacing:.03em;text-transform:uppercase;padding:3px 10px;border-radius:6px;display:inline-block;margin-bottom:6px}}
.arm-label.turbo8{{background:rgba(255,157,77,.15);color:var(--turbo);border:1px solid rgba(255,157,77,.4)}}
.arm-label.vdn{{background:rgba(201,139,255,.15);color:var(--vdn);border:1px solid rgba(201,139,255,.4)}}
.arm-label.ours4{{background:rgba(255,210,77,.15);color:var(--ours4);border:1px solid rgba(255,210,77,.4)}}
.row{{display:grid;gap:14px}}
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
<header class="page"><h1>MiniMax-H3 general-case 4-step comparison</h1>
<p>Our 4-step (gate800) / LightX2V Turbo8 / VDN-H3 8-step, across 12 prompts deliberately outside the
fire/physics/impact training niche (human interaction, camera motion, animal motion, object interaction,
human motion, indoor lifestyle, landscape) &mdash; a generalization spot-check. Rows play/pause/restart
together &mdash; use the row controls or click any video's own controls. All videos start muted; use a
row's audio picker (or a video's own unmute control) to hear exactly one at a time.</p>
<div class="links"><a href="4step.html">4-step gallery (physics prompts)</a> <a href="6step.html">6-step gallery</a> <a href="index.html">All galleries</a></div>
</header>
<nav class="toc">{toc}</nav>
<main>
<div class="summary-box">
<h2>Result summary</h2>
<div class="summary-grid">
<div class="summary-card"><div class="label">gate800 vs Turbo8</div><div class="score"><span class="w">2 wins</span> / <span class="l">2 losses</span> / <span class="t">8 ties</span></div></div>
<div class="summary-card"><div class="label">gate800 vs VDN-H3</div><div class="score"><span class="w">5 wins</span> / <span class="l">1 loss</span> / <span class="t">6 ties</span></div></div>
</div>
<div class="verdict"><strong>Overall:</strong> gate800 is roughly on par with Turbo8 and slightly ahead of VDN-H3 on this 12-prompt qualitative spot-check. This is not a claim that gate800 is globally better than either baseline &mdash; per-prompt verdicts (chips above each row) show a mix of wins, losses, and ties in both directions.</div>
<div class="caveat"><strong>Caveat:</strong> this is a qualitative generalization check across three different distillation efforts at different step counts (4 vs. 8) on 12 clips &mdash; not a rigorous benchmark. Judge from the videos themselves; the counts summarize, they don't replace, that review.</div>
</div>
{"".join(sections)}
</main>
<footer>Manifest: <a href="general_case_4step_manifest.json">general_case_4step_manifest.json</a> (exact source paths/checkpoints/commands for all three arms, full prompt text, per-prompt verdicts).
<br>Prompts outside the physics-heavy training distribution used for the other galleries on this site &mdash; see <a href="4step.html">4-step gallery</a> for the original 14 held-out (fire/physics/impact-focused) prompts.</footer>
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
with open("general_case_4step.html", "w") as f:
    f.write(html_out)
print("wrote general_case_4step.html and general_case_4step_manifest.json")
