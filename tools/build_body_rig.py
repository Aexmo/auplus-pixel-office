#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""换头架构·身体绑定构建器
输入: scratchpad/bodygen/<body>_<state>[_2].png (已keyed透明)
输出:
  frontend/characters/rig_<body>_<state>_<f>.png  (去头身体: 蛋头连通块擦成透明)
  frontend/characters/body_rig.json  {body:{state:{f:{cx,cy,w,h}}}}
用法: build_body_rig.py body_m   (每具身体各跑一次)
"""
import json, os, sys
from collections import deque
from PIL import Image

CHARDIR = '/home/aexmo/auplus-pixel-office/frontend/characters'
BG = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/bodygen'
RIG_FILE = f'{CHARDIR}/body_rig.json'
STATES = ['idle','busy','angry','happy','sad','eating','playing','sleepy','sleeping']
BODY = sys.argv[1] if len(sys.argv) > 1 else 'body_m'
import os as _os
OSUF = ('_' + _os.environ.get('ORIENT')) if _os.environ.get('ORIENT') not in (None, 'front') else ''
BODYKEY = BODY + OSUF


def is_egg(px):
    r, g, b, a = px
    return a > 120 and (r+g+b)/3 > 168 and b >= r - 14 and abs(r-g) < 42 and abs(g-b) < 42


def largest_egg_blob(im):
    """上65%内最大的蛋头连通块 → 掩码坐标集"""
    px = im.load(); W, H = im.size
    limit = int(H * 0.66)
    seen = [[False]*W for _ in range(limit)]
    best = []
    for sy in range(limit):
        for sx in range(W):
            if seen[sy][sx] or not is_egg(px[sx, sy]):
                continue
            comp = []
            q = deque([(sx, sy)]); seen[sy][sx] = True
            while q:
                x, y = q.popleft(); comp.append((x, y))
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < W and 0 <= ny < limit and not seen[ny][nx] and is_egg(px[nx, ny]):
                        seen[ny][nx] = True; q.append((nx, ny))
            if len(comp) > len(best):
                best = comp
    return best


def process(body, state, f):
    suffix = '' if f == 0 else '_2'
    src = f'{BG}/{body}{OSUF}_{state}{suffix}.png'
    if not os.path.exists(src):
        return None
    im = Image.open(src).convert('RGBA')
    blob = largest_egg_blob(im)
    if not blob:
        return None
    xs = [p[0] for p in blob]; ys = [p[1] for p in blob]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    anchor = {'cx': (x0+x1)//2, 'cy': (y0+y1)//2, 'w': x1-x0, 'h': y1-y0}
    # 擦除蛋头 + 膨胀5px(连描边/抗锯齿一起擦净，避免头压低后露出蛋头描边弧线)
    px = im.load()
    R = 5
    eggset = set(blob)
    erase = set()
    for x, y in blob:
        for dx in range(-R, R + 1):
            for dy in range(-R, R + 1):
                if dx * dx + dy * dy <= R * R:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < im.width and 0 <= ny < im.height:
                        erase.add((nx, ny))
    for x, y in erase:
        px[x, y] = (0, 0, 0, 0)
    # 蛋头下沿再向下清 10px 内浅色(脖子残留)
    for x in range(max(0, x0 - 3), min(im.width, x1 + 4)):
        for y in range(y1, min(im.height, y1 + 12)):
            r, g, b, a = px[x, y]
            if a > 0 and (r + g + b) / 3 > 150 and b >= r - 20 and abs(r - g) < 45:
                px[x, y] = (0, 0, 0, 0)
    out = f'{CHARDIR}/rig_{body}{OSUF}_{state}_{f}.png'
    im.save(out)
    return anchor


def main():
    rig = {}
    if os.path.exists(RIG_FILE):
        try:
            rig = json.load(open(RIG_FILE, encoding='utf-8'))
        except Exception:
            rig = {}
    rig[BODYKEY] = {}
    for st in STATES:
        rig[BODYKEY][st] = {}
        for f in (0, 1):
            anc = process(BODY, st, f)
            if anc:
                rig[BODYKEY][st][str(f)] = anc
        print(st, rig[BODYKEY][st].get('0'))
    with open(RIG_FILE, 'w', encoding='utf-8') as fp:
        json.dump(rig, fp, ensure_ascii=False, indent=1)
    print('rig saved', BODYKEY, 'states', len(rig[BODYKEY]))


if __name__ == '__main__':
    main()
