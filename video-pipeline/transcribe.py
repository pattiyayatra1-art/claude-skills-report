import json, sys, time
from faster_whisper import WhisperModel
audio, out, model_id = sys.argv[1], sys.argv[2], sys.argv[3]
t=time.time()
m = WhisperModel(model_id, device="cpu", compute_type="int8", cpu_threads=4)
print("loaded", time.time()-t, flush=True)
segs, info = m.transcribe(audio, language="th", beam_size=5, word_timestamps=True,
    vad_filter=True, vad_parameters={"min_silence_duration_ms": 300}, condition_on_previous_text=False)
res=[]
for s in segs:
    res.append({"start":s.start,"end":s.end,"text":s.text.strip(),
                "words":[{"s":w.start,"e":w.end,"w":w.word,"p":w.probability} for w in (s.words or [])]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
json.dump(res, open(out,"w"), ensure_ascii=False, indent=1)
print("done", time.time()-t, flush=True)
