#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""像素素材生成器二期（渠道B）：家具/设备/墙面(含新窗户)/挂画/地板贴片
风格与一期一致：半分辨率绘制 → 2x 最近邻放大，INK 描边。输出 frontend/。
"""
import random
from PIL import Image, ImageDraw

random.seed(7)
OUT = '/home/aexmo/auplus-pixel-office/frontend'
INK = (30, 22, 14, 255)


def canvas(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save2x(im, name):
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(f'{OUT}/{name}')
    print(name)


def r(d, x, y, w, h, c):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def outline(d, x, y, w, h, c=INK):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=c)


def hi(c, n=26):
    return tuple(min(255, v + n) for v in c[:3])


def lo(c, n=26):
    return tuple(max(0, v - n) for v in c[:3])


# ---------------- 家具 ----------------
def gen_armchair_green():
    im, d = canvas(34, 32)
    c = (96, 138, 96)
    r(d, 2, 4, 30, 16, c); outline(d, 2, 4, 30, 16)
    r(d, 3, 5, 28, 3, hi(c))
    r(d, 0, 12, 6, 14, lo(c)); outline(d, 0, 12, 6, 14)
    r(d, 28, 12, 6, 14, lo(c)); outline(d, 28, 12, 6, 14)
    r(d, 6, 18, 22, 8, hi(c, 14)); outline(d, 6, 18, 22, 8)
    r(d, 4, 27, 4, 4, (70, 50, 34)); r(d, 26, 27, 4, 4, (70, 50, 34))
    save2x(im, 'prop2_armchair.png')


def gen_sofa_blue():
    im, d = canvas(52, 30)
    c = (86, 108, 150)
    r(d, 3, 2, 46, 14, c); outline(d, 3, 2, 46, 14)
    r(d, 4, 3, 44, 3, hi(c))
    r(d, 0, 10, 6, 14, lo(c)); outline(d, 0, 10, 6, 14)
    r(d, 46, 10, 6, 14, lo(c)); outline(d, 46, 10, 6, 14)
    r(d, 6, 15, 40, 9, hi(c, 12)); outline(d, 6, 15, 40, 9)
    d.line([26, 16, 26, 23], fill=lo(c))
    r(d, 5, 25, 4, 4, (70, 50, 34)); r(d, 43, 25, 4, 4, (70, 50, 34))
    save2x(im, 'prop2_sofa.png')


def gen_beanbag():
    im, d = canvas(26, 22)
    c = (200, 130, 90)
    d.ellipse([0, 6, 25, 21], fill=c)
    d.ellipse([3, 0, 22, 14], fill=hi(c, 14))
    d.ellipse([7, 3, 18, 10], fill=hi(c, 30))
    d.ellipse([0, 6, 25, 21], outline=lo(c, 40))
    save2x(im, 'prop2_beanbag.png')


def gen_chair_office():
    im, d = canvas(18, 28)
    c = (70, 84, 104)
    r(d, 3, 0, 12, 10, c); outline(d, 3, 0, 12, 10)
    r(d, 4, 1, 10, 2, hi(c))
    r(d, 2, 12, 14, 6, hi(c, 10)); outline(d, 2, 12, 14, 6)
    r(d, 8, 18, 2, 5, (50, 54, 60))
    d.line([3, 26, 15, 26], fill=(50, 54, 60), width=2)
    d.point((3, 27), fill=(30, 30, 34)); d.point((15, 27), fill=(30, 30, 34))
    save2x(im, 'prop2_chair.png')


def gen_stool():
    im, d = canvas(14, 16)
    c = (150, 104, 66)
    d.ellipse([0, 0, 13, 7], fill=c, outline=lo(c, 40))
    d.ellipse([2, 1, 11, 4], fill=hi(c))
    r(d, 2, 7, 2, 8, lo(c, 20)); r(d, 10, 7, 2, 8, lo(c, 20))
    save2x(im, 'prop2_stool.png')


def gen_bench():
    im, d = canvas(44, 18)
    c = (140, 96, 60)
    r(d, 1, 3, 42, 6, c); outline(d, 1, 3, 42, 6)
    r(d, 2, 4, 40, 2, hi(c))
    r(d, 4, 9, 3, 8, lo(c, 20)); r(d, 37, 9, 3, 8, lo(c, 20))
    save2x(im, 'prop2_bench.png')


def gen_side_table():
    im, d = canvas(20, 20)
    c = (128, 90, 58)
    r(d, 1, 4, 18, 5, c); outline(d, 1, 4, 18, 5)
    r(d, 2, 5, 16, 1, hi(c))
    r(d, 3, 9, 2, 10, lo(c, 16)); r(d, 15, 9, 2, 10, lo(c, 16))
    r(d, 6, 0, 8, 4, (170, 190, 170)); outline(d, 6, 0, 8, 4)   # 小盆栽
    save2x(im, 'prop2_sidetable.png')


def gen_coffee_table():
    im, d = canvas(36, 20)
    c = (120, 84, 54)
    r(d, 1, 4, 34, 7, c); outline(d, 1, 4, 34, 7)
    r(d, 2, 5, 32, 2, hi(c))
    r(d, 8, 6, 8, 4, (240, 238, 230))                            # 杂志
    r(d, 20, 6, 6, 3, (200, 90, 80))                             # 杯子
    r(d, 3, 11, 3, 8, lo(c, 16)); r(d, 30, 11, 3, 8, lo(c, 16))
    save2x(im, 'prop2_coffeetable.png')


def gen_tv_stand():
    im, d = canvas(46, 34)
    r(d, 8, 0, 30, 18, (40, 44, 52)); outline(d, 8, 0, 30, 18)   # 电视
    r(d, 10, 2, 26, 14, (26, 34, 52))
    d.line([12, 12, 18, 6, 24, 9, 33, 4], fill=(120, 210, 160))
    r(d, 21, 18, 4, 2, (60, 64, 72))
    c = (128, 90, 58)
    r(d, 1, 20, 44, 10, c); outline(d, 1, 20, 44, 10)            # 柜体
    r(d, 2, 21, 42, 2, hi(c))
    r(d, 6, 24, 14, 5, lo(c, 12)); outline(d, 6, 24, 14, 5, lo(c, 40))
    r(d, 26, 24, 14, 5, lo(c, 12)); outline(d, 26, 24, 14, 5, lo(c, 40))
    r(d, 1, 30, 44, 3, lo(c, 30))
    save2x(im, 'prop2_tvstand.png')


def gen_bar_counter():
    im, d = canvas(60, 30)
    c = (110, 74, 46)
    r(d, 0, 4, 60, 6, hi(c, 16)); outline(d, 0, 4, 60, 6)
    r(d, 0, 4, 60, 2, hi(c, 34))
    r(d, 2, 10, 56, 16, c); outline(d, 2, 10, 56, 16)
    for x in (6, 20, 34, 48):
        r(d, x, 12, 10, 12, lo(c, 10)); outline(d, x, 12, 10, 12, lo(c, 36))
    r(d, 8, 0, 5, 4, (220, 180, 90))                             # 吧台上的杯瓶
    r(d, 20, 1, 3, 3, (150, 200, 220))
    r(d, 40, 0, 4, 4, (170, 120, 170))
    r(d, 0, 26, 60, 3, lo(c, 30))
    save2x(im, 'prop2_bar.png')


def gen_locker():
    im, d = canvas(24, 42)
    c = (110, 130, 140)
    r(d, 0, 0, 24, 40, c); outline(d, 0, 0, 24, 40)
    d.line([12, 1, 12, 38], fill=lo(c, 30))
    for x in (2, 14):
        r(d, x, 3, 8, 2, lo(c, 20)); r(d, x, 7, 8, 2, lo(c, 20))
        r(d, x + 6, 16, 2, 5, (60, 70, 76))
    r(d, 0, 40, 24, 2, lo(c, 40))
    save2x(im, 'prop2_locker.png')


def gen_bookcase_low():
    im, d = canvas(44, 30)
    wood = (110, 74, 46)
    r(d, 0, 0, 44, 28, wood); outline(d, 0, 0, 44, 28)
    r(d, 1, 1, 42, 2, hi(wood))
    books = [(196, 92, 80), (108, 140, 180), (196, 168, 92), (110, 160, 110), (170, 110, 170)]
    for sy in (4, 16):
        r(d, 2, sy, 40, 10, (62, 42, 26))
        x = 3
        while x < 38:
            bw = random.choice([3, 4])
            if random.random() < 0.15:
                x += bw; continue
            c = random.choice(books)
            bh = random.choice([7, 8, 9])
            r(d, x, sy + 10 - bh, bw, bh, c)
            x += bw + 1
        r(d, 1, sy + 10, 42, 2, lo(wood, 10))
    r(d, 0, 28, 44, 2, lo(wood, 30))
    save2x(im, 'prop2_bookcase_low.png')


def gen_partition():
    im, d = canvas(40, 34)
    frame = (110, 80, 50)
    for i, x in enumerate((0, 13, 26)):
        r(d, x, 2 if i % 2 else 0, 14, 30, (220, 208, 180))
        outline(d, x, 2 if i % 2 else 0, 14, 30, frame)
        r(d, x + 2, (2 if i % 2 else 0) + 2, 10, 26, (236, 226, 200))
    save2x(im, 'prop2_partition.png')


def gen_coat_rack():
    im, d = canvas(18, 40)
    r(d, 8, 2, 2, 34, (110, 74, 46))
    d.line([3, 6, 15, 6], fill=(110, 74, 46), width=2)
    d.line([3, 6, 3, 10], fill=(110, 74, 46))
    d.line([15, 6, 15, 10], fill=(110, 74, 46))
    r(d, 1, 9, 6, 12, (170, 90, 80)); outline(d, 1, 9, 6, 12)     # 外套
    r(d, 12, 8, 5, 9, (90, 110, 150)); outline(d, 12, 8, 5, 9)    # 围巾/包
    r(d, 4, 36, 10, 3, (90, 62, 40)); outline(d, 4, 36, 10, 3)
    save2x(im, 'prop2_coatrack.png')


# ---------------- 设备 ----------------
def gen_arcade():
    im, d = canvas(30, 46)
    c = (70, 60, 110)
    r(d, 1, 0, 28, 44, c); outline(d, 1, 0, 28, 44)
    r(d, 2, 1, 3, 42, hi(c))
    r(d, 5, 5, 20, 14, (24, 32, 48)); outline(d, 5, 5, 20, 14)
    d.line([8, 15, 12, 9, 16, 12, 21, 7], fill=(120, 220, 160))
    d.point((10, 8), fill=(240, 200, 110)); d.point((18, 15), fill=(230, 130, 110))
    r(d, 5, 22, 20, 7, (50, 44, 84))                              # 操作台
    d.ellipse([8, 23, 12, 27], fill=(220, 80, 80))                # 摇杆
    d.point((17, 24), fill=(240, 200, 110)); d.point((20, 26), fill=(110, 200, 240))
    r(d, 5, 34, 20, 6, (40, 36, 68))                              # 投币口
    r(d, 13, 36, 4, 2, (20, 18, 30))
    r(d, 1, 44, 28, 2, lo(c, 30))
    save2x(im, 'prop2_arcade.png')


def gen_aquarium():
    im, d = canvas(40, 30)
    r(d, 0, 24, 40, 6, (90, 62, 40)); outline(d, 0, 24, 40, 6)    # 柜座
    r(d, 2, 2, 36, 22, (60, 130, 170)); outline(d, 2, 2, 36, 22)
    r(d, 3, 3, 34, 3, (120, 190, 220))                            # 水面反光
    d.polygon([(8, 20), (10, 16), (12, 20)], fill=(80, 160, 90))  # 水草
    d.polygon([(28, 20), (30, 14), (32, 20)], fill=(80, 160, 90))
    r(d, 14, 10, 5, 3, (240, 150, 80)); d.point((13, 11), fill=(240, 150, 80))   # 鱼
    r(d, 24, 15, 4, 2, (240, 210, 110)); d.point((28, 15), fill=(240, 210, 110))
    for x in range(4, 36, 4):
        d.point((x, 22), fill=(200, 190, 150))                    # 底砂
    r(d, 0, 0, 40, 2, (90, 62, 40)); outline(d, 0, 0, 40, 2)
    save2x(im, 'prop2_aquarium.png')


def gen_floor_lamp():
    im, d = canvas(16, 40)
    r(d, 4, 0, 8, 8, (240, 210, 140)); outline(d, 4, 0, 8, 8)
    r(d, 5, 1, 6, 2, (250, 230, 180))
    r(d, 7, 8, 2, 26, (80, 70, 60))
    d.ellipse([3, 34, 12, 38], fill=(70, 60, 50))
    save2x(im, 'prop2_floorlamp.png')


def gen_fan():
    im, d = canvas(20, 32)
    d.ellipse([2, 0, 17, 15], fill=(190, 200, 210), outline=(110, 120, 130))
    d.ellipse([5, 3, 14, 12], fill=(150, 165, 180))
    d.line([9, 7, 12, 4], fill=(230, 240, 250), width=2)
    d.line([9, 8, 12, 11], fill=(230, 240, 250), width=2)
    d.point((9, 7)); r(d, 9, 15, 2, 12, (110, 120, 130))
    r(d, 4, 28, 12, 3, (110, 120, 130)); outline(d, 4, 28, 12, 3)
    save2x(im, 'prop2_fan.png')


def gen_vacuum():
    im, d = canvas(20, 14)
    d.ellipse([0, 2, 19, 13], fill=(60, 66, 78), outline=(30, 32, 40))
    d.ellipse([3, 4, 16, 10], fill=(84, 92, 108))
    d.point((10, 6), fill=(110, 220, 130))
    save2x(im, 'prop2_vacuum.png')


def gen_trash_bin():
    im, d = canvas(14, 18)
    c = (120, 130, 140)
    r(d, 2, 4, 10, 12, c); outline(d, 2, 4, 10, 12)
    r(d, 3, 5, 2, 10, hi(c))
    r(d, 1, 2, 12, 3, lo(c, 10)); outline(d, 1, 2, 12, 3)
    r(d, 6, 0, 2, 2, lo(c, 10))
    save2x(im, 'prop2_trashbin.png')


def gen_safe():
    im, d = canvas(22, 24)
    c = (90, 96, 108)
    r(d, 0, 0, 22, 22, c); outline(d, 0, 0, 22, 22)
    r(d, 1, 1, 20, 2, hi(c))
    d.ellipse([8, 8, 14, 14], fill=lo(c, 14), outline=(50, 54, 60))
    d.line([11, 9, 11, 11], fill=(220, 220, 220))
    r(d, 17, 9, 2, 5, (60, 64, 72))
    r(d, 0, 22, 22, 2, lo(c, 30))
    save2x(im, 'prop2_safe.png')


# ---------------- 墙面（窗户/挂画/霓虹/搁板） ----------------
def gen_window_night():
    im, d = canvas(34, 26)
    f = (110, 78, 48)
    r(d, 0, 0, 34, 26, f); outline(d, 0, 0, 34, 26)
    r(d, 3, 3, 28, 20, (30, 42, 74)); outline(d, 3, 3, 28, 20, lo(f, 30))
    d.line([17, 3, 17, 22], fill=f, width=2)
    d.line([3, 13, 30, 13], fill=f, width=2)
    for (px, py) in [(7, 7), (12, 10), (24, 6), (27, 11), (9, 18), (22, 17), (26, 20)]:
        d.point((px, py), fill=(230, 230, 190))                   # 星/远灯
    d.ellipse([20, 5, 26, 10], fill=(240, 236, 200))              # 月亮
    d.ellipse([19, 4, 24, 9], fill=(30, 42, 74))
    save2x(im, 'prop2_window_night.png')


def gen_window_blinds():
    im, d = canvas(34, 26)
    f = (150, 155, 165)
    r(d, 0, 0, 34, 26, f); outline(d, 0, 0, 34, 26)
    r(d, 2, 2, 30, 22, (215, 220, 228))
    for y in range(4, 22, 3):
        r(d, 3, y, 28, 2, (180, 186, 196))
    r(d, 3, 20, 28, 3, (150, 200, 235))                           # 底部露出天色
    r(d, 26, 3, 2, 18, (140, 146, 156))                           # 拉绳
    save2x(im, 'prop2_window_blinds.png')


def gen_window_curtain():
    im, d = canvas(38, 28)
    f = (110, 78, 48)
    r(d, 3, 2, 32, 24, f); outline(d, 3, 2, 32, 24)
    r(d, 6, 5, 26, 18, (150, 195, 230)); outline(d, 6, 5, 26, 18, lo(f, 30))
    d.ellipse([10, 7, 18, 12], fill=(240, 245, 250))              # 云
    d.ellipse([15, 9, 24, 13], fill=(240, 245, 250))
    c = (170, 100, 100)
    for x in (0, 30):                                             # 两侧窗帘
        r(d, x, 0, 8, 28, c); outline(d, x, 0, 8, 28)
        d.line([x + 2, 2, x + 2, 25], fill=lo(c, 20))
        d.line([x + 5, 2, x + 5, 25], fill=hi(c, 14))
    r(d, 0, 0, 38, 3, (90, 62, 40)); outline(d, 0, 0, 38, 3)      # 帘杆
    save2x(im, 'prop2_window_curtain.png')


def _painting(name, painter):
    im, d = canvas(26, 20)
    r(d, 0, 0, 26, 20, (110, 78, 48)); outline(d, 0, 0, 26, 20)
    r(d, 2, 2, 22, 16, (60, 70, 90))
    painter(d)
    save2x(im, name)


def gen_paintings():
    def mountain(d):
        r(d, 2, 2, 22, 10, (90, 130, 180))
        d.polygon([(4, 17), (10, 6), (16, 17)], fill=(80, 90, 110))
        d.polygon([(12, 17), (18, 9), (24, 17)], fill=(100, 110, 130))
        d.polygon([(9, 8), (10, 6), (11, 8)], fill=(240, 245, 250))
        d.ellipse([18, 3, 22, 7], fill=(250, 240, 180))
    def abstract(d):
        r(d, 3, 3, 8, 8, (220, 120, 90))
        d.ellipse([12, 6, 22, 16], fill=(110, 170, 150))
        d.line([4, 15, 22, 5], fill=(240, 210, 110), width=2)
    def sunset(d):
        r(d, 2, 2, 22, 8, (240, 150, 90))
        r(d, 2, 10, 22, 8, (90, 70, 110))
        d.ellipse([10, 6, 16, 12], fill=(250, 210, 120))
        d.line([2, 10, 23, 10], fill=(250, 190, 110))
    _painting('prop2_painting_mtn.png', mountain)
    _painting('prop2_painting_abs.png', abstract)
    _painting('prop2_painting_sun.png', sunset)


def gen_neon():
    im, d = canvas(40, 16)
    r(d, 0, 0, 40, 16, (24, 20, 34)); outline(d, 0, 0, 40, 16)
    d.line([4, 8, 10, 4, 14, 11, 18, 5], fill=(240, 110, 180), width=2)   # 波形霓虹
    d.line([22, 10, 26, 4, 30, 10, 35, 6], fill=(110, 220, 230), width=2)
    d.point((6, 12), fill=(240, 110, 180)); d.point((33, 11), fill=(110, 220, 230))
    save2x(im, 'prop2_neon.png')


def gen_wall_shelf():
    im, d = canvas(34, 18)
    r(d, 0, 12, 34, 3, (110, 74, 46)); outline(d, 0, 12, 34, 3)
    r(d, 0, 12, 34, 1, hi((110, 74, 46)))
    r(d, 3, 4, 5, 8, (170, 110, 170))                             # 小摆件
    r(d, 12, 6, 6, 6, (110, 160, 110)); outline(d, 12, 6, 6, 6)
    r(d, 24, 3, 4, 9, (196, 168, 92))
    save2x(im, 'prop2_wallshelf.png')


def gen_globe():
    im, d = canvas(16, 22)
    d.ellipse([1, 0, 14, 13], fill=(90, 150, 200), outline=(50, 80, 120))
    d.polygon([(4, 3), (8, 2), (10, 6), (6, 8)], fill=(110, 170, 110))
    d.polygon([(9, 9), (12, 8), (11, 11)], fill=(110, 170, 110))
    d.line([13, 2, 15, 16], fill=(140, 110, 70), width=2)
    r(d, 5, 16, 6, 2, (110, 74, 46)); r(d, 3, 18, 10, 3, (90, 62, 40))
    save2x(im, 'prop2_globe.png')


def gen_dartboard():
    im, d = canvas(20, 20)
    d.ellipse([0, 0, 19, 19], fill=(60, 50, 40), outline=INK)
    d.ellipse([2, 2, 17, 17], fill=(220, 210, 180))
    d.ellipse([5, 5, 14, 14], fill=(180, 80, 70))
    d.ellipse([8, 8, 11, 11], fill=(60, 120, 70))
    d.line([9, 3, 9, 9], fill=(240, 220, 100))                    # 飞镖
    save2x(im, 'prop2_dartboard.png')


# ---------------- 地板贴片（floorpatch 层，可缩放铺装区域） ----------------
def _tile_to_patch(tile_img, name, reps=3):
    t = tile_img
    patch = Image.new('RGBA', (t.width * reps, t.height * reps))
    for gy in range(reps):
        for gx in range(reps):
            patch.paste(t, (gx * t.width, gy * t.height))
    patch.save(f'{OUT}/{name}')
    print(name, patch.size)


def gen_floor_patches():
    # 现有 5 种材质直接出贴片
    for tname in ('tile_wood', 'tile_wood2', 'tile_carpet', 'tile_tech', 'tile_stone'):
        _tile_to_patch(Image.open(f'{OUT}/{tname}.png'), f'patch_{tname[5:]}.png')
    # 新材质：大理石 / 深木 / 黑白棋盘 / 混凝土 / 草地 / 蓝地毯
    def mk(name, painter):
        im, d = canvas(32, 32)
        painter(d)
        big = im.resize((64, 64), Image.NEAREST)
        big.save(f'{OUT}/tile_{name}.png')
        _tile_to_patch(big, f'patch_{name}.png')
    def marble(d):
        r(d, 0, 0, 32, 32, (214, 214, 210))
        for gx, gy in ((0, 0), (16, 16)):
            r(d, gx, gy, 16, 16, (226, 226, 224))
        for _ in range(6):
            x, y = random.randint(2, 28), random.randint(2, 28)
            d.line([x, y, x + random.randint(2, 5), y + random.randint(1, 3)], fill=(190, 192, 194))
        d.line([0, 0, 0, 31], fill=(196, 196, 194)); d.line([0, 0, 31, 0], fill=(196, 196, 194))
    def darkwood(d):
        base = (74, 52, 36)
        for row, y in enumerate(range(0, 32, 8)):
            c = (base[0] + (5 if row % 2 else 0), base[1] + (3 if row % 2 else 0), base[2])
            r(d, 0, y, 32, 8, c)
            r(d, 0, y, 32, 1, hi(c, 14)); r(d, 0, y + 7, 32, 1, lo(c, 14))
            d.line([random.randint(4, 26), y + 2, random.randint(4, 26), y + 5], fill=lo(c, 8))
    def checker(d):
        for gy in range(2):
            for gx in range(2):
                c = (232, 230, 224) if (gx + gy) % 2 == 0 else (52, 52, 58)
                r(d, gx * 16, gy * 16, 16, 16, c)
                r(d, gx * 16, gy * 16, 16, 1, hi(c, 10))
    def concrete(d):
        r(d, 0, 0, 32, 32, (150, 150, 148))
        for _ in range(14):
            d.point((random.randint(0, 31), random.randint(0, 31)), fill=(138, 138, 136))
        d.line([0, 0, 31, 0], fill=(162, 162, 160)); d.line([0, 16, 31, 16], fill=(140, 140, 138))
    def grass(d):
        r(d, 0, 0, 32, 32, (96, 140, 76))
        for _ in range(20):
            x, y = random.randint(0, 30), random.randint(0, 30)
            d.point((x, y), fill=(116, 160, 90)); d.point((x + 1, y), fill=(84, 124, 66))
    def carpet_blue(d):
        r(d, 0, 0, 32, 32, (86, 104, 140))
        for gy in range(0, 32, 8):
            for gx in range(0, 32, 8):
                d.point((gx + 4, gy + 4), fill=(104, 124, 160))
        d.line([0, 0, 31, 0], fill=(98, 118, 154))
    mk('marble', marble); mk('darkwood', darkwood); mk('checker', checker)
    mk('concrete', concrete); mk('grass', grass); mk('carpetblue', carpet_blue)


if __name__ == '__main__':
    for fn in [gen_armchair_green, gen_sofa_blue, gen_beanbag, gen_chair_office,
               gen_stool, gen_bench, gen_side_table, gen_coffee_table, gen_tv_stand,
               gen_bar_counter, gen_locker, gen_bookcase_low, gen_partition,
               gen_coat_rack, gen_arcade, gen_aquarium, gen_floor_lamp, gen_fan,
               gen_vacuum, gen_trash_bin, gen_safe, gen_window_night,
               gen_window_blinds, gen_window_curtain, gen_paintings, gen_neon,
               gen_wall_shelf, gen_globe, gen_dartboard, gen_floor_patches]:
        fn()
    print('done')
