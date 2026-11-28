#!/usr/bin/env python3
"""Auto bisect: restore a subset of carved files, run kyty, screenshot the
topmost window, classify black-vs-rendered, then clean up.

Usage:
  python bisect_carved.py 1,2,3,4,5      # restore manifest lines 1-5
  python bisect_carved.py none            # clean baseline (no files)

Prints a JSON-ish verdict line at the end: VERDICT rendered|black N_COLORS=<n>
"""
import ctypes
import ctypes.wintypes as wt
import glob
import os
import shutil
import subprocess
import sys
import time
from collections import Counter

from PIL import Image, ImageGrab

BACKUP = r'C:\GTAVI\PS5\logs\carved-backup'
MANIFEST = r'C:\GTAVI\PS5\logs\carve-placed-manifest.txt'
KYTY = r'C:\GTAVI\PS5\tools\KytyPS5-20261126\kyty_clean.exe'
GAME = r'C:\GTAVI\PS5\games\GTA6-dump\GTAVIPS5'
LOGDIR = r'C:\GTAVI\PS5\logs'
SHOTDIR = r'C:\GTAVI\PS5\logs\play-shots'
RUN_SECONDS = 75


def manifest_lines():
    out = []
    for line in open(MANIFEST, encoding='utf-8', errors='replace'):
        p = line.split('\t')[0].strip()
        if p and os.path.isabs(p):
            out.append(p)
    return out


def backup_key(p):
    return os.path.join(BACKUP,
                        os.path.basename(os.path.dirname(p)) + '__' + os.path.basename(p))


def restore(indices):
    lines = manifest_lines()
    restored = []
    for i in indices:
        if i < 1 or i > len(lines):
            continue
        p = lines[i - 1]
        src = backup_key(p)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            if os.path.exists(p):
                os.remove(p)
            shutil.move(src, p)
            restored.append(p)
    return restored


def cleanup(restored):
    for p in restored:
        if os.path.exists(p):
            os.remove(p)


def find_kyty_window():
    u = ctypes.windll.user32
    found = []
    CB = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)

    def cb(h, l):
        if u.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, b, 256)
            if 'Kyty' in b.value:
                found.append((h, b.value))
        return True

    u.EnumWindows(CB(cb), 0)
    return found


def topmost_shot(h, path):
    u = ctypes.windll.user32
    u.SetWindowPos(h, ctypes.c_void_p(-1), 0, 0, 0, 0, 0x0001 | 0x0040)
    u.BringWindowToTop(h)
    u.SetForegroundWindow(h)
    time.sleep(1.5)
    r = wt.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    im = ImageGrab.grab(bbox=(max(0, r.left), max(0, r.top),
                              min(3840, r.right), min(2160, r.bottom)))
    im.save(path)
    return im


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else 'none'
    indices = [] if arg == 'none' else [int(x) for x in arg.split(',') if x.strip()]
    tag = 'none' if not indices else '-'.join(map(str, indices))
    log = os.path.join(LOGDIR, 'bisect-%s-%s.log' % (tag, time.strftime('%H%M%S')))
    shot = os.path.join(SHOTDIR, 'bisect-%s.png' % tag)

    restored = restore(indices)
    print('RESTORED', len(restored), [os.path.basename(x) for x in restored], flush=True)
    confirm_proc = None
    try:
        with open(log, 'w', errors='replace') as fh:
            proc = subprocess.Popen([KYTY, '--game', GAME,
                                     '--printf-direction', 'File',
                                     '--printf-output-file', log,
                                     '--perf-overlay', '--shader-cache'],
                                    stdout=fh, stderr=subprocess.STDOUT)
        # auto_confirm drives past notice/CONTINUE screens -> title art
        confirm = os.path.join(os.path.dirname(__file__), 'auto_confirm.py')
        confirm_proc = subprocess.Popen([sys.executable, confirm, '8', '300', 'JL'],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
        try:
            deadline = time.time() + RUN_SECONDS
            wins = []
            while time.time() < deadline:
                wins = find_kyty_window()
                if wins:
                    break
                time.sleep(1)
            print('WINDOW', [(hex(h), t[:70]) for h, t in wins], flush=True)
            if wins:
                # wait for title screen to stabilise: poll title for frame count
                hwnd = wins[0][0]
                stab_deadline = time.time() + 60
                title = wins[0][1]
                while time.time() < stab_deadline:
                    b = ctypes.create_unicode_buffer(256)
                    ctypes.windll.user32.GetWindowTextW(hwnd, b, 256)
                    title = b.value
                    import re as _re
                    m = _re.search(r'frame:\s*(\d+)', title)
                    if m and int(m.group(1)) >= 400:
                        break
                    if time.time() > deadline:
                        break
                    time.sleep(2)
                print('TITLE', title[:110], flush=True)
                im = topmost_shot(hwnd, shot)
                # analyze full game area excluding title bar (top 45px)
                w, h = im.size
                c = Counter()
                for y in range(50, min(h, h - 5), 6):
                    for x in range(5, min(w, w - 5), 6):
                        c[im.getpixel((x, y))] += 1
                ncolors = len(c)
                top = c.most_common(4)
                total = sum(c.values())
                top_frac = top[0][1] / total if total else 0
                print('COLORS', ncolors, 'top_frac=%.2f' % top_frac, top, flush=True)
                # poisoned state = uniform (32,32,44); clean title = colorful (many colors)
                # early black = (0,0,0) with low frame count -> inconclusive
                main = top[0][0]
                if main == (32, 32, 44) and top_frac > 0.85:
                    verdict = 'black'
                elif ncolors >= 15 and main != (32, 32, 44):
                    verdict = 'rendered'
                else:
                    verdict = 'inconclusive'
                print('VERDICT', verdict, 'N_COLORS=%d' % ncolors,
                      'MAIN=%s' % str(main), flush=True)
            else:
                print('VERDICT no_window', flush=True)
        finally:
            if confirm_proc is not None:
                confirm_proc.terminate()
                try:
                    confirm_proc.wait(timeout=3)
                except Exception:
                    confirm_proc.kill()
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    finally:
        cleanup(restored)
        print('CLEANED', len(restored), flush=True)


if __name__ == '__main__':
    main()
