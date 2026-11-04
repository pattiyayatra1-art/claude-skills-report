"""TikTok talking-head render: jump cuts + punch-in zoom + grade + ASS subtitles + emoji stickers + music bed.

Usage: render.py plan.json out.mp4 [--preview SECONDS] [--no-music]

plan.json:
{
  "source": "...mp4", "voice": "...wav", "music": "...wav" | null,
  "keep": [[start, end, zoom], ...],            # source seconds, zoom 1.0 / 1.12 ...
  "subs": [{"s": src_start, "e": src_end, "text": "...", "hl": ["word", ...]}, ...],
  "stickers": [{"t": src_time, "dur": 1.6, "file": "...mov", "x": 700, "y": 260}, ...],
  "hook": {"text": "...", "dur": 2.8} | null
}
Times for subs/stickers are SOURCE times; they are remapped onto the cut timeline here.
"""
import json, subprocess, sys, os

plan = json.load(open(sys.argv[1]))
out = sys.argv[2]
preview = None
if "--preview" in sys.argv:
    preview = float(sys.argv[sys.argv.index("--preview") + 1])
no_music = "--no-music" in sys.argv
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
W, H, FPS = 1080, 1920, 30

keep = plan["keep"]
# cumulative map from source time -> output time
offsets, acc = [], 0.0
for a, b, z in keep:
    offsets.append((a, b, acc)); acc += b - a
total = acc


def remap(t):
    for a, b, o in offsets:
        if a <= t <= b:
            return o + (t - a)
    # snap to next kept segment start
    for a, b, o in offsets:
        if t < a:
            return o
    return total


def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# ---------- ASS subtitles ----------
ass = os.path.splitext(out)[0] + ".ass"
lines = [
    "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    # white, thick black outline, soft shadow; bottom-centre above TikTok caption area
    "Style: Sub,Kanit ExtraBold,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,8,3,2,80,80,430,1",
    "Style: Hook,Kanit ExtraBold,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,26,0,8,70,70,330,1",
    "Style: Card,Kanit Bold,64,&H00FFFFFF,&H00FFFFFF,&HB4000000,&H00000000,0,0,0,0,100,100,0,0,3,22,0,8,90,90,250,1",
    "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
for sb in plan["subs"]:
    s, e = remap(sb["s"]), remap(sb["e"])
    if e - s < 0.15:
        continue
    text = sb["text"]
    for w in sb.get("hl", []):  # keyword highlight in TikTok yellow
        text = text.replace(w, "{\\c&H00F2FF&}" + w + "{\\c&HFFFFFF&}", 1)
    # pop-in: start at 85% scale, ease to 100% in 120ms
    lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Sub,,0,0,0,,{{\\fscx85\\fscy85\\t(0,120,\\fscx100\\fscy100)}}{text}")
hook = plan.get("hook")
if hook:
    # yellow box with dark text, drops in from above
    lines.append(
        f"Dialogue: 1,{ts(0.05)},{ts(hook['dur'])},Hook,,0,0,0,,"
        f"{{\\3c&H00F2FF&\\c&H101010&\\move(540,240,540,330,0,220)\\fad(0,200)}}{hook['text']}"
    )
for cd in plan.get("cards", []):
    s, e = remap(cd["s"]), remap(cd["e"])
    lines.append(f"Dialogue: 1,{ts(s)},{ts(e)},Card,,0,0,0,,{{\\fad(180,180)}}{cd['text']}")
open(ass, "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---------- filter graph ----------
inputs = ["-i", plan["source"], "-i", plan["voice"]]
music = None if no_music else plan.get("music")
if music:
    inputs += ["-stream_loop", "-1", "-i", music]
sticker_inputs = []
for st in plan.get("stickers", []):
    sticker_inputs.append(st)
    inputs += ["-i", st["file"]]

fc = []
grade = "eq=contrast=1.07:saturation=1.15:gamma=0.97,colorbalance=rs=0.03:gs=0.0:bs=-0.03:rm=0.02:bm=-0.02,unsharp=5:5:0.4"
vlabels, alabels = [], []
for i, (a, b, z) in enumerate(keep):
    crop = "" if z <= 1.001 else f",crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.42,scale={W}:{H}"
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS{crop},setsar=1[v{i}]")
    # 15ms fades at each cut avoid clicks
    d = b - a
    fc.append(f"[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0, d - 0.015)}:d=0.015[a{i}]")
    vlabels.append(f"[v{i}]"); alabels.append(f"[a{i}]")
n = len(keep)
fc.append("".join(v + a for v, a in zip(vlabels, alabels)) + f"concat=n={n}:v=1:a=1[vc][vo]")
fc.append(f"[vc]{grade},fps={FPS}[vg]")
cur = "[vg]"
base_idx = 3 if music else 2
for k, st in enumerate(sticker_inputs):
    t0 = remap(st["t"])
    lab = f"[vs{k}]"
    fc.append(f"[{base_idx + k}:v]setpts=PTS-STARTPTS+{t0}/TB[st{k}]")
    fc.append(f"{cur}[st{k}]overlay=x={st.get('x', 690)}:y={st.get('y', 250)}:eof_action=pass{lab}")
    cur = lab
fc.append(f"{cur}ass='{ass}':fontsdir='{FONTS}'[vout]")
if music:
    fc.append("[vo]asplit=2[vo1][vo2]")
    fc.append(f"[2:a]atrim=0:{total},asetpts=PTS-STARTPTS,volume=0.32,afade=t=in:d=1.0,afade=t=out:st={max(0, total - 2.0)}:d=2.0[m]")
    fc.append("[m][vo2]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md]")
    fc.append("[vo1][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
else:
    fc.append("[vo]loudnorm=I=-14:TP=-1.5:LRA=9[aout]")

script = os.path.splitext(out)[0] + ".filter"
open(script, "w").write(";\n".join(fc))
cmd = ["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-filter_complex_script", script,
       "-map", "[vout]", "-map", "[aout]",
       "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "12M", "-bufsize", "24M", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart"]
if preview:
    cmd += ["-t", str(preview)]
cmd.append(out)
print(f"segments={n} output_duration={total:.2f}s", flush=True)
subprocess.run(cmd, check=True)
