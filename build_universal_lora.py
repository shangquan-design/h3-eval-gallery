"""Build universal_lora.html: T2VA / FL2VA / Ref2VA comparison gallery for
the universal multi-task LoRA diagnostic campaign (gate50 / gate100 / v2
vs the existing single-task baselines and Base H3). Rows sync play/pause/
restart/seek; one audio-source radio group per row (mute by default).
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
EXAMPLES = json.loads(Path("/data/home/sunsean/work/h3_sft_dmd/eval_three_modes_examples.json").read_text())

ARM_META = {
    "gate250":       {"label": "gate250 (existing baseline)", "cls": "baseline"},
    "ref2va_smoke":  {"label": "ref2va_smoke (existing baseline)", "cls": "baseline"},
    "u50":           {"label": "universal gate50", "cls": "u50"},
    "u100":          {"label": "universal gate100", "cls": "u100"},
    "v2":            {"label": "universal_v2 (gate50)", "cls": "v2"},
    "base":          {"label": "Base H3 (no LoRA)", "cls": "base"},
}
T2VA_FL2VA_ARMS = ["gate250", "u50", "u100", "v2", "base"]
REF2VA_ARMS = ["ref2va_smoke", "u50", "u100", "v2", "base"]

MODE_TITLE = {"t2va": "T2VA (text-only)", "fl2va": "FL2VA (first+last frame conditioned)", "ref2va": "Ref2VA (reference-image conditioned)"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def truncate(s, n=200):
    return s if len(s) <= n else s[:n] + "..."


def row_id(mode, ex_id):
    return f"{mode}-{ex_id}"


def video_cell(mode, ex_id, arm):
    meta = ARM_META[arm]
    src = f"assets/video/universal_lora/{mode}/{ex_id}_{arm}.mp4"
    return (
        f'<div class="cell"><span class="arm-label {meta["cls"]}">{esc(meta["label"])}</span>'
        f'<video controls playsinline preload="none" data-arm="{arm}" src="{src}" muted></video></div>'
    )


def audio_radio_group(rid, arms):
    opts = ['<label><input type="radio" name="audio-' + rid + '" value="mute" checked> Mute all</label>']
    for arm in arms:
        opts.append(f'<label><input type="radio" name="audio-{rid}" value="{arm}"> {esc(ARM_META[arm]["label"])}</label>')
    return '<span class="row-audio-label">Audio:</span><span class="row-audio" role="radiogroup" aria-label="Choose audio source">' + "".join(opts) + "</span>"


def render_example_section(mode, ex, arms, ref_cell_html):
    rid = row_id(mode, ex["id"])
    n_cols = len(arms) + (1 if ref_cell_html else 0)
    row_class = "six" if n_cols >= 6 else ("five" if n_cols == 5 else "four")
    cells = (ref_cell_html or "") + "".join(video_cell(mode, ex["id"], a) for a in arms)
    return (
        f'<section class="prompt-block" id="p-{rid}">'
        f'<h3 class="prompt-id">{esc(ex["id"])} <span class="cat">({esc(ex["category"])}, seed {ex["seed"]})</span></h3>'
        f'<details class="prompt-text"><summary>Prompt text</summary><div class="prompt-body">{esc(truncate(ex["prompt"], 400))}</div></details>'
        f'<div class="sync-row" id="sync-{rid}">'
        f'<div class="row-controls" data-row-id="{rid}"><button type="button" class="row-play">&#9654; Play row</button>'
        f'<button type="button" class="row-restart">&#8635; Restart</button>'
        f'{audio_radio_group(rid, arms)}</div>'
        f'<div class="row {row_class}">{cells}</div>'
        f'</div></section>'
    )


def fl2va_ref_cell(ex_id):
    return (
        '<div class="cell reference"><span class="arm-label ref">keyframes (first / last)</span>'
        f'<img src="assets/video/universal_lora/fl2va/{ex_id}_keyframe_first.png">'
        f'<img src="assets/video/universal_lora/fl2va/{ex_id}_keyframe_last.png" style="margin-top:4px;"></div>'
    )


def ref2va_ref_cell(ex_id):
    return (
        '<div class="cell reference"><span class="arm-label ref">reference image</span>'
        f'<img src="assets/video/universal_lora/ref2va/{ex_id}_reference.png"></div>'
    )


CSS = """
:root{color-scheme:light dark;--bg:#0e0f12;--panel:#17191d;--panel2:#1e2126;--text:#e8e8ea;--muted:#9aa0aa;--accent:#5fb0ff;
--baseline:#5fb0ff;--u50:#5fd98a;--u100:#ff6b6b;--v2:#c98bff;--base:#9aa0aa;--ref:#e8c15f;--border:#2b2f36;--nav-h:46px;}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.4;overflow-x:hidden}
header.page{position:static;background:rgba(14,15,18,.96);border-bottom:1px solid var(--border);padding:14px 24px}
header.page h1{margin:0;font-size:1.25rem;overflow-wrap:anywhere}
header.page p{margin:6px 0 0;color:var(--muted);font-size:.85rem;max-width:900px}
header.page .links{margin-top:8px;font-size:.8rem;display:flex;flex-wrap:wrap;gap:4px 14px}
header.page .links a{color:var(--accent);text-decoration:none}
header.page .links a:hover{text-decoration:underline}
nav.toc{display:flex;flex-wrap:wrap;gap:6px;padding:10px 24px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:9}
nav.toc a{color:var(--muted);text-decoration:none;font-size:.78rem;padding:4px 9px;border:1px solid var(--border);border-radius:999px}
nav.toc a:hover{color:var(--text);border-color:var(--accent)}
main{max-width:1600px;margin:0 auto;padding:24px;overflow-x:hidden}
.summary-box{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin-bottom:22px;font-size:.85rem;color:var(--muted)}
.summary-box .tldr{color:var(--text);font-weight:600;margin-bottom:10px}
.summary-box ul{margin:0;padding-left:18px}
.summary-box li{margin-bottom:4px}
.summary-box li b{color:var(--text)}
h2{font-size:1.1rem;margin-top:36px;padding-bottom:6px;border-bottom:2px solid var(--border);scroll-margin-top:var(--nav-h)}
h2 .modenote{color:var(--muted);font-weight:400;font-size:.78rem}
h3.subset{font-size:.9rem;margin-top:22px;color:var(--accent)}
.badge{display:inline-block;font-size:.7rem;padding:1px 7px;border-radius:10px;margin-left:8px;vertical-align:middle}
.seen{background:#2a5;color:#000}
.heldout{background:#a52;color:#fff}
section.prompt-block{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:16px 18px;margin-bottom:18px;max-width:100%;scroll-margin-top:var(--nav-h)}
h3.prompt-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:1rem;margin:0 0 8px;color:var(--accent);overflow-wrap:anywhere}
h3.prompt-id .cat{color:var(--muted);font-weight:400;font-size:.78rem}
.prompt-text{margin-bottom:10px;font-size:.8rem}
.prompt-text summary{cursor:pointer;color:var(--muted)}
.prompt-text summary:hover{color:var(--text)}
.prompt-body{margin-top:6px;padding:8px 10px;background:var(--panel2);border:1px solid var(--border);border-radius:8px;color:var(--muted)}
.arm-label{font-weight:700;font-size:.72rem;letter-spacing:.02em;text-transform:uppercase;padding:2px 8px;border-radius:6px;display:block;width:fit-content;margin-bottom:6px}
.arm-label.baseline{background:rgba(95,176,255,.15);color:var(--baseline);border:1px solid rgba(95,176,255,.4)}
.arm-label.u50{background:rgba(95,217,138,.15);color:var(--u50);border:1px solid rgba(95,217,138,.4)}
.arm-label.u100{background:rgba(255,107,107,.15);color:var(--u100);border:1px solid rgba(255,107,107,.4)}
.arm-label.v2{background:rgba(201,139,255,.15);color:var(--v2);border:1px solid rgba(201,139,255,.4)}
.arm-label.base{background:rgba(154,160,170,.15);color:var(--base);border:1px solid rgba(154,160,170,.4)}
.arm-label.ref{background:rgba(232,193,95,.15);color:var(--ref);border:1px solid rgba(232,193,95,.4)}
.row{display:grid;gap:12px}
.row.four{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.row.five{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.row.six{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.cell{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:8px;min-width:0}
.cell.reference{background:#22201a;border-color:#463e2a}
video,.cell img{width:100%;max-width:100%;border-radius:6px;background:#000;display:block}
.row-controls{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;margin-bottom:10px;padding:7px 10px;background:var(--panel2);border:1px solid var(--border);border-radius:8px;font-size:.78rem}
.row-controls button{font:inherit;font-size:.75rem;font-weight:600;color:var(--text);background:var(--panel);border:1px solid var(--border);border-radius:999px;padding:5px 12px;cursor:pointer}
.row-controls button:hover{border-color:var(--accent)}
.row-audio{display:flex;flex-wrap:wrap;gap:2px 10px;align-items:center}
.row-audio label{display:flex;align-items:center;gap:4px;color:var(--muted);cursor:pointer}
.row-audio input{accent-color:var(--accent)}
.row-audio-label{color:var(--muted)}
footer{padding:26px 24px;color:var(--muted);font-size:.76rem;border-top:1px solid var(--border);margin-top:36px}
footer a{color:var(--accent)}
@media (max-width:700px){nav.toc{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;gap:8px;padding:8px 12px}nav.toc a{flex:0 0 auto;white-space:nowrap}}
@media (max-width:640px){.row-controls{gap:8px}main{padding:14px}section.prompt-block{padding:12px 10px}header.page{padding:12px 14px}}
"""

SYNC_JS = """
(function(){
function initSyncRows(){
  document.querySelectorAll('.sync-row').forEach(function(row){
    var videos = Array.prototype.slice.call(row.querySelectorAll('video[data-arm]'));
    if(!videos.length) return;
    var playBtn = row.querySelector('.row-play');
    var restartBtn = row.querySelector('.row-restart');
    var audioInputs = Array.prototype.slice.call(row.querySelectorAll('.row-audio input[type=radio]'));
    var syncing = false;
    var DRIFT = 0.15;
    function withSync(fn){ syncing = true; try { fn(); } finally { setTimeout(function(){ syncing = false; }, 80); } }
    function setAllTime(t){ videos.forEach(function(v){ if (Math.abs(v.currentTime - t) > 0.03) { try { v.currentTime = t; } catch(e){} } }); }
    function playAll(){ videos.forEach(function(v){ var p = v.play(); if (p && p.catch) p.catch(function(){}); }); }
    function pauseAll(){ videos.forEach(function(v){ v.pause(); }); }
    function isPlaying(){ return videos.some(function(v){ return !v.paused && !v.ended; }); }
    function updatePlayBtn(){ if (playBtn) playBtn.textContent = isPlaying() ? '\\u23f8 Pause row' : '\\u25b6 Play row'; }
    if (playBtn) {
      playBtn.addEventListener('click', function(){
        withSync(function(){ if (isPlaying()) { pauseAll(); } else { setAllTime(videos[0].currentTime); playAll(); } });
        setTimeout(updatePlayBtn, 60);
      });
    }
    if (restartBtn) {
      restartBtn.addEventListener('click', function(){
        var wasPlaying = isPlaying();
        withSync(function(){ setAllTime(0); if (wasPlaying) playAll(); else pauseAll(); });
        setTimeout(updatePlayBtn, 60);
      });
    }
    videos.forEach(function(v){
      v.addEventListener('play', function(){ if (syncing) return; withSync(function(){ setAllTime(v.currentTime); playAll(); }); setTimeout(updatePlayBtn, 60); });
      v.addEventListener('pause', function(){ if (syncing) return; withSync(function(){ pauseAll(); }); setTimeout(updatePlayBtn, 60); });
      v.addEventListener('seeked', function(){ if (syncing) return; withSync(function(){ setAllTime(v.currentTime); }); });
      v.addEventListener('timeupdate', function(){
        if (syncing) return;
        var t = v.currentTime;
        var drifted = videos.some(function(o){ return o !== v && Math.abs(o.currentTime - t) > DRIFT; });
        if (drifted) { withSync(function(){ videos.forEach(function(o){ if (o !== v && Math.abs(o.currentTime - t) > 0.03) { try { o.currentTime = t; } catch(e){} } }); }); }
      });
      v.addEventListener('ended', function(){ setTimeout(updatePlayBtn, 60); });
    });
    function selectAudioOnly(v){ videos.forEach(function(o){ if (o !== v) { o.muted = true; } }); v.muted = false; v.volume = 1; }
    function muteAll(){ videos.forEach(function(v){ v.muted = true; }); }
    audioInputs.forEach(function(radio){
      radio.addEventListener('change', function(){
        if (radio.value === 'mute') { muteAll(); return; }
        var target = radio.value;
        var match = videos.filter(function(v){ return v.getAttribute('data-arm') === target; })[0];
        if (match) selectAudioOnly(match);
      });
    });
    var suppressVolumeSync = false;
    videos.forEach(function(v){
      v.addEventListener('volumechange', function(){
        if (suppressVolumeSync) return;
        if (!v.muted) {
          suppressVolumeSync = true;
          videos.forEach(function(o){ if (o !== v) o.muted = true; });
          var arm = v.getAttribute('data-arm');
          audioInputs.forEach(function(r){ r.checked = (r.value === arm); });
          setTimeout(function(){ suppressVolumeSync = false; }, 50);
        }
      });
    });
    updatePlayBtn();
  });
}
if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', initSyncRows); }
else { initSyncRows(); }
})();
"""

html = []
html.append('<!doctype html><html lang="en"><head><meta charset="utf-8">')
html.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
html.append("<title>MiniMax-H3: Universal Multi-Task LoRA Diagnostic Gallery</title><style>" + CSS + "</style></head>")
html.append("<body>")
html.append(
    '<header class="page"><h1>MiniMax-H3: Universal multi-task LoRA diagnostic gallery</h1>'
    "<p>One LoRA trained jointly on T2VA + Ref2VA, compared against the existing single-task baselines "
    "and Base H3, across three conditioning modes and 6 prompts (2 seen in training, 4 held-out). "
    "Rows play/pause/restart/seek together; pick one audio source per row (muted by default). "
    "Visual comparison only &mdash; no automated win/loss verdicts, human review is the deciding step.</p>"
    '<div class="links"><a href="index.html">All galleries</a></div>'
    "</header>"
)
html.append('<nav class="toc"><a href="#t2va">T2VA</a><a href="#fl2va">FL2VA</a><a href="#ref2va">Ref2VA</a></nav>')
html.append("<main>")
html.append(
    '<div class="summary-box">'
    '<div class="tldr">gate50 = tiny-data sweet spot &nbsp;|&nbsp; gate100 = overtrained/overfit &nbsp;|&nbsp; '
    "universal_v2 = more diverse data but still short-trained, likely under-exploited rather than overfit.</div>"
    "<ul>"
    "<li><b>gate250 / ref2va_smoke</b> (existing single-task baseline): T2VA/FL2VA gate250 = 922 samples, SFT teacher, 250 iters; "
    "ref2va_smoke = Ref2VA-only, 15 iters, not a strong baseline.</li>"
    "<li><b>universal gate50</b>: 4 samples&times;8 repeats, 50 iters &mdash; usable, tiny-data-limited, not yet clearly overfit.</li>"
    "<li><b>universal gate100</b>: same 4 samples, 100 iters &mdash; overtrained/overfit (color blocks, blur, FL2VA endpoint-chasing).</li>"
    "<li><b>universal_v2</b>: 44 diverse samples (no repeats), 50 iters, same Base-H3 teacher &mdash; more diverse but still short-trained.</li>"
    "<li><b>Base H3</b>: no LoRA, ~50-step teacher &mdash; reference point; already follows Ref2VA conditioning somewhat on its own.</li>"
    "</ul></div>"
)

for mode, arms, ref_fn in [("t2va", T2VA_FL2VA_ARMS, None), ("fl2va", T2VA_FL2VA_ARMS, fl2va_ref_cell), ("ref2va", REF2VA_ARMS, ref2va_ref_cell)]:
    html.append(f'<h2 id="{mode}">{MODE_TITLE[mode]}</h2>')
    html.append('<h3 class="subset">Seen in training <span class="badge seen">seen</span></h3>')
    for ex in EXAMPLES["seen"]:
        ref_html = ref_fn(ex["id"]) if ref_fn else None
        html.append(render_example_section(mode, ex, arms, ref_html))
    html.append('<h3 class="subset">Held-out <span class="badge heldout">held_out</span></h3>')
    for ex in EXAMPLES["held_out"]:
        ref_html = ref_fn(ex["id"]) if ref_fn else None
        html.append(render_example_section(mode, ex, arms, ref_html))

html.append("</main>")
html.append('<footer>Source: h3_sft_dmd universal-LoRA mixed-teacher DMD campaign. No new inference was run for this page &mdash; reused stored evaluation videos.</footer>')
html.append("<script>" + SYNC_JS + "</script>")
html.append("</body></html>")

out = ROOT / "universal_lora.html"
out.write_text("\n".join(html))
print(f"wrote {out} ({out.stat().st_size} bytes)")

# sanity: verify every referenced video/image file actually exists
missing = []
for mode, arms, ref_fn in [("t2va", T2VA_FL2VA_ARMS, None), ("fl2va", T2VA_FL2VA_ARMS, True), ("ref2va", REF2VA_ARMS, True)]:
    for subset in ("seen", "held_out"):
        for ex in EXAMPLES[subset]:
            for arm in arms:
                p = ROOT / "assets" / "video" / "universal_lora" / mode / f"{ex['id']}_{arm}.mp4"
                if not p.exists():
                    missing.append(str(p))
            if ref_fn and mode == "fl2va":
                for suf in ("keyframe_first.png", "keyframe_last.png"):
                    p = ROOT / "assets" / "video" / "universal_lora" / mode / f"{ex['id']}_{suf}"
                    if not p.exists():
                        missing.append(str(p))
            if ref_fn and mode == "ref2va":
                p = ROOT / "assets" / "video" / "universal_lora" / mode / f"{ex['id']}_reference.png"
                if not p.exists():
                    missing.append(str(p))
print(f"missing referenced files: {len(missing)}")
for m in missing:
    print("  MISSING:", m)
