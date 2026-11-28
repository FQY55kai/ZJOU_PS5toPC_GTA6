#!/usr/bin/env python3
"""Generic nested-RPF9 archive scanner for *_concat.rpf files.

Scans for the 9FPR magic, parses the 64-byte header, then extracts ASCII
string signatures from the data area (align16(64+toc_end)).  Payloads of
nested archives are plaintext and self-describing (verified 2026-11-28),
so signatures are used to map archives to missing logical paths.

Usage: python scan_concat.py <concat.rpf> <out.json>
"""
import json
import mmap
import os
import re
import struct
import sys

MAGIC = b'9FPR'
STR_RE = re.compile(rb'[A-Za-z][A-Za-z0-9_./]{4,}')


def parse_header(mm, off, file_size):
    h = mm[off:off + 64]
    if len(h) < 64 or h[:4] != MAGIC:
        return None
    magic, toc_end, f08, name_bs = struct.unpack_from('<4sIII', h, 0)
    toc_hash, = struct.unpack_from('>Q', h, 0x10)
    fcount, = struct.unpack_from('<I', h, 0x24)
    key_id, = struct.unpack_from('<I', h, 0x28)
    flags, = struct.unpack_from('<I', h, 0x2C)
    data_start = (64 + toc_end + 15) & ~15
    if off + data_start >= file_size:
        return None
    return dict(off=off, toc_end=toc_end, f08=f08, name_bs=name_bs,
                toc_hash='%016X' % toc_hash, fcount=fcount,
                key_id='%08X' % key_id, flags='%08X' % flags,
                data_start=data_start)


def main():
    path, out_path = sys.argv[1], sys.argv[2]
    f = open(path, 'rb')
    size = os.path.getsize(path)
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    # collect all magic offsets
    offsets = []
    pos = 0
    while True:
        j = mm.find(MAGIC, pos)
        if j < 0:
            break
        offsets.append(j)
        pos = j + 1
    print('magic count:', len(offsets), 'file:', path)
    archives = []
    for n, off in enumerate(offsets):
        t = parse_header(mm, off, size)
        if t is None:
            continue
        # size = next magic - this off, or file end
        end = offsets[n + 1] if n + 1 < len(offsets) else size
        t['size'] = end - off
        t['i'] = n
        # sample first 64KB of data area for strings
        s = off + t['data_start']
        sample = mm[s:min(end, s + 65536)]
        strs = [x.decode() for x in STR_RE.findall(sample)]
        uniq = []
        for x in strs:
            if x not in uniq:
                uniq.append(x)
        t['strings'] = uniq[:24]
        archives.append(t)
        if (n + 1) % 20 == 0:
            print('  parsed', n + 1)
    mm.close()
    f.close()
    json.dump(archives, open(out_path, 'w'), indent=1)
    print('total archives:', len(archives), '->', out_path)
    for t in archives:
        print('#%-3d off=%-12d sz=%-11d fc=%-6d key=%s : %s' % (
            t['i'], t['off'], t['size'], t['fcount'], t['key_id'],
            ','.join(t['strings'][:8])))


if __name__ == '__main__':
    main()
