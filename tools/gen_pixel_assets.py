#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""像素办公室 v3 素材生成器：墙体贴图 + 道具集
半分辨率绘制 → 2x 最近邻放大，保证像素颗粒感。输出到 frontend/。
"""
import random
from PIL import Image, ImageDraw

random.seed(42)
OUT = '/home/aexmo/auplus-pixel-office/frontend'

INK = (30, 22, 14, 255)          # 统一深色描边


def canvas(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save2x(im, name):
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(f'{OUT}/{name}')
    print(name, im.width * 2, 'x', im.height * 2)


def r(d, x, y, w, h, c):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def outline(d, x, y, w, h, c=INK):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=c)


# ---------------------------------------------------------------- 墙体贴图
def gen_wall_face():
    # 32x30 (1x) -> 64x60：横向木板墙面 + 底部踢脚线
    im, d = canvas(32, 30)
    base = (122, 84, 54)
    for row, y in enumerate(range(0, 24, 6)):
        c = (base[0] + (6 if row % 2 else 0), base[1] + (4 if row % 2 else 0), base[2])
        r(d, 0, y, 32, 6, c)
        r(d, 0, y, 32, 1, (min(255, c[0] + 26), min(255, c[1] + 20), c[2] + 12))  # 板上高光
        r(d, 0, y + 5, 32, 1, (78, 52, 32))                                       # 板缝
        for _ in range(3):  # 木纹点
            wx = random.randint(1, 30)
            d.point((wx, y + random.randint(2, 4)), fill=(96, 64, 40))
    r(d, 0, 24, 32, 6, (64, 44, 30))   # 踢脚线
    r(d, 0, 24, 32, 1, (150, 108, 70))
    save2x(im, 'wall_face.png')


def gen_wall_cap():
    # 32x8 (1x) -> 64x16：墙顶(近黑深棕 + 顶缘高光)
    im, d = canvas(32, 8)
    r(d, 0, 0, 32, 8, (44, 32, 24))
    r(d, 0, 0, 32, 1, (92, 70, 50))
    r(d, 0, 7, 32, 1, (24, 16, 10))
    for _ in range(6):
        d.point((random.randint(0, 31), random.randint(2, 6)), fill=(56, 42, 30))
    save2x(im, 'wall_cap.png')


def gen_tile_stone():
    # 32x32 (1x) -> 64x64：灰蓝棋盘石板（参考 Mountain Lodge 公共区）
    im, d = canvas(32, 32)
    a, b = (116, 122, 138), (100, 106, 122)
    for gy in range(2):
        for gx in range(2):
            c = a if (gx + gy) % 2 == 0 else b
            x, y = gx * 16, gy * 16
            r(d, x, y, 16, 16, c)
            r(d, x, y, 16, 1, (min(255, c[0] + 16), min(255, c[1] + 16), min(255, c[2] + 16)))
            r(d, x, y + 15, 16, 1, (c[0] - 18, c[1] - 18, c[2] - 18))
            r(d, x + 15, y, 1, 16, (c[0] - 12, c[1] - 12, c[2] - 12))
            for _ in range(4):
                d.point((x + random.randint(2, 13), y + random.randint(2, 13)),
                        fill=(c[0] - 10, c[1] - 10, c[2] - 6))
    save2x(im, 'tile_stone.png')


# ---------------------------------------------------------------- 家具道具
def gen_bookshelf():
    # 46x64 -> 92x128 木书架 + 彩色书脊
    im, d = canvas(46, 64)
    wood, dark = (110, 74, 46), (84, 56, 34)
    r(d, 0, 0, 46, 64, wood)
    outline(d, 0, 0, 46, 64)
    r(d, 1, 1, 44, 3, (140, 98, 62))                 # 顶板
    books = [(196, 92, 80), (108, 140, 180), (196, 168, 92), (110, 160, 110),
             (170, 110, 170), (220, 140, 90), (120, 120, 190), (200, 200, 190)]
    for shelf in range(3):
        sy = 6 + shelf * 19
        r(d, 2, sy, 42, 16, (62, 42, 26))            # 格内阴影
        x = 3
        while x < 40:
            bw = random.choice([3, 4, 5])
            bh = random.choice([12, 13, 14])
            if x + bw > 42:
                break
            if random.random() < 0.14:               # 留空隙
                x += bw
                continue
            c = random.choice(books)
            r(d, x, sy + 16 - bh, bw, bh, c)
            r(d, x, sy + 16 - bh, bw, 1, tuple(min(255, v + 30) for v in c))
            x += bw + 1
        r(d, 1, sy + 16, 44, 3, dark)                # 隔板
        r(d, 1, sy + 16, 44, 1, (140, 98, 62))
    save2x(im, 'prop_bookshelf.png')


def gen_whiteboard():
    # 58x36 -> 116x72 白板（挂墙）
    im, d = canvas(58, 36)
    r(d, 0, 0, 58, 32, (168, 130, 88))
    outline(d, 0, 0, 58, 32)
    r(d, 3, 3, 52, 26, (238, 240, 236))
    r(d, 3, 3, 52, 1, (255, 255, 255))
    # 涂写内容：折线图 + 字迹线
    for i, (x1, y1, x2, y2) in enumerate([(7, 22, 14, 12), (14, 12, 22, 18), (22, 18, 30, 8)]):
        d.line([x1, y1, x2, y2], fill=(74, 116, 180), width=1)
    for y in (9, 13, 17):
        d.line([36, y, 50, y], fill=(190, 90, 90) if y == 9 else (110, 110, 120), width=1)
    r(d, 6, 32, 46, 3, (140, 104, 66))               # 笔槽
    r(d, 10, 31, 6, 2, (200, 70, 70))                # 笔
    r(d, 20, 31, 6, 2, (70, 110, 200))
    save2x(im, 'prop_whiteboard.png')


def gen_pinboard():
    # 48x34 -> 96x68 软木公告板
    im, d = canvas(48, 34)
    r(d, 0, 0, 48, 34, (120, 86, 52))
    outline(d, 0, 0, 48, 34)
    r(d, 3, 3, 42, 28, (196, 158, 108))
    notes = [(214, 214, 150), (170, 210, 170), (230, 170, 160), (160, 190, 230), (230, 210, 140)]
    for i in range(5):
        nx, ny = 5 + (i % 3) * 14, 5 + (i // 3) * 13
        c = notes[i]
        r(d, nx, ny + 1, 11, 10, (150, 120, 80))     # 纸影
        r(d, nx, ny, 11, 10, c)
        d.point((nx + 5, ny), fill=(200, 60, 60))    # 图钉
        for ly in range(ny + 3, ny + 9, 2):
            d.line([nx + 2, ly, nx + 8, ly], fill=(120, 110, 90))
    save2x(im, 'prop_pinboard.png')


def gen_water_cooler():
    # 20x44 -> 40x88 饮水机
    im, d = canvas(20, 44)
    r(d, 3, 12, 14, 28, (228, 230, 234))             # 机身
    outline(d, 3, 12, 14, 28)
    r(d, 4, 13, 3, 26, (250, 250, 252))              # 高光
    r(d, 4, 2, 12, 11, (150, 200, 235))              # 水桶
    outline(d, 4, 2, 12, 11)
    r(d, 6, 4, 3, 7, (200, 230, 250))
    r(d, 6, 22, 3, 4, (90, 150, 210))                # 冷热龙头
    r(d, 11, 22, 3, 4, (210, 100, 90))
    r(d, 5, 28, 10, 4, (180, 184, 190))              # 接水槽
    r(d, 2, 40, 16, 3, (120, 124, 130))              # 底座
    outline(d, 2, 40, 16, 3)
    save2x(im, 'prop_watercooler.png')


def gen_vending():
    # 36x56 -> 72x112 自动售货机
    im, d = canvas(36, 56)
    r(d, 0, 0, 36, 54, (176, 58, 58))
    outline(d, 0, 0, 36, 54)
    r(d, 1, 1, 3, 52, (208, 84, 78))                 # 侧高光
    r(d, 4, 4, 20, 40, (46, 56, 74))                 # 玻璃橱窗
    outline(d, 4, 4, 20, 40)
    d.line([6, 6, 20, 6], fill=(120, 150, 190))      # 玻璃反光
    items = [(230, 190, 90), (110, 190, 140), (220, 130, 90), (140, 160, 220), (240, 220, 160), (200, 100, 140)]
    for row in range(4):
        ry = 9 + row * 9
        for col in range(4):
            c = random.choice(items)
            r(d, 6 + col * 5, ry, 4, 5, c)
            r(d, 6 + col * 5, ry, 4, 1, tuple(min(255, v + 26) for v in c))
        r(d, 5, ry + 6, 18, 1, (90, 100, 120))       # 货架
    r(d, 26, 8, 7, 10, (240, 240, 235))              # 面板
    r(d, 27, 20, 5, 2, (30, 30, 30))                 # 投币口
    r(d, 27, 24, 5, 5, (60, 70, 90))                 # 按钮区
    r(d, 5, 46, 18, 6, (40, 40, 46))                 # 取物口
    r(d, 0, 54, 36, 2, (60, 26, 26))                 # 底座
    save2x(im, 'prop_vending.png')


def gen_fridge():
    # 28x48 -> 56x96 双门冰箱
    im, d = canvas(28, 48)
    r(d, 0, 0, 28, 46, (216, 222, 228))
    outline(d, 0, 0, 28, 46)
    r(d, 1, 1, 4, 44, (240, 244, 248))               # 高光
    r(d, 1, 16, 26, 2, (160, 168, 176))              # 冷冻/冷藏分界
    r(d, 22, 5, 2, 8, (120, 128, 136))               # 把手
    r(d, 22, 20, 2, 12, (120, 128, 136))
    r(d, 4, 21, 8, 6, (250, 250, 250))               # 便签磁贴
    d.line([5, 23, 10, 23], fill=(150, 150, 160))
    d.line([5, 25, 9, 25], fill=(150, 150, 160))
    r(d, 0, 46, 28, 2, (110, 116, 124))              # 底
    save2x(im, 'prop_fridge.png')


def gen_kitchen():
    # 76x38 -> 152x76 厨房台（水槽+微波炉+水壶）
    im, d = canvas(76, 38)
    r(d, 0, 8, 76, 6, (196, 200, 206))               # 台面
    outline(d, 0, 8, 76, 6)
    r(d, 0, 8, 76, 1, (232, 236, 240))
    r(d, 0, 14, 76, 22, (128, 90, 58))               # 柜体
    outline(d, 0, 14, 76, 22)
    for cx in (2, 27, 52):                           # 柜门
        r(d, cx, 17, 22, 16, (146, 104, 68))
        outline(d, cx, 17, 22, 16, (94, 64, 40))
        r(d, cx + 9, 24, 4, 2, (80, 56, 36))
    r(d, 6, 9, 18, 4, (150, 158, 168))               # 水槽
    outline(d, 6, 9, 18, 4)
    r(d, 14, 4, 2, 5, (170, 176, 184))               # 龙头
    r(d, 12, 3, 6, 2, (170, 176, 184))
    r(d, 32, 0, 20, 9, (70, 74, 82))                 # 微波炉
    outline(d, 32, 0, 20, 9)
    r(d, 34, 2, 11, 5, (40, 46, 58))
    d.point((48, 3), fill=(120, 220, 140))
    r(d, 60, 2, 8, 7, (200, 90, 80))                 # 水壶
    outline(d, 60, 2, 8, 7)
    r(d, 62, 0, 4, 2, (150, 60, 56))
    r(d, 0, 36, 76, 2, (74, 50, 32))
    save2x(im, 'prop_kitchen.png')


def gen_printer():
    # 32x30 -> 64x60 打印机
    im, d = canvas(32, 30)
    r(d, 2, 8, 28, 16, (188, 192, 198))
    outline(d, 2, 8, 28, 16)
    r(d, 3, 9, 26, 2, (220, 224, 230))
    r(d, 6, 2, 20, 7, (168, 172, 178))               # 上盖/进纸
    outline(d, 6, 2, 20, 7)
    r(d, 9, 0, 14, 3, (245, 246, 248))               # 纸
    r(d, 5, 14, 16, 5, (60, 66, 78))                 # 出纸口
    r(d, 7, 13, 12, 3, (245, 246, 248))
    d.point((26, 11), fill=(110, 220, 130))          # 状态灯
    r(d, 24, 15, 4, 3, (90, 96, 106))                # 按钮
    r(d, 2, 24, 28, 4, (120, 124, 132))              # 底座
    outline(d, 2, 24, 28, 4)
    save2x(im, 'prop_printer.png')


def gen_meeting_table():
    # 88x52 -> 176x104 会议桌+椅子
    im, d = canvas(88, 52)
    chair, chair_hi = (72, 88, 110), (96, 114, 138)
    for cx in (14, 38, 62):                          # 上排椅背
        r(d, cx, 2, 12, 8, chair)
        outline(d, cx, 2, 12, 8)
        r(d, cx + 1, 3, 10, 2, chair_hi)
    r(d, 4, 10, 80, 30, (140, 96, 60))               # 桌面
    outline(d, 4, 10, 80, 30)
    r(d, 5, 11, 78, 3, (172, 122, 78))               # 桌面高光
    r(d, 6, 14, 76, 24, (150, 104, 66))
    for px_ in (16, 40, 64):                         # 桌上文件/笔电
        r(d, px_, 18, 10, 7, (240, 240, 236))
        d.line([px_ + 2, 20, px_ + 8, 20], fill=(140, 140, 150))
        d.line([px_ + 2, 22, px_ + 7, 22], fill=(140, 140, 150))
    r(d, 40, 28, 9, 6, (60, 66, 80))                 # 笔电
    r(d, 41, 29, 7, 4, (110, 170, 220))
    for cx in (14, 38, 62):                          # 下排椅子
        r(d, cx, 42, 12, 8, chair)
        outline(d, cx, 42, 12, 8)
        r(d, cx + 1, 43, 10, 2, chair_hi)
    save2x(im, 'prop_meeting_table.png')


def gen_rug():
    # 70x44 -> 140x88 圆角地毯
    im, d = canvas(70, 44)
    d.ellipse([0, 0, 69, 43], fill=(150, 92, 78))
    d.ellipse([4, 3, 65, 40], fill=(186, 120, 96))
    d.ellipse([10, 7, 59, 36], fill=(206, 150, 116))
    d.ellipse([18, 12, 51, 31], fill=(186, 120, 96))
    for _ in range(20):                              # 织物噪点
        d.point((random.randint(8, 61), random.randint(6, 37)), fill=(170, 108, 88))
    save2x(im, 'prop_rug.png')


def gen_clock():
    # 16x16 -> 32x32 挂钟
    im, d = canvas(16, 16)
    d.ellipse([0, 0, 15, 15], fill=(90, 62, 40))
    d.ellipse([2, 2, 13, 13], fill=(240, 240, 234))
    d.line([8, 8, 8, 4], fill=(40, 40, 46))
    d.line([8, 8, 11, 9], fill=(40, 40, 46))
    d.point((8, 3), fill=(140, 140, 150))
    d.point((8, 13), fill=(140, 140, 150))
    d.point((3, 8), fill=(140, 140, 150))
    d.point((13, 8), fill=(140, 140, 150))
    save2x(im, 'prop_clock.png')


def gen_tv():
    # 54x34 -> 108x68 壁挂大屏(数据看板)
    im, d = canvas(54, 34)
    r(d, 0, 0, 54, 32, (40, 44, 52))
    outline(d, 0, 0, 54, 32)
    r(d, 2, 2, 50, 28, (24, 32, 48))
    bars = [(90, 200, 140), (110, 170, 230), (240, 200, 110), (230, 130, 110), (150, 130, 220)]
    for i, c in enumerate(bars):                     # 柱状图
        h = random.randint(6, 18)
        r(d, 5 + i * 6, 28 - h, 4, h, c)
    d.line([34, 24, 40, 14, 46, 18, 50, 8], fill=(120, 220, 160), width=1)  # 折线
    r(d, 34, 5, 16, 5, (60, 70, 90))                 # 标题条
    r(d, 24, 32, 6, 2, (70, 76, 86))                 # 挂架
    save2x(im, 'prop_tv.png')


def gen_cabinet():
    # 23x39 -> 46x78 文件柜
    im, d = canvas(23, 39)
    r(d, 0, 0, 23, 37, (130, 138, 148))
    outline(d, 0, 0, 23, 37)
    r(d, 1, 1, 3, 35, (160, 168, 178))
    for i in range(3):
        dy = 3 + i * 11
        r(d, 3, dy, 17, 9, (110, 118, 128))
        outline(d, 3, dy, 17, 9, (70, 76, 86))
        r(d, 8, dy + 3, 7, 2, (60, 66, 76))          # 拉手
        r(d, 5, dy + 1, 5, 2, (200, 200, 190))       # 标签
    r(d, 0, 37, 23, 2, (80, 86, 96))
    save2x(im, 'prop_cabinet.png')


def gen_boxes():
    # 38x32 -> 76x64 纸箱堆
    im, d = canvas(38, 32)
    def box(x, y, w, h):
        r(d, x, y, w, h, (188, 142, 92))
        outline(d, x, y, w, h)
        r(d, x + 1, y + 1, w - 2, 2, (212, 168, 116))
        d.line([x + w // 2, y + 1, x + w // 2, y + h - 2], fill=(150, 108, 66))
        r(d, x + 2, y + h // 2, 6, 3, (240, 236, 220))   # 快递单
    box(2, 14, 18, 16)
    box(19, 16, 17, 14)
    box(9, 2, 16, 13)
    save2x(im, 'prop_boxes.png')


def gen_fireplace():
    # 56x58 -> 112x116 石砌壁炉（参考 Mountain Lodge）
    im, d = canvas(56, 58)
    stone, stone_d = (140, 140, 148), (112, 112, 122)
    r(d, 2, 6, 52, 50, stone)                        # 炉体
    outline(d, 2, 6, 52, 50)
    for sy in range(7, 54, 6):                       # 石块纹
        off = 4 if (sy // 6) % 2 else 0
        for sx in range(3 + off, 50, 9):
            outline(d, sx, sy, 8, 5, stone_d)
    r(d, 0, 2, 56, 5, (120, 120, 130))               # 炉檐
    outline(d, 0, 2, 56, 5)
    r(d, 1, 2, 54, 1, (170, 170, 178))
    r(d, 14, 20, 28, 28, (30, 22, 20))               # 炉膛
    d.ellipse([12, 16, 43, 26], fill=(30, 22, 20))
    # 火焰
    d.polygon([(20, 46), (24, 30), (28, 40), (31, 26), (34, 42), (37, 34), (38, 46)], fill=(232, 120, 46))
    d.polygon([(24, 46), (27, 36), (30, 42), (32, 34), (35, 46)], fill=(250, 190, 80))
    r(d, 26, 44, 5, 2, (255, 235, 160))
    r(d, 16, 46, 24, 3, (70, 50, 40))                # 柴
    r(d, 12, 49, 32, 3, (90, 66, 48))
    r(d, 0, 54, 56, 4, (100, 100, 110))              # 炉底座
    outline(d, 0, 54, 56, 4)
    save2x(im, 'prop_fireplace.png')


def gen_caution():
    # 20x30 -> 40x60 Bug区警示牌
    im, d = canvas(20, 30)
    r(d, 9, 12, 2, 16, (140, 144, 152))              # 杆
    d.polygon([(10, 0), (19, 14), (1, 14)], fill=(240, 200, 70))
    d.polygon([(10, 2), (17, 13), (3, 13)], outline=(60, 50, 20))
    r(d, 9, 5, 2, 5, (40, 36, 20))                   # 感叹号
    d.point((10, 11), fill=(40, 36, 20))
    r(d, 5, 27, 10, 2, (110, 114, 122))              # 底座
    save2x(im, 'prop_caution.png')


def gen_trophy():
    # 30x24 -> 60x48 奖杯架（老板室）
    im, d = canvas(30, 24)
    r(d, 0, 18, 30, 4, (110, 74, 46))                # 搁板
    outline(d, 0, 18, 30, 4)
    r(d, 0, 18, 30, 1, (146, 102, 64))
    def cup(x, gold=True):
        c = (222, 178, 74) if gold else (190, 194, 202)
        hi = (250, 220, 130) if gold else (228, 232, 240)
        r(d, x + 1, 4, 6, 6, c)
        d.point((x + 2, 5), fill=hi)
        r(d, x, 4, 1, 4, c)
        r(d, x + 7, 4, 1, 4, c)
        r(d, x + 3, 10, 2, 3, c)
        r(d, x + 1, 13, 6, 3, (140, 96, 52))
    cup(3, True)
    cup(13, False)
    cup(22, True)
    save2x(im, 'prop_trophy.png')


def gen_mat():
    # 46x20 -> 92x40 入口地垫
    im, d = canvas(46, 20)
    r(d, 0, 0, 46, 20, (96, 60, 46))
    outline(d, 0, 0, 46, 20)
    r(d, 3, 3, 40, 14, (150, 96, 70))
    for x in range(6, 40, 5):
        r(d, x, 5, 2, 10, (120, 76, 56))
    save2x(im, 'prop_mat.png')


def gen_plate():
    # 房间名木牌九宫格底 44x14 -> 88x28
    im, d = canvas(44, 14)
    r(d, 0, 0, 44, 14, (74, 50, 32))
    outline(d, 0, 0, 44, 14)
    r(d, 1, 1, 42, 12, (116, 78, 48))
    r(d, 1, 1, 42, 1, (150, 106, 66))
    d.point((2, 2), fill=(200, 170, 120))            # 钉子
    d.point((41, 2), fill=(200, 170, 120))
    d.point((2, 11), fill=(200, 170, 120))
    d.point((41, 11), fill=(200, 170, 120))
    save2x(im, 'prop_plate.png')


if __name__ == '__main__':
    for fn in [gen_wall_face, gen_wall_cap, gen_tile_stone, gen_bookshelf,
               gen_whiteboard, gen_pinboard, gen_water_cooler, gen_vending,
               gen_fridge, gen_kitchen, gen_printer, gen_meeting_table,
               gen_rug, gen_clock, gen_tv, gen_cabinet, gen_boxes,
               gen_fireplace, gen_caution, gen_trophy, gen_mat, gen_plate]:
        fn()
    print('done')
