#!/usr/bin/env python3
"""Sequence-mapping hypothesis test:
resolve-log order of missing paths <-> nested RPF header offsets in *_concat.rpf.
Hypothesis: game resolves members in TOC order, which matches physical order in concat.
"""
import re, sys, json, os

LOG = r"C:\GTAVI\PS5\logs\auto-scene-20261128-100030.log"
CONCAT = r"C:\GTAVI\PS5\games\GTA6-dump\GTAVIPS5\data\data_concat.rpf"
OUT = r"C:\GTAVI\PS5\logs\seqmap-result.json"

MAGIC = b"9FPR"  # LE bytes of 0x52504F39 ... actually magic word stored LE

# 1. ordered missing paths from log
pat = re.compile(r"APR resolve missing path[^\"]*\"([^\"]+)\"")
pat2 = re.compile(r"APR resolve missing path.*?(/app0/\S+)")
ordered = []
seen = set()
with open(LOG, "r", errors="replace") as f:
    for line in f:
        if "APR resolve missing path" not in line:
            continue
        m = pat2.search(line)
        if not m:
            m = pat.search(line)
            if not m:
                continue
        p = m.group(1)
        if p not in seen:
            seen.add(p)
            ordered.append((p, sum(1 for _ in ()) if False else None))
# keep only first-appearance order; record line numbers too
ordered = []
seen = set()
with open(LOG, "r", errors="replace") as f:
    for i, line in enumerate(f, 1):
        if "APR resolve missing path" not in line:
            continue
        m = pat2.search(line) or pat.search(line)
        if not m:
            continue
        p = m.group(1)
        if p not in seen:
            seen.add(p)
            ordered.append((i, p))

print(f"unique missing paths (first-appearance order): {len(ordered)}")
for ln, p in ordered[:30]:
    print(f"  L{ln}: {p}")

# 2. group by top dir
from collections import Counter, defaultdict
groups = defaultdict(list)
for ln, p in ordered:
    m = re.match(r"/app0/\.?/?data/([^/]+)/", p)
    key = m.group(1) if m else (p.replace("/app0/", "")[:20])
    groups[key].append((ln, p))
print("\ngroups:", {k: len(v) for k, v in sorted(groups.items(), key=lambda x: -len(x[1]))[:15]})

# 3. scan data_concat.rpf for nested magic offsets
offs = []
with open(CONCAT, "rb") as f:
    CHUNK = 1 << 24
    pos = 0
    prev_tail = b""
    while True:
        buf = f.read(CHUNK)
        if not buf:
            break
        data = prev_tail + buf
        base = pos - len(prev_tail)
        start = 0
        while True:
            i = data.find(MAGIC, start)
            if i < 0:
                break
            offs.append(base + i)
            start = i + 1
        prev_tail = buf[-4:]
        pos += len(buf)
print(f"\nmagic hits in data_concat.rpf: {len(offs)}")
print("first 45 offsets:", offs[:45])

# 4. read nested header info (entry count etc.) at each offset
# RPF7/9 header: magic(4) entryCount(4) namesLen(4) flags(4) + key material 32B
info = []
with open(CONCAT, "rb") as f:
    for o in offs:
        f.seek(o)
        hdr = f.read(40)
        if len(hdr) < 16:
            continue
        magic = hdr[:4]
        entry_count = int.from_bytes(hdr[4:8], "little")
        names_len = int.from_bytes(hdr[8:12], "little")
        flags = int.from_bytes(hdr[12:16], "little")
        info.append({"off": o, "entry_count": entry_count, "names_len": names_len, "flags": flags})
for e in info[:45]:
    print(e)

json.dump({"ordered": [{"line": ln, "path": p} for ln, p in ordered],
           "offsets": offs, "headers": info},
          open(OUT, "w"), indent=1)
print(f"\nwritten {OUT}")
