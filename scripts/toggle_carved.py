#!/usr/bin/env python3
"""Toggle carved archive files between dump tree and a reversible backup dir.

Usage:
  python toggle_carved.py out   # move all manifest-listed files to backup
  python toggle_carved.py in    # restore them to the dump tree

Only files listed in the two manifests are ever touched (iron rule).
"""
import os
import shutil
import sys

BACKUP = r'C:\GTAVI\PS5\logs\carved-backup'
MANIFESTS = [
    r'C:\GTAVI\PS5\logs\carve-placed-manifest.txt',
    r'C:\GTAVI\PS5\logs\carve2-placed-manifest.txt',
]


def listed_files():
    out = []
    for m in MANIFESTS:
        if not os.path.exists(m):
            continue
        for line in open(m, encoding='utf-8', errors='replace'):
            p = line.split('\t')[0].strip()
            if p and os.path.isabs(p):
                out.append(p)
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'out'
    os.makedirs(BACKUP, exist_ok=True)
    n = 0
    for p in listed_files():
        if not os.path.exists(p):
            continue
        if mode == 'out':
            dst = os.path.join(BACKUP, os.path.basename(p))
            # avoid collisions: prefix with parent dir name
            parent = os.path.basename(os.path.dirname(p))
            dst = os.path.join(BACKUP, parent + '__' + os.path.basename(p))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(p, dst)
            n += 1
        elif mode == 'in':
            # out-mode names backup as <immediate parent basename>__<basename>
            # derive the same key from the manifest path's parent dir
            parent = os.path.basename(os.path.dirname(p))
            src = os.path.join(BACKUP, parent + '__' + os.path.basename(p))
            if os.path.exists(src):
                os.makedirs(os.path.dirname(p), exist_ok=True)
                if os.path.exists(p):
                    os.remove(p)
                shutil.move(src, p)
                n += 1
            else:
                print('MISSING BACKUP:', src)
    print('%s: %d files' % (mode, n))


if __name__ == '__main__':
    main()
