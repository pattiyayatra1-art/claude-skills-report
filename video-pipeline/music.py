# Procedurally generated lo-fi background bed (royalty-free, made here). Usage: music.py out.wav seconds
import sys, numpy as np, wave
out, secs = sys.argv[1], float(sys.argv[2])
sr, bpm = 44100, 84
beat = 60 / bpm; bar = 4 * beat
N = int(secs * sr); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def env(n, a, r):
    e = np.ones(n); a = max(1, int(a * sr)); r = max(1, int(r * sr))
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
def add(buf, start, sig):
    i = int(start * sr); j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[: j - i]
def lp(x, a):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for k in range(len(x)): acc += a * (x[k] - acc); y[k] = acc
    return y
# Fmaj7 - Em7 - Dm7 - Cmaj7 (warm, friendly)
prog = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
bars = int(secs / bar) + 1
t_bar = np.arange(int(bar * sr)) / sr
for b in range(bars):
    ch = prog[b % 4]; st = b * bar
    pad = sum(np.sin(2 * np.pi * midi(n) * t_bar) + 0.5 * np.sin(2 * np.pi * midi(n) * 1.003 * t_bar) for n in ch)
    pad *= env(len(t_bar), 0.4, 0.6) * 0.035
    add(L, st, pad); add(R, st, pad * 0.9)
    bass_t = np.arange(int(beat * 2 * sr)) / sr
    bass = np.sin(2 * np.pi * midi(ch[0] - 12) * bass_t) * np.exp(-bass_t * 2.5) * 0.12
    add(L, st, bass); add(R, st, bass); add(L, st + 2 * beat, bass * 0.8); add(R, st + 2 * beat, bass * 0.8)
    for k in range(8):  # gentle e-piano arpeggio, swung 8ths
        n = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
        tt = np.arange(int(0.6 * sr)) / sr
        note = (np.sin(2 * np.pi * midi(n) * tt) + 0.3 * np.sin(4 * np.pi * midi(n) * tt)) * np.exp(-tt * 6) * 0.03
        off = st + k * beat / 2 + (0.06 if k % 2 else 0)
        pan = 0.5 + 0.3 * np.sin(k)
        add(L, off, note * (1 - pan) * 2); add(R, off, note * pan * 2)
    for k in range(4):  # drums
        kt = np.arange(int(0.25 * sr)) / sr
        if k in (0, 2):
            kick = np.sin(2 * np.pi * (50 + 60 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 12) * 0.22
            add(L, st + k * beat, kick); add(R, st + k * beat, kick)
        else:
            sn = rng.standard_normal(len(kt)) * np.exp(-kt * 25) * 0.04
            add(L, st + k * beat, sn); add(R, st + k * beat, sn)
        for h in (0, 0.5):
            ht = np.arange(int(0.05 * sr)) / sr
            hat = np.diff(rng.standard_normal(len(ht) + 1)) * np.exp(-ht * 80) * 0.012
            add(L, st + (k + h) * beat + 0.03, hat); add(R, st + (k + h) * beat, hat)
vin = rng.standard_normal(N) * 0.002  # vinyl hiss
L = lp(L + vin, 0.35); R = lp(R + vin, 0.35)
fade = int(2 * sr); 
for ch in (L, R): ch[:fade] *= np.linspace(0, 1, fade); ch[-fade:] *= np.linspace(1, 0, fade)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L / mx * 0.8, R / mx * 0.8
data = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(data.tobytes())
