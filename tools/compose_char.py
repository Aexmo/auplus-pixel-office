#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""换头合成器(共享逻辑): 去头身体 + 动物头 → 完整角色帧
被 backend 和测试脚本复用。头比蛋头略大并下压到肩，保证蛋头区域被完全覆盖。
"""
import json, os
from PIL import Image

CHARDIR = '/home/aexmo/auplus-pixel-office/frontend/characters'
RIG_FILE = f'{CHARDIR}/body_rig.json'
STATES = ['idle','busy','angry','happy','sad','eating','playing','sleepy','sleeping']

# 头表情映射(mode B: 6个表情头覆盖9状态)
STATE_TO_EXPR = {
    'idle': 'normal', 'busy': 'normal', 'playing': 'happy', 'happy': 'happy',
    'angry': 'angry', 'sad': 'sad', 'eating': 'happy', 'sleepy': 'sleepy', 'sleeping': 'sleepy',
}
EXPR_ORDER = ['normal', 'happy', 'angry', 'sad', 'sleepy']


def load_rig():
    return json.load(open(RIG_FILE, encoding='utf-8'))


def compose_frame(body, state, f, head_img, rig=None):
    rig = rig or load_rig()
    fs = str(f)
    anc = rig.get(body, {}).get(state, {}).get(fs) or rig.get(body, {}).get(state, {}).get('0')
    rig_path = f'{CHARDIR}/rig_{body}_{state}_{f}.png'
    if not os.path.exists(rig_path):
        rig_path = f'{CHARDIR}/rig_{body}_{state}_0.png'
    if not anc or not os.path.exists(rig_path):
        return None
    bodyimg = Image.open(rig_path).convert('RGBA')
    # 头宽 = 蛋头宽 ×1.28 (更大以完全覆盖)
    hw = int(anc['w'] * 1.28)
    hh = int(head_img.height * hw / head_img.width)
    head2 = head_img.resize((hw, hh), Image.NEAREST)
    pad = max(0, hh - anc['cy'] + 24)
    cv = Image.new('RGBA', (max(bodyimg.width, hw) + 30, bodyimg.height + pad), (0, 0, 0, 0))
    bx = (cv.width - bodyimg.width) // 2
    by = pad
    cv.alpha_composite(bodyimg, (bx, by))
    acx, acy = bx + anc['cx'], by + anc['cy']
    hx = acx - hw // 2
    # 头底沉到蛋头中心下方 55% 处 → 下巴压到脖子/肩，蛋头彻底被盖
    hy = int(acy + anc['h'] * 0.30) - hh
    cv.alpha_composite(head2, (hx, hy))
    bb = cv.getbbox()
    return cv.crop(bb) if bb else cv


if __name__ == '__main__':
    # 测试: doge头 × 男身体9状态
    from PIL import ImageDraw
    rig = load_rig()
    head = Image.open('/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/heads/doge.png').convert('RGBA')
    sheet = Image.new('RGBA', (1550, 380), (40, 40, 48, 255))
    d = ImageDraw.Draw(sheet); x = 10
    for st in STATES:
        comp = compose_frame('body_m', st, 0, head, rig)
        if comp:
            comp.thumbnail((150, 320), Image.NEAREST)
            sheet.paste(comp, (x, 10), comp)
            d.text((x+40, 350), st, fill=(230, 220, 200))
        x += 168
    sheet.save('/tmp/claude-1001/-home-aexmo/97bd1a9a-02a3-48c8-b799-da42bc926bec/scratchpad/compose_verify.png')
    print('verify sheet ok')
