# -*- coding: utf-8 -*-
# 自动确认键循环：每 N 秒按一次 Cross(J)，附带 Circle(L) 兜底
# 方法：PostMessage WM_KEYDOWN/UP 直投 Kyty 窗口（不依赖前台焦点）+ SendInput 备份
# 用法: python auto_confirm.py [间隔秒] [总时长秒] [按键序列，如 JL]
import ctypes, ctypes.wintypes as wt, time, sys

user32 = ctypes.windll.user32
INTERVAL = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
TOTAL = float(sys.argv[2]) if len(sys.argv) > 2 else 480.0
KEYS = sys.argv[3] if len(sys.argv) > 3 else "JL"

WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
KEYEVENTF_KEYUP = 0x0002
INPUT_KEYBOARD = 1

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
class _U(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]
class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wt.DWORD), ("u", _U)]

def find_kyty():
    found = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, lp):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, buf, 256)
            if "Kyty" in buf.value:
                found.append(hwnd)
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return found[0] if found else None

def press_vk(hwnd, vk):
    scan = user32.MapVirtualKeyW(vk, 0)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 1 | (scan << 16))
    time.sleep(0.06)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 1 | (scan << 16) | (1 << 30) | (1 << 31))
    # SendInput 备份（若窗口在前台也能收到）
    for flags in (0, KEYEVENTF_KEYUP):
        inp = INPUT(type=INPUT_KEYBOARD)
        inp.u.ki = KEYBDINPUT(vk, 0, flags, 0, None)
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

start = time.time()
n = 0
while time.time() - start < TOTAL:
    hwnd = find_kyty()
    if hwnd:
        for ch in KEYS:
            press_vk(hwnd, ord(ch.upper()))
            time.sleep(0.15)
        n += 1
        print("press %d keys=%s t=%.0fs" % (n, KEYS, time.time()-start), flush=True)
    else:
        print("kyty window not found, skip t=%.0fs" % (time.time()-start), flush=True)
    time.sleep(INTERVAL)
print("done, total press cycles:", n)
