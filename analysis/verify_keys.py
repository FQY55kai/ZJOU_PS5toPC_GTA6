# -*- coding: utf-8 -*-
"""PS5 debug FPKG outer-PFS unlock verification (LibProsperoPKG algorithm).

Chain:
  EKPFS   = SHA3_256( SHA3_256(u64be(1)) || SHA3_256(content_id padded to 48 w/ NUL) || passcode )
  encKey  = HMAC_SHA256(key=HMAC_SHA256(ekpfs, seed), msg=seed || u64be(1))
  tweakKey, dataKey = encKey[:16], encKey[16:32]
  XTS sectors of 0x1000; sectors < block_size/0x1000 (16) stay plaintext.
"""
import hashlib
import hmac
import struct
import sys

PKG = r"C:\GTAVI\PS5\games\Grand Theft Auto VI [PPSA38500] [v01.002].pkg"
PFS_OFF = 0x10000
CONTENT_ID = "EP1004-PPSA38500_00-GRANDTHEFTAUTO00"
PASSCODE = "0" * 32

f = open(PKG, "rb")

def read(off, n):
    f.seek(off)
    return f.read(n)

# ---------- 1. locate outer superblock ----------
# superblock: version=2 (i64 LE), magic=20130315 (i64 LE) right after
sig2 = struct.pack("<QQ", 2, 20130315)
head = read(PFS_OFF, 0x20000)
pos = head.find(sig2)
print("superblock signature at image offset: 0x%x" % pos if pos >= 0 else "NOT FOUND in first 128KiB")
if pos < 0:
    # maybe at block 1
    head = read(PFS_OFF + 0x10000, 0x20000)
    pos = head.find(sig2)
    print("second scan:", "0x%x" % (pos + 0x10000) if pos >= 0 else "NOT FOUND")
    pos += 0x10000 if pos >= 0 else 0

sb_off = PFS_OFF + pos
sb = read(sb_off, 0x380)
version, magic, pid = struct.unpack_from("<QQQ", sb, 0)
mode, unk1, block_size, nbackup = struct.unpack_from("<HHII", sb, 0x1C)
nblock, dinode_count, ndblock, dinode_block_count = struct.unpack_from("<QQQQ", sb, 0x28)
seed = sb[0x370:0x380]
print("version=%d magic=%d id=%d" % (version, magic, pid))
print("mode=0x%04x block_size=0x%x nblock=%d ndblock=%d dinode_count=%d dinode_block_count=%d"
      % (mode, block_size, nblock, ndblock, dinode_count, dinode_block_count))
print("seed:", seed.hex())
# mode bits: 0x1 signed, 0x2 64bit, 0x4 encrypted, 0x8 always
print("signed=%d is64=%d encrypted=%d" % (mode & 1, (mode >> 1) & 1, (mode >> 2) & 1))

# ---------- 2. derive keys ----------
def sha3(b):
    return hashlib.sha3_256(b).digest()

def compute_keys(content_id, passcode, index):
    data = bytearray(96)
    data[0:32] = sha3(struct.pack(">I", index))
    data[32:64] = sha3(content_id.encode().ljust(48, b"\x00"))
    data[64:96] = passcode.encode()
    return sha3(bytes(data))

def pfs_gen_crypto_key(ekpfs, seed, index):
    return hmac.new(ekpfs, struct.pack("<I", index) + seed, hashlib.sha256).digest()

ekpfs = compute_keys(CONTENT_ID, PASSCODE, 1)
print("EKPFS (sha3):", ekpfs.hex())
inner = hmac.new(ekpfs, seed, hashlib.sha256).digest()
enc_key = pfs_gen_crypto_key(inner, seed, 1)
tweak_key, data_key = enc_key[:16], enc_key[16:32]
print("tweakKey:", tweak_key.hex(), " dataKey:", data_key.hex())

# also SHA-256 candidates
def sha256(b):
    return hashlib.sha256(b).digest()
def compute_keys_sha256(content_id, passcode, index):
    data = bytearray(96)
    data[0:32] = sha256(struct.pack(">I", index))
    data[32:64] = sha256(content_id.encode().ljust(48, b"\x00"))
    data[64:96] = passcode.encode()
    return sha256(bytes(data))
ekpfs_s256 = compute_keys_sha256(CONTENT_ID, PASSCODE, 1)

# ---------- 3. XTS decrypt via OpenSSL ----------
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openssl_xts import xts_decrypt, tweak_block

def try_keys(ekpfs_val, label):
    inner_k = hmac.new(ekpfs_val, seed, hashlib.sha256).digest()
    ek = pfs_gen_crypto_key(inner_k, seed, 1)
    tk, dk = ek[:16], ek[16:32]
    ct = read(sb_off + 16 * 0x1000, 0x1000)
    pt = xts_decrypt(dk + tk, tweak_block(16), ct)
    printable = sum(1 for c in pt if 32 <= c < 127 or c in (9, 10, 13))
    print("[%s] sector16 first 32B: %s  printable%%=%.1f" % (label, pt[:32].hex(), 100 * printable / len(pt)))
    return pt

pt3 = try_keys(ekpfs, "sha3 ")
pt2 = try_keys(ekpfs_s256, "sha256")
