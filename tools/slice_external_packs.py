#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CC0 外部素材包切片器（渠道A）
来源：Kenney Roguelike Indoor / Modern City pack（CC0，via OpenGameArt）。
16px 网格(1px 间距) → 过滤空格 → 4x 最近邻放大 → 打包成 64px 网格大图 +
生成 frontend/extra-props-meta.js 供前端物品栏读取。
物件(带透明边) layer=floor；满格图块 layer=floorpatch（地板/墙面材质）。
"""
import json
import os
from PIL import Image

SCRATCH = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad'
OUT = '/home/aexmo/auplus-pixel-office/frontend'
CELL, GAP, UP = 16, 1, 4
PACK_COLS = 20

PACKS = [
    ('extra_indoor', f'{SCRATCH}/ext_indoor/Spritesheet/roguelikeIndoor_transparent.png', 'extra-indoor-64.png'),
    ('extra_city',   f'{SCRATCH}/ext_city/Spritesheet/roguelikeCity_transparent.png',     'extra-city-64.png'),
]


def slice_pack(src):
    im = Image.open(src).convert('RGBA')
    W, H = im.size
    cells = []
    y = 0
    while y + CELL <= H:
        x = 0
        while x + CELL <= W:
            c = im.crop((x, y, x + CELL, y + CELL))
            alpha = c.getchannel('A')
            solid = sum(1 for a in alpha.getdata() if a > 40)
            ratio = solid / (CELL * CELL)
            if ratio > 0.10:                       # 过滤空格
                cells.append((c, ratio > 0.97))    # 满格 = 图块
            x += CELL + GAP
        y += CELL + GAP
    return cells


def main():
    meta = {'sheets': [], 'items': []}
    for key, src, outname in PACKS:
        cells = slice_pack(src)
        # 去重（相同字节的格子只留一个）
        seen, uniq = set(), []
        for c, tile in cells:
            sig = c.tobytes()
            if sig in seen:
                continue
            seen.add(sig)
            uniq.append((c, tile))
        rows = (len(uniq) + PACK_COLS - 1) // PACK_COLS
        sheet = Image.new('RGBA', (PACK_COLS * CELL * UP, rows * CELL * UP), (0, 0, 0, 0))
        for i, (c, tile) in enumerate(uniq):
            big = c.resize((CELL * UP, CELL * UP), Image.NEAREST)
            sheet.paste(big, ((i % PACK_COLS) * CELL * UP, (i // PACK_COLS) * CELL * UP))
            meta['items'].append([key, i, 1 if tile else 0])
        sheet.save(f'{OUT}/{outname}')
        meta['sheets'].append({'key': key, 'file': outname, 'cols': PACK_COLS,
                               'rows': rows, 'count': len(uniq)})
        print(key, len(uniq), 'cells ->', outname, sheet.size)
    with open(f'{OUT}/extra-props-meta.js', 'w', encoding='utf-8') as f:
        f.write('// CC0 外部素材包索引（Kenney roguelike packs, via OpenGameArt）— 自动生成\n')
        f.write('window.EXTRA_PROPS = ' + json.dumps(meta, ensure_ascii=False) + ';\n')
    print('meta items:', len(meta['items']))


if __name__ == '__main__':
    main()
