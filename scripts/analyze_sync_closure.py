# -*- coding: utf-8 -*-
# 闭环校验：RELEASE_MEM 写回(label) 地址 vs WAIT_REG_MEM/WAIT_REG_MEM_64 轮询地址
import re, glob, collections, os

DUMP = r"C:\GTAVI\PS5\logs\cmdbuf-dump"
REL_ADDR = collections.Counter()   # release write addr -> count
REL_DATA = collections.Counter()   # (addr, data) pairs
WAIT_ADDR = collections.Counter()  # wait poll addr -> count
WAIT_REF = collections.Counter()   # (addr, ref) pairs
SEM_ADDR = collections.Counter()   # mem semaphore addr
n_files = 0

def parse_file(path):
    global n_files
    n_files += 1
    hdr = None
    payload = []
    def flush():
        if hdr is None:
            return
        op = (hdr >> 8) & 0xff
        if op == 0x49 and len(payload) >= 6:  # RELEASE_MEM
            addr = (payload[2] & ~0x3) | (payload[3] << 32)
            data = payload[4] | (payload[5] << 32)
            REL_ADDR[addr] += 1
            REL_DATA[(addr, data)] += 1
        elif op in (0x3c, 0x93) and len(payload) >= 5:  # WAIT_REG_MEM / _64
            if op == 0x3c and len(payload) >= 6:
                addr = (payload[2] & ~0x3) | ((payload[3] & 0x3ffff) << 32)
                ref = payload[4]
                WAIT_ADDR[addr] += 1
                WAIT_REF[(addr, ref)] += 1
            elif op == 0x93 and len(payload) >= 7:
                addr = (payload[2] & ~0x3) | ((payload[3] & 0x3ffff) << 32)
                ref = payload[4] | (payload[5] << 32)
                WAIT_ADDR[addr] += 1
                WAIT_REF[(addr, ref)] += 1
        elif op == 0x39 and len(payload) >= 3:  # MEM_SEMAPHORE
            addr = (payload[0] & ~0x7) | ((payload[1] & 0x3ffff) << 32)
            SEM_ADDR[addr] += 1
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.match(r"^\s*([0-9a-f]{5}) \| (0x[0-9a-fA-F]{8}) \|", line)
            if m:
                flush()
                hdr = int(m.group(2), 16)
                payload = []
            else:
                m2 = re.match(r"^\s*\| (0x[0-9a-fA-F]{8}) \|", line)
                if m2 and hdr is not None:
                    payload.append(int(m2.group(1), 16))
    flush()

for p in glob.glob(os.path.join(DUMP, "*.log")):
    parse_file(p)

print("files parsed:", n_files)
print("RELEASE_MEM distinct addrs:", len(REL_ADDR), "total:", sum(REL_ADDR.values()))
print("WAIT_REG_MEM distinct addrs:", len(WAIT_ADDR), "total:", sum(WAIT_ADDR.values()))
print("MEM_SEMAPHORE distinct addrs:", len(SEM_ADDR), "total:", sum(SEM_ADDR.values()))
inter = set(REL_ADDR) & set(WAIT_ADDR)
print("overlap release∩wait addrs:", len(inter))
inter_sem = set(REL_ADDR) & set(SEM_ADDR)
print("overlap release∩semaphore addrs:", len(inter_sem))
print("\n-- top RELEASE (addr, data) --")
for (a, d), c in REL_DATA.most_common(12):
    print(f"  0x{a:016x} data=0x{d:x}  x{c}")
print("\n-- top WAIT (addr, ref) --")
for (a, r), c in WAIT_REF.most_common(12):
    print(f"  0x{a:016x} ref=0x{r:x}  x{c}")
print("\n-- top SEM addr --")
for a, c in SEM_ADDR.most_common(8):
    print(f"  0x{a:016x}  x{c}")
if inter:
    print("\n-- overlap addrs sample --")
    for a in list(inter)[:10]:
        rels = [(dd, cc) for (aa, dd), cc in REL_DATA.items() if aa == a]
        wts = [(rr, cc) for (aa, rr), cc in WAIT_REF.items() if aa == a]
        print(f"  0x{a:016x}  release:{rels[:3]}  wait:{wts[:3]}")
