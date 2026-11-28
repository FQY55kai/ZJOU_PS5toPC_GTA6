# -*- coding: utf-8 -*-
# 周期截屏：每 10s 一张，共 30 张（5 分钟），文件名带时间戳
import time, os
from PIL import ImageGrab
out = r"C:\GTAVI\PS5\logs\overlay-shots"
os.makedirs(out, exist_ok=True)
for i in range(30):
    ts = time.strftime("%H%M%S")
    im = ImageGrab.grab()
    p = os.path.join(out, "shot-%02d-%s.png" % (i, ts))
    im.save(p)
    print(p, flush=True)
    if i < 29:
        time.sleep(10)
