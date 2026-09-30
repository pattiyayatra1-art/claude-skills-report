"""ภาพที่ 1: สมการความสำเร็จของเศรษฐกิจดิจิทัล (จาก VDO ตอนที่ 2) - box diagram in the model report's style."""
import glob, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

cands = glob.glob(r"C:\Windows\Fonts\THSarabunNew*.ttf") + glob.glob(
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts\THSarabunNew*.ttf"))
reg = [c for c in cands if os.path.basename(c).lower() == "thsarabunnew.ttf"][0]
bold = [c for c in cands if os.path.basename(c).lower() == "thsarabunnew bold.ttf"][0]
for f in (reg, bold):
    font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=reg).get_name()

boxes = [
    ("ข้อมูลที่ดี", "ถูกต้อง เป็นปัจจุบัน\nเชื่อถือได้ มีแหล่งอ้างอิง\nครบถ้วน", "#dce6f2"),
    ("เทคโนโลยีที่ใช่", "AI/ML, IoT, Blockchain\nCloud, 5G, Automation\nAR/VR", "#c9d9ef"),
    ("คนและองค์กรที่พร้อม", "ทักษะดิจิทัล\nความรู้ทางการเงิน\nการคิดเชิงวิพากษ์", "#b4cbea"),
    ("ความสำเร็จใน\nเศรษฐกิจดิจิทัล", "ลดต้นทุน เพิ่มประสิทธิภาพ\nสร้างมูลค่าทางเศรษฐกิจ", "#1f3864"),
]
ops = ["+", "+", "="]
fig, ax = plt.subplots(figsize=(10, 2.9), dpi=220)
ax.set_xlim(0, 100); ax.set_ylim(0, 30); ax.axis("off")
w, h, gap, y = 20.5, 24, 6.0, 3
x = 1
for i, (title, body, col) in enumerate(boxes):
    dark = col == "#1f3864"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", fc=col, ec="#1f3864", lw=1.2))
    tc = "white" if dark else "#0b0b0b"
    ax.text(x + w / 2, y + h - 6.5, title, ha="center", va="center", fontsize=17, fontweight="bold", color=tc, linespacing=0.95)
    ax.text(x + w / 2, y + 7.5, body, ha="center", va="center", fontsize=12.5 if dark else 14, color=tc, linespacing=1.05)
    if i < 3:
        ax.text(x + w + gap / 2, y + h / 2, ops[i], ha="center", va="center", fontsize=30, fontweight="bold", color="#1f3864")
    x += w + gap
fig.savefig("fig_equation.png", bbox_inches="tight", pad_inches=0.05, facecolor="white")
print("ok")
