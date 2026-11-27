# -*- coding: utf-8 -*-
"""PS5 finalized-image (.pkg, \\x7fFIH) parser - LibProsperoPKG layout.

FIH header (little-endian):
  0x00 magic "\\x7fFIH"
  0x05 signed byte: 0x00 = debug FPKG, 0x80 = retail
  0x10 PFS image offset (normally 0x10000)
  0x18 PFS image size
  0x58 embedded CNT metadata offset
  0xA0 embedded CNT metadata size
Then a 0x10000-byte digest table.

CNT container (big-endian header):
  0x00 magic "\\x7fCNT"
  entry count / entry-table offset / content-id (36 chars) / DRM type
Entry table: 0x20-byte records per file entry.
"""
import hashlib
import json
import struct
import sys

PKG = r"C:\GTAVI\PS5\games\Grand Theft Auto VI [PPSA38500] [v01.002].pkg"
OUT = r"C:\GTAVI\PS5\analysis\fih_analysis.json"

f = open(PKG, "rb")

def read(off, n):
    f.seek(off)
    return f.read(n)

# ---- FIH header ----
hdr = read(0, 0x100)
magic = hdr[0x00:0x04]
signed = hdr[0x05]
pfs_off = struct.unpack_from("<Q", hdr, 0x10)[0]
pfs_size = struct.unpack_from("<Q", hdr, 0x18)[0]
cnt_off = struct.unpack_from("<Q", hdr, 0x58)[0]
cnt_size = struct.unpack_from("<Q", hdr, 0xA0)[0]
print("magic          :", magic)
print("signed byte    : 0x%02x -> %s" % (signed, "RETAIL" if signed == 0x80 else "DEBUG" if signed == 0x00 else "UNKNOWN"))
print("PFS offset     : 0x%x" % pfs_off)
print("PFS size       : 0x%x (%.2f GiB)" % (pfs_size, pfs_size / 2**30))
print("CNT offset     : 0x%x" % cnt_off)
print("CNT size       : 0x%x" % cnt_size)

# ---- sanity: PFS magic at pfs_off ----
pfs_head = read(pfs_off, 0x40)
print("PFS first bytes:", pfs_head[:16].hex())

# ---- find \\x7fCNT magic if declared offset wrong ----
cnt_magic_ok = False
if cnt_off and cnt_size:
    c = read(cnt_off, 4)
    cnt_magic_ok = (c == b"\x7fCNT")
    print("CNT magic at declared offset:", c, "OK" if cnt_magic_ok else "MISMATCH")
if not cnt_magic_ok:
    # scan first 2 MiB in 0x10-aligned steps
    scan = read(0, 2 * 1024 * 1024)
    idx = scan.find(b"\x7fCNT")
    print("CNT magic scan result: 0x%x" % idx if idx >= 0 else "CNT magic not found in first 2MiB")
    if idx >= 0:
        cnt_off = idx
        cnt_magic_ok = True

# ---- CNT container (big-endian) ----
info = {"fih": {}, "cnt": None, "entries": []}
info["fih"] = {
    "magic": magic.decode("latin1"),
    "signed": signed,
    "type": "retail" if signed == 0x80 else "debug",
    "pfs_offset": pfs_off,
    "pfs_size": pfs_size,
    "cnt_offset": cnt_off,
    "cnt_size": cnt_size,
    "sha256_first_1mib": hashlib.sha256(read(0, 1024 * 1024)).hexdigest(),
}

if cnt_magic_ok:
    ch = read(cnt_off, 0x100)
    # big-endian guesses; print raw words to interpret
    words = struct.unpack_from(">8I", ch, 4)
    print("CNT header BE words[4:36]:", [hex(w) for w in words[:8]])
    # common layout: 0x04 entry_count, 0x08 entry_table_offset(rel), 0x0C entry_table_size, 0x10 content_id..
    entry_count = words[0]
    et_off = words[1]
    et_size = words[2]
    content_id = ch[0x10:0x34].decode("latin1", "replace").strip("\x00 ")
    drm = struct.unpack_from(">I", ch, 0x34)[0]
    print("entry_count    :", entry_count)
    print("entry_table off: 0x%x (rel to CNT)" % et_off)
    print("entry_table sz : 0x%x" % et_size)
    print("content_id     :", content_id)
    print("drm_type       : 0x%x" % drm)
    info["cnt"] = {
        "entry_count": entry_count, "entry_table_offset": et_off,
        "entry_table_size": et_size, "content_id": content_id, "drm_type": drm,
    }
    # ---- walk entry table (0x20 bytes each), flags bit 0x80000000 = encrypted ----
    et_abs = cnt_off + et_off
    for i in range(min(entry_count, 4096)):
        rec = read(et_abs + i * 0x20, 0x20)
        if len(rec) < 0x20:
            break
        f1, f2, f3, f4, off, size = struct.unpack_from(">IIIIQQ", rec, 0)
        enc = bool(f1 & 0x80000000)
        name = rec[0x20 - 0x20:]
        # name lives in a separate string table in real PKG; record raw words
        info["entries"].append({"flags1": "0x%08x" % f1, "offset": off, "size": size, "encrypted": enc})
    print("entries walked :", len(info["entries"]))
    enc_count = sum(1 for e in info["entries"] if e["encrypted"])
    print("encrypted entries:", enc_count, "/", len(info["entries"]))

with open(OUT, "w") as o:
    json.dump(info, o, indent=2)
print("saved ->", OUT)
