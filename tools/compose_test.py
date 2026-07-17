#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""换头合成测试：生成3个柴犬头(纯头) + 检测男身体蛋头锚点 + 合成 + 拼审查图"""
import base64, json, urllib.request, io, os
from PIL import Image, ImageDraw

KEY = json.load(open('/home/aexmo/auplus-pixel-office/runtime-config.json'))['gemini_api_key']
MODEL = "gemini-3.1-flash-image-preview"
CHARDIR = '/home/aexmo/auplus-pixel-office/frontend/characters'
BG = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/bodygen'
SCR = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad'
HEADDIR = f'{SCR}/heads'; os.makedirs(HEADDIR, exist_ok=True)
STATES = ['idle','busy','angry','happy','sad','eating','playing','sleepy','sleeping']

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

def gen_head(desc):
    ref = base64.b64encode(open(f'{CHARDIR}/char_6a5a6992_idle.png', 'rb').read()).decode()
    CORE = "ultra-simple flat cute style, minimal shading, clean outline, BOLD shiba features (cream muzzle, pointy ears)"
    prompt = ("Reference image: pixel style benchmark. Create ONLY THE HEAD of a shiba inu dog mascot: "
        f"big round HEAD, no body, no neck. Art style: {CORE}. Expression: {desc}. "
        "Pixel art, front-facing, centered, entire background solid pure magenta (#FF00FF), no text.")
    body = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": ref}}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=180))
    for pt in resp["candidates"][0]["content"]["parts"]:
        d = pt.get("inlineData") or pt.get("inline_data")
        if d:
            return keyed(Image.open(io.BytesIO(base64.b64decode(d["data"]))))
    return None

def detect_anchor(img):
    """检测蛋头(上60%的亮冷灰连通区)中心与尺寸"""
    px = img.load(); W, H = img.size
    xs, ys = [], []
    for y in range(int(H * 0.62)):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a > 120 and (r+g+b)/3 > 172 and b >= r - 12 and abs(r-g) < 40:
                xs.append(x); ys.append(y)
    if not xs:
        return None
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return {'cx': (x0+x1)//2, 'cy': (y0+y1)//2, 'w': x1-x0, 'h': y1-y0, 'y0': y0}

def compose(body, head, anc):
    hw = int(anc['w'] * 1.16)
    hh = int(head.height * hw / head.width)
    head2 = head.resize((hw, hh), Image.NEAREST)
    pad = 70
    cv = Image.new('RGBA', (max(body.width, hw) + 30, body.height + pad), (0, 0, 0, 0))
    bx = (cv.width - body.width) // 2
    by = pad
    cv.alpha_composite(body, (bx, by))
    acx, acy = bx + anc['cx'], by + anc['cy']
    hx = acx - hw // 2
    hy = int(acy + anc['h'] * 0.28) - hh
    cv.alpha_composite(head2, (hx, hy))
    bb = cv.getbbox()
    return cv.crop(bb) if bb else cv

# 1) 生成3个柴犬头
HEADS = {
    'doge':   'inspired by the doge meme: sideways skeptical glance, raised inner eyebrows, subtle smug pursed mouth',
    'cheems': 'inspired by the sad crying shiba meme: droopy watery puppy eyes, wobbly frown, pitiful adorable face',
    'smug':   'smug shiba: eyes closed in self-satisfied smile, chin up, insufferably proud',
}
heads = {}
for hid, desc in HEADS.items():
    fp = f'{HEADDIR}/{hid}.png'
    if os.path.exists(fp):
        heads[hid] = Image.open(fp)
    else:
        for _ in range(3):
            try:
                h = gen_head(desc)
                if h:
                    h.save(fp); heads[hid] = h; break
            except Exception as e:
                print(hid, 'retry', str(e)[:40])
    print(hid, 'head', heads.get(hid) and heads[hid].size)

# 2) 检测锚点 + 合成审查图
sheet = Image.new('RGBA', (1700, 1080), (40, 40, 48, 255))
d = ImageDraw.Draw(sheet)
for row, hid in enumerate(['doge', 'cheems', 'smug']):
    if hid not in heads:
        continue
    x = 10
    d.text((10, row * 360 + 5), hid, fill=(250, 230, 180))
    for st in STATES:
        body = Image.open(f'{BG}/body_m_{st}.png').convert('RGBA')
        anc = detect_anchor(body)
        if not anc:
            continue
        comp = compose(body, heads[hid], anc)
        comp.thumbnail((150, 300), Image.NEAREST)
        sheet.paste(comp, (x, row * 360 + 25), comp)
        if row == 0:
            d.text((x + 30, 340), st, fill=(180, 200, 220))
        x += 168
sheet.save(f'{SCR}/shiba_composed.png')
print('composed sheet ok')
