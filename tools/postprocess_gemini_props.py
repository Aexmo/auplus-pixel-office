#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gemini 生成素材后处理：品红抠底 → 去紫边 → 自动裁剪 → 缩放到游戏尺寸
输出 frontend/prop3_<id>.png
"""
import os
from PIL import Image

RAW = '/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/gemgen'
OUT = '/home/aexmo/auplus-pixel-office/frontend'

# id -> 游戏内目标高度(px)
TARGET_H = {
    'sofa_fabric': 96, 'armchair': 84, 'beanbag': 66, 'coffee_table': 64,
    'meeting_table': 116, 'tv_console': 92, 'bar_counter': 100, 'floor_lamp': 108,
    'plant_big': 108, 'aquarium': 96, 'arcade': 128, 'fridge': 116,
    'kitchen_counter': 92, 'vending': 128, 'watercooler': 92, 'printer': 76,
    'fireplace': 122, 'rug_round': 88, 'window_night': 78, 'painting_land': 64,
    'noticeboard': 70, 'neon_sign': 54, 'cat_tree': 118, 'pingpong': 108,
    'partition': 98, 'safe': 78, 'clock_wall': 46, 'bookshelf_big': 130,
    'pool_table': 112, 'foosball': 96, 'piano': 110, 'guitar_stand': 84,
    'jukebox': 116, 'christmas_tree': 140, 'easel': 104, 'statue': 96,
    'telescope': 100, 'grandfather_clock': 128, 'treadmill': 96, 'massage_chair': 100,
    'reception': 104, 'sofa_l': 120, 'wardrobe': 128, 'bed_double': 124,
    'bunk_bed': 132, 'washing_machine': 88, 'popcorn': 108, 'espresso_cart': 100,
    'bar_shelf': 116, 'dog_bed': 64, 'pet_bowls': 40, 'bird_cage': 110,
    'flower_vase': 84, 'hanging_plant': 80, 'cactus_set': 72, 'fountain': 104,
    'mirror_standing': 108, 'magazine_rack': 76, 'photo_wall': 84, 'banner_flag': 72,
    'shelf_trophies': 60, 'window_big': 92, 'rug_rect': 96, 'welcome_mat': 44,
}


def keyed(im):
    im = im.convert('RGBA')
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            # 品红判定（宽容度覆盖 jpeg 压缩噪声）
            if r > 130 and b > 130 and g < 110 and abs(r - b) < 90 and (r - g) > 60 and (b - g) > 60:
                px[x, y] = (0, 0, 0, 0)
            elif r > 110 and b > 110 and g < r - 30 and g < b - 30:
                # 紫边：向灰色压（去品红污染）
                m = (r + g + b) // 3
                px[x, y] = ((r + m) // 2 - 20, g, (b + m) // 2 - 20, a)
    return im


def erode_edge(im):
    """把贴着透明区的半透明/污染边收一圈，边缘更干净"""
    px = im.load()
    W, H = im.size
    kill = []
    for y in range(H):
        for x in range(W):
            if px[x, y][3] == 0:
                continue
            n_trans = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and px[nx, ny][3] == 0:
                    n_trans += 1
            r, g, b, a = px[x, y]
            if n_trans >= 2 and r > 150 and b > 150 and g < 120:
                kill.append((x, y))
    for x, y in kill:
        px[x, y] = (0, 0, 0, 0)
    return im


def process(pid, th):
    src = f'{RAW}/raw_{pid}.png'
    if not os.path.exists(src):
        print('missing', pid)
        return False
    im = Image.open(src)
    im = keyed(im)
    im = erode_edge(im)
    bbox = im.getbbox()
    if not bbox:
        print('empty after key', pid)
        return False
    im = im.crop(bbox)
    scale = th / im.height
    im = im.resize((max(1, round(im.width * scale)), th), Image.NEAREST)
    im.save(f'{OUT}/prop3_{pid}.png')
    print(f'prop3_{pid}.png {im.size}')
    return True


def main():
    ok = 0
    for pid, th in TARGET_H.items():
        if process(pid, th):
            ok += 1
    print('processed', ok, '/', len(TARGET_H))


if __name__ == '__main__':
    main()
