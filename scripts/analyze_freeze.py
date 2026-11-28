#!/usr/bin/env python3
"""One-pass scan of a kyty fliptrace log to discriminate FlipQueue-freeze hypotheses.

Signatures:
  ① CompleteFlip stall : requests stay Reserved -> Flip() early-returns at line 1101
  ② due=false          : generation mismatch / IsFlipDueLocked false
  ③ master/slave        : SetFlipMaster mid-run -> main port group=0, no owner (line 1094)

We detect: Open/Close churn, SetFlipMaster, last "Flip done", CpFlip after last present,
flipPendingNum trend, vblank activity.
"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else r"C:\GTAVI\PS5\logs\auto-fliptrace-20261128-085943.log"

pat_flipdone = re.compile(r"Flip done:")
pat_cpflip = re.compile(r"CommandProcessor::Flip\(\)")
pat_setflipmaster = re.compile(r"SetFlipMaster|VideoOutSetFlipMaster|SetFlipMaster\(", re.I)
pat_open = re.compile(r"VideoOutOpen|VideoOut::Open", re.I)
pat_close = re.compile(r"VideoOutClose|VideoOut::Close", re.I)
pat_pending = re.compile(r"flipPendingNum\s*=\s*(\d+)")
pat_vblank = re.compile(r"VblankBegin|vblank", re.I)

counts = {
    "flipdone": 0, "cpflip": 0, "setflipmaster": 0, "open": 0, "close": 0, "vblank": 0,
}
first = {}
last = {}
first_pending = None
last_pending = None
pending_samples = []  # (lineno, value)
last_flipdone_line = None
last_cpflip_before_freeze = None

# We'll record first line where each SetFlipMaster/Open/Close appears (capped)
sfm_lines = []
open_lines = []
close_lines = []

with open(path, "r", encoding="utf-8", errors="replace") as f:
    for lineno, line in enumerate(f, 1):
        if pat_flipdone.search(line):
            counts["flipdone"] += 1
            last["flipdone"] = lineno
            if "flipdone" not in first:
                first["flipdone"] = lineno
        if pat_cpflip.search(line):
            counts["cpflip"] += 1
            last["cpflip"] = lineno
            if "cpflip" not in first:
                first["cpflip"] = lineno
        if pat_setflipmaster.search(line):
            counts["setflipmaster"] += 1
            if len(sfm_lines) < 50:
                sfm_lines.append((lineno, line.rstrip()[:200]))
        if pat_open.search(line):
            counts["open"] += 1
            if len(open_lines) < 50:
                open_lines.append((lineno, line.rstrip()[:200]))
        if pat_close.search(line):
            counts["close"] += 1
            if len(close_lines) < 50:
                close_lines.append((lineno, line.rstrip()[:200]))
        m = pat_pending.search(line)
        if m:
            val = int(m.group(1))
            if first_pending is None:
                first_pending = (lineno, val)
            last_pending = (lineno, val)
            if len(pending_samples) < 40 or (lineno % 500000 == 0):
                pending_samples.append((lineno, val))
        if pat_vblank.search(line):
            counts["vblank"] += 1

print("=== COUNTS ===")
for k, v in counts.items():
    print(f"{k}: {v}")
print("\n=== FIRST/LAST ===")
for k in ("flipdone", "cpflip"):
    print(f"{k}: first={first.get(k)} last={last.get(k)}")
print(f"\nflipPendingNum: first={first_pending} last={last_pending}")
print(f"\nLast 'Flip done' line: {last.get('flipdone')}")
print(f"Last 'CommandProcessor::Flip()' line: {last.get('cpflip')}")
print(f"CpFlip AFTER last Flip done: {counts['cpflip']} presents, {last.get('cpflip')} last cpflip")

print("\n=== SetFlipMaster lines (max 50) ===")
for ln, t in sfm_lines:
    print(f"L{ln}: {t}")
print("\n=== VideoOutOpen lines (max 50) ===")
for ln, t in open_lines:
    print(f"L{ln}: {t}")
print("\n=== VideoOutClose lines (max 50) ===")
for ln, t in close_lines:
    print(f"L{ln}: {t}")

print("\n=== flipPendingNum samples (max 40) ===")
for ln, v in pending_samples[:40]:
    print(f"L{ln}: {v}")
print("... last: ")
for ln, v in pending_samples[-10:]:
    print(f"L{ln}: {v}")
