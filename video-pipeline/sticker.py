# Render an animated emoji sticker (pop-in, gentle bob, pop-out) as RGBA PNG frames -> transparent MOV
import sys, math, os, subprocess
from PIL import Image, ImageDraw, ImageFont
emoji, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
size = int(sys.argv[4]) if len(sys.argv) > 4 else 220
fps = 30
f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
base = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
ImageDraw.Draw(base).text((80, 80), emoji, font=f, embedded_color=True, anchor="mm")
bbox = base.getbbox(); base = base.crop(bbox)
base = base.resize((size, int(size * base.height / base.width)), Image.LANCZOS)
W = H = int(size * 1.6)
tmp = out + "_frames"; os.makedirs(tmp, exist_ok=True)
n = int(dur * fps)
def ease_back(t):  # overshoot pop
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
for i in range(n):
    t = i / fps
    tin = min(t / 0.25, 1); tout = min(max((dur - t) / 0.2, 0), 1)
    s = ease_back(tin) * (tout ** 0.5)
    ang = 8 * math.sin(t * 2 * math.pi * 1.2)
    bob = 10 * math.sin(t * 2 * math.pi * 0.9)
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if s > 0.01:
        im = base.resize((max(1, int(base.width * s)), max(1, int(base.height * s))), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(im, ((W - im.width) // 2, int((H - im.height) // 2 + bob)))
    fr.save(f"{tmp}/{i:04d}.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", f"{tmp}/%04d.png", "-c:v", "qtrle", out], check=True)
subprocess.run(["rm", "-rf", tmp])
