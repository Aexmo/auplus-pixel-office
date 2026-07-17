#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精品素材批量生成（渠道D）：Gemini 生图 API + 现有 desk 素材做风格锚
每件：品红底单物件 → raw 落盘。后续由 postprocess_gemini_props.py 抠底/裁剪/缩放。
"""
import base64
import json
import os
import sys
import time
import urllib.request

KEY = os.environ.get("GEMINI_API_KEY", "")  # 凭证见记忆 reference_credentials，勿硬编码入库
if not KEY:
    sys.exit("请先 export GEMINI_API_KEY=<key> 再运行")
MODEL = "gemini-3.1-flash-image-preview"
REF = '/home/aexmo/auplus-pixel-office/frontend/desk-v3.webp'
RAW = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/gemgen'
os.makedirs(RAW, exist_ok=True)

# id, 英文物件描述
ITEMS = [
    ('sofa_fabric',   'a cozy beige fabric three-seat sofa with warm cushions'),
    ('armchair',      'a brown leather single armchair, cozy and worn'),
    ('beanbag',       'an orange bean bag chair'),
    ('coffee_table',  'a low wooden coffee table with a coffee mug and magazines on top'),
    ('meeting_table', 'a large wooden meeting table with six chairs around it, seen from 3/4 top-down game perspective'),
    ('tv_console',    'a wooden TV console cabinet with a retro CRT television on top showing a chart'),
    ('bar_counter',   'a small wooden bar counter with two bar stools and bottles on top'),
    ('floor_lamp',    'a brass floor lamp with warm glowing lampshade'),
    ('plant_big',     'a large potted monstera plant in a wooden pot'),
    ('aquarium',      'an aquarium fish tank on a wooden cabinet, tropical fish and water plants inside, soft glow'),
    ('arcade',        'a retro arcade game machine with glowing neon screen and joystick'),
    ('fridge',        'a retro cream-colored refrigerator with chrome handle'),
    ('kitchen_counter', 'a wooden kitchen counter with a sink, kettle and microwave'),
    ('vending',       'a red vending machine filled with colorful snacks, glowing softly'),
    ('watercooler',   'an office water cooler dispenser with blue water bottle on top'),
    ('printer',       'an office multifunction printer copier machine'),
    ('fireplace',     'a stone fireplace with burning fire and firewood, warm glow'),
    ('rug_round',     'a round woven rug with warm concentric ring pattern, seen from directly above'),
    ('window_night',  'a wooden-framed window showing starry night sky and moon, small potted plant on windowsill'),
    ('painting_land', 'a framed landscape oil painting of mountains and a lake, wooden frame'),
    ('noticeboard',   'a cork notice board with pinned colorful sticky notes and photos'),
    ('neon_sign',     'a neon wall sign glowing pink and cyan, abstract wave shape'),
    ('cat_tree',      'a cat climbing tree tower with platforms and a cute cat sitting on top'),
    ('pingpong',      'a ping pong table with net, paddles and ball, seen from 3/4 top-down game perspective'),
    ('partition',     'a three-panel wooden folding screen room divider'),
    ('safe',          'a vintage dark green metal safe box with round dial'),
    ('clock_wall',    'a round wall clock with wooden frame'),
    ('bookshelf_big', 'a tall wooden bookshelf completely filled with colorful books'),
]

PROMPT_TMPL = """Reference image: a pixel-art wooden desk sprite from our cozy office game. Create a NEW sprite in the EXACT same pixel art style (same warm palette, same pixel density, same outline and shading style, same 3/4 top-down game perspective):

{desc}.

Requirements: single object only, centered, entire background must be solid pure magenta (#FF00FF), no shadow cast on the background, no text, no watermark."""


def gen_one(pid, desc, ref_b64):
    body = {
        "contents": [{"parts": [
            {"text": PROMPT_TMPL.format(desc=desc)},
            {"inline_data": {"mime_type": "image/webp", "data": ref_b64}}
        ]}],
        "generationConfig": {"responseModalities": ["IMAGE"]}
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=180))
    for p in resp["candidates"][0]["content"]["parts"]:
        d = p.get("inlineData") or p.get("inline_data")
        if d:
            open(f"{RAW}/raw_{pid}.png", "wb").write(base64.b64decode(d["data"]))
            return True
    return False


def main():
    ref_b64 = base64.b64encode(open(REF, 'rb').read()).decode()
    done, fail = 0, []
    for pid, desc in ITEMS:
        out = f"{RAW}/raw_{pid}.png"
        if os.path.exists(out) and os.path.getsize(out) > 30000:
            done += 1
            print(f"[skip] {pid}", flush=True)
            continue
        ok = False
        for attempt in range(3):
            try:
                ok = gen_one(pid, desc, ref_b64)
                if ok:
                    break
            except Exception as e:
                print(f"[retry{attempt}] {pid}: {e}", flush=True)
                time.sleep(8)
        if ok:
            done += 1
            print(f"[ok] {pid} ({done}/{len(ITEMS)})", flush=True)
        else:
            fail.append(pid)
            print(f"[FAIL] {pid}", flush=True)
        time.sleep(2)
    print("DONE", done, "FAILED", fail, flush=True)


if __name__ == '__main__':
    main()
