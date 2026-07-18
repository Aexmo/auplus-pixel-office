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

# 纯身体语言(无表情，脸在头上) —— 夸张无厘头版: 幅度大、姿势怪、搞笑
STATES = [
    ('idle',     'standing but wobbling and swaying goofily side to side, little arms swinging loosely, silly relaxed vibe'),
    ('busy',     'FRANTICALLY typing at insane speed, both little arms a blurry flurry, leaning way in super hectic and comical'),
    ('angry',    'THROWING A TANTRUM: jumping off the ground in a rage, both fists flailing wildly in the air, legs kicking, over-the-top furious'),
    ('happy',    'LEAPING super high into the air, both little arms thrown up wildly, legs kicking out, ecstatic explosive joy'),
    ('sad',      'DRAMATICALLY collapsed forward in despair, both arms dangling limp all the way to the floor, over-the-top melodramatic gloom'),
    ('eating',   'STUFFING food into the mouth with both hands frantically, arms shoveling, belly out, comically gluttonous'),
    ('playing',  'doing a WILD silly dance, arms and legs flailing in totally different crazy directions, goofy party pose'),
    ('sleepy',   'standing still and drowsy, head drooping down, both little arms hanging limp and relaxed at the sides, calm and about to fall asleep (NOT flailing)'),
    ('sleeping', 'sitting down peacefully fast asleep, body relaxed and still, little arms resting quietly, calm sleeping posture (NOT flailing)'),
]
CALM_STATES = {'sleepy', 'sleeping'}   # 安静状态: 第2帧只做轻微呼吸,不做大动作
STATE_FILTER = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None
ORIENT = os.environ.get('ORIENT', 'front')   # front / back / side
SUF = ('_' + ORIENT) if ORIENT != 'front' else ''
if ORIENT == 'back':
    BACK_NOTE = (' The WHOLE body is seen FROM BEHIND (back facing the viewer): back of the head, back of the '
                 'outfit, AND the legs/feet also from behind (we see the backs of the heels, NOT the toes). '
                 'The character must have exactly TWO legs and TWO arms, no extra limbs.')
elif ORIENT == 'side':
    BACK_NOTE = (' The WHOLE body is seen from the SIDE (LEFT profile, facing left): head, outfit and legs all '
                 'in clean side profile. Keep it a clear side view, exactly two legs and two arms visible in '
                 'profile, no extra limbs.')
else:
    BACK_NOTE = ''
# 背面专用姿势覆盖(修正正面朝向脚/多脚等问题状态)
BACK_OVERRIDE = {
    'sad': 'crouched down and slumped in dejection, seen FULLY FROM BEHIND — the back and the backs of the '
           'legs/heels toward the viewer, both arms hanging limp down, gloomy',
    'playing': 'a lively playful little dance seen FULLY FROM BEHIND, exactly TWO legs and two arms (absolutely '
               'no third leg or extra limbs), one leg lifted in a cute hop, back toward viewer',
} if ORIENT == 'back' else {}

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

base_ref = base64.b64encode(open(f'{CHARDIR}/{BODY}{SUF}.png', 'rb').read()).decode()
KEEP = ("Keep the IDENTICAL chibi humanoid body: same clothing/outfit, same colors, same "
        "2-heads-tall proportions, same tiny stubby arms and legs. The head MUST stay a PLAIN "
        "FEATURELESS light-gray egg shape with NO face, no eyes, no features (blank placeholder). " + BACK_NOTE)

done = 0
for state, desc in STATES:
    if STATE_FILTER and state not in STATE_FILTER:
        continue
    desc = BACK_OVERRIDE.get(state, desc)   # 背面问题状态用专用描述
    def_ref = base_ref
    frames = []
    for fi in range(2):
        if fi == 0:
            prompt = ("Reference image: THIS EXACT chibi body template. " + KEEP +
                f"Show the body posture: {desc}. Pixel art, front-facing, centered, "
                "entire background solid pure magenta (#FF00FF), no text.")
            ref = base_ref
        elif state in CALM_STATES:
            prompt = ("Reference image: animation frame 1 of THIS EXACT body. " + KEEP +
                "Create animation frame 2 of a 2-frame loop: keep the SAME calm sleepy posture, change ONLY a "
                "tiny subtle breathing motion (body rises/settles a little), stay relaxed and still. Pixel art, "
                "centered, entire background solid pure magenta (#FF00FF), no text.")
            ref = frame1_b64
        else:
            prompt = ("Reference image: animation frame 1 of THIS EXACT body. " + KEEP +
                "Create animation frame 2 of a 2-frame loop: keep the same character and outfit but make a "
                "BIG exaggerated motion change (limbs swung to opposite side, body bounced/twisted noticeably, "
                "a lively wacky jitter) so the 2-frame loop looks energetic and funny, NOT subtle. Pixel art, "
                "centered, entire background solid pure magenta (#FF00FF), no text.")
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
        fn = f"{BODY}{SUF}_{state}" + (f"_{fi+1}" if fi else "") + ".png"
        im.save(f"{OUT}/{fn}")
        frames.append(fn)
        if fi == 0:
            frame1_b64 = base64.b64encode(open(f"{OUT}/{fn}", 'rb').read()).decode()
    done += 1
    print(f"[ok] {state} ({done}/{len(STATES)})", flush=True)
    time.sleep(1)
print("DONE", done, flush=True)
