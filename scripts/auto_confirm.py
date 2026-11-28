# -*- coding: utf-8 -*-
# 每 20 秒自动按一次确定键（J = PAD_BUTTON_CROSS，Kyty hostInput 映射）
# 用法: python auto_confirm.py [间隔秒数] [总时长秒数]
import ctypes, ctypes.wintypes as wt, time, sys

user32 = ctypes.windll.user32
INTERVAL = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
TOTAL = float(sys.argv[2]) if len(sys.argv) > 2 else 480.0

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_J = 0x4A

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wt.DWORD), ("u", _INPUTUNION)]

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

def send_key(vk, flags):
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.u.ki = KEYBDINPUT(vk, 0, flags, 0, None)
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def press_cross(hwnd):
    fg = user32.GetForegroundWindow()
    if fg != hwnd:
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.08)
    send_key(VK_J, 0)
    time.sleep(0.07)
    send_key(VK_J, KEYEVENTF_KEYUP)

start = time.time()
n = 0
while time.time() - start < TOTAL:
    hwnd = find_kyty()
    if hwnd:
        press_cross(hwnd)
        n += 1
        print("press %d ok hwnd=%s t=%.0fs" % (n, hex(hwnd), time.time()-start), flush=True)
    else:
        print("kyty window not found, skip t=%.0fs" % (time.time()-start), flush=True)
    time.sleep(INTERVAL)
print("done, total presses:", n)
