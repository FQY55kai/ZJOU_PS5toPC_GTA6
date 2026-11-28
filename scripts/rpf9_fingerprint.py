#!/usr/bin/env python3
"""RPF9 nested-archive fingerprint + payload content sniffing for name mapping.
Header layout per GTA6-Asset-Info (jaylikesbunda):
  0x00 magic, 0x04 toc_end, 0x0C name block size, 0x10 u64 unique value,
  0x24 file count, 0x28 key_id, 0x2C index variant.
Payload: plain zlib streams, 16-byte aligned, start after toc_end.
"""
import json, zlib, re, os

CONCAT = r"C:\GTAVI\PS5\games\GTA6-dump\GTAVIPS5\data_concat.rpf"
d = json.load(open(r"C:\GTAVI\PS5\logs\seqmap-result.json"))
offs = d["offsets"]

rows = []
with open(CONCAT, "rb") as f:
    for i, o in enumerate(offs):
        f.seek(o)
        h = f.read(0x40)
        if len(h) < 0x40:
            continue
        magic = int.from_bytes(h[0:4], "little")
        toc_end = int.from_bytes(h[4:8], "little")
        f08 = int.from_bytes(h[8:12], "little")
        name_bs = int.from_bytes(h[0x0C:0x10], "little")
        uniq = int.from_bytes(h[0x10:0x18], "little")
        const18 = int.from_bytes(h[0x18:0x1C], "little")
        const1C = int.from_bytes(h[0x1C:0x20], "little")
        fcount = int.from_bytes(h[0x24:0x28], "little")
        key_id = int.from_bytes(h[0x28:0x2C], "little")
        variant = int.from_bytes(h[0x2C:0x30], "little")
        end = offs[i + 1] if i + 1 < len(offs) else 1_554_000_000
        rows.append(dict(i=i, off=o, size=end - o, toc_end=toc_end, f08=f08,
                         name_bs=name_bs, uniq=f"{uniq:016X}", fcount=fcount,
                         key_id=f"{key_id:08X}", variant=f"{variant:08X}",
                         c18=const18, c1c=const1c if False else const1C))
print(f"{'#':>3} {'offset':>12} {'size':>12} {'toc_end':>8} {'fcount':>7} {'key_id':>9} {'variant':>9} {'name_bs':>7} {'uniq':>17}")
for r in rows:
    print(f"{r['i']:>3} {r['off']:>12,} {r['size']:>12,} {r['toc_end']:>8} {r['fcount']:>7} {r['key_id']:>9} {r['variant']:>9} {r['name_bs']:>7} {r['uniq']:>17}")

json.dump(rows, open(r"C:\GTAVI\PS5\logs\seqmap-headers.json", "w"), indent=1)

# ---- content sniffing: decompress first zlib streams of each archive ----
def sniff(f, off, toc_end, nbytes=96):
    f.seek(off + toc_end)
    window = f.read(1 << 20)
    out = []
    pos = 0
    tried = 0
    while pos < len(window) - 2 and tried < 6:
        if window[pos] == 0x78:
            try:
                dec = zlib.decompressobj()
                data = dec.decompress(window[pos:], 4096)
                if len(data) > 8:
                    out.append((off + toc_end + pos, data[:nbytes]))
                    tried += 1
            except Exception:
                pass
        pos += 16  # 16-aligned
    return out

sig_text = re.compile(rb"[\x20-\x7e]{6,}")
print("\n== payload sniff (first zlib streams) ==")
with open(CONCAT, "rb") as f:
    for r in rows[3:]:
        if r["size"] > 100_000_000:
            continue
        hits = sniff(f, r["off"], r["toc_end"])
        if not hits:
            print(f"#{r['i']:02d} off={r['off']:,} NO-STREAM (toc_end={r['toc_end']})")
            continue
        pos0, data0 = hits[0]
        texts = sig_text.findall(data0[:96])
        preview = b" | ".join(texts[:3]).decode(errors="replace")[:120]
        print(f"#{r['i']:02d} off={r['off']:,} fcount={r['fcount']:>6} stream0@+{pos0-off:x} head={data0[:8].hex()} text='{preview}'")
