#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""换头架构·共享身体动画生成器
以定稿身体(body_m/body_f)为参照，逐状态生成 2 帧身体姿态动画。
头保持空白灰蛋(后续被动物大头覆盖)。产物 → scratchpad/bodygen 待审查。
"""
import base64, json, urllib.request, io, os, sys, time
from PIL import Image

KEY = json.load(open('/home/aexmo/auplus-pixel-office/runtime-config.json'))['gemini_api_key']
MODEL = "gemini-3.1-flash-image-preview"
CHARDIR = '/home/aexmo/auplus-pixel-office/frontend/characters'
OUT = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/bodygen'
os.makedirs(OUT, exist_ok=True)

BODY = sys.argv[1] if len(sys.argv) > 1 else 'body_m'

# 纯身体语言(无表情，脸在头上)
STATES = [
    ('idle',     'standing relaxed, little stubby arms resting at sides'),
    ('busy',     'leaning forward slightly, both little arms in front as if busily working'),
    ('angry',    'standing tense, both little fists clenched down, stomping angry stance'),
    ('happy',    'both little arms raised up high cheering, hopping up joyfully off the ground'),
    ('sad',      'shoulders slumped, both little arms drooping down limply, dejected posture'),
    ('eating',   'one little hand raised up toward the head as if bringing food up, other arm at side'),
    ('playing',  'dynamic playful pose, little arms spread out wide, one leg lifted'),
    ('sleepy',   'body swaying tiredly, one little hand raised up rubbing near the head'),
    ('sleeping', 'sitting curled down small on the ground, resting peacefully'),
]

def keyed(im):
    im = im.convert('RGBA'); px = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if r > 130 and b > 130 and g < 110 and abs(r-b) < 90 and (r-g) > 60 and (b-g) > 60:
                px[x, y] = (0, 0, 0, 0)
            elif r > 110 and b > 110 and g < r-30 and g < b-30:
                m = (r+g+b)//3; px[x, y] = ((r+m)//2-20, g, (b+m)//2-20, a)
    bb = im.getbbox()
    return im.crop(bb) if bb else im

def call(prompt, ref_b64):
    body = {"contents": [{"parts": [{"text": prompt},
        {"inline_data": {"mime_type": "image/png", "data": ref_b64}}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=180))
    for pt in resp["candidates"][0]["content"]["parts"]:
        d = pt.get("inlineData") or pt.get("inline_data")
        if d:
            return base64.b64decode(d["data"])
    return None

base_ref = base64.b64encode(open(f'{CHARDIR}/{BODY}.png', 'rb').read()).decode()
KEEP = ("Keep the IDENTICAL chibi humanoid body: same clothing/outfit, same colors, same "
        "2-heads-tall proportions, same tiny stubby arms and legs. The head MUST stay a PLAIN "
        "FEATURELESS light-gray egg shape with NO face, no eyes, no features (blank placeholder). ")

done = 0
for state, desc in STATES:
    def_ref = base_ref
    frames = []
    for fi in range(2):
        if fi == 0:
            prompt = ("Reference image: THIS EXACT chibi body template. " + KEEP +
                f"Show the body posture: {desc}. Pixel art, front-facing, centered, "
                "entire background solid pure magenta (#FF00FF), no text.")
            ref = base_ref
        else:
            prompt = ("Reference image: animation frame 1 of THIS EXACT body. " + KEEP +
                "Create animation frame 2 of a 2-frame loop: same posture and framing, change ONLY "
                "subtle motion (limbs/body slightly shifted) for a smooth loop. Pixel art, centered, "
                "entire background solid pure magenta (#FF00FF), no text.")
            ref = frame1_b64
        raw = None
        for attempt in range(3):
            try:
                raw = call(prompt, ref); break
            except Exception as e:
                print(f"[retry{attempt}] {state} f{fi}: {str(e)[:50]}", flush=True); time.sleep(6)
        if raw is None:
            print(f"[FAIL] {state} f{fi}", flush=True); continue
        im = keyed(Image.open(io.BytesIO(raw)))
        th = 300
        im = im.resize((max(1, round(im.width * th / im.height)), th), Image.NEAREST)
        fn = f"{BODY}_{state}" + (f"_{fi+1}" if fi else "") + ".png"
        im.save(f"{OUT}/{fn}")
        frames.append(fn)
        if fi == 0:
            frame1_b64 = base64.b64encode(open(f"{OUT}/{fn}", 'rb').read()).decode()
    done += 1
    print(f"[ok] {state} ({done}/{len(STATES)})", flush=True)
    time.sleep(1)
print("DONE", done, flush=True)
