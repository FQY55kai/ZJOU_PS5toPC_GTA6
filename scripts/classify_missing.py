import re, collections
log = r'C:\GTAVI\PS5\logs\auto-scene-20261128-100030.log'
pat = re.compile(r'APR resolve missing path: (\S+) -> (\S+)')
pairs = []
with open(log, 'r', errors='replace') as f:
    for line in f:
        m = pat.search(line)
        if m:
            pairs.append((m.group(1), m.group(2).strip()))
print("total missing:", len(pairs))
root = 'C:/GTAVI/PS5/games/GTA6-dump/GTAVIPS5'
BS = chr(92)
c = collections.Counter()
samples = {}
for src, tgt in pairs:
    t = tgt
    if t.startswith(root):
        t = t[len(root):]
    t = t.lstrip('/').lstrip(BS)
    if t.startswith('./'):
        t = t[2:]
    parts = t.replace(BS, '/').split('/')
    key = '/'.join(parts[:3])
    c[key] += 1
    samples.setdefault(key, t)
for k, v in c.most_common(25):
    print(f"  {v:5d}  {k}   e.g. {samples[k]}")
print("\nfirst 8 src paths:")
for s, t in pairs[:8]:
    print("  ", s)
print("\nlevels samples:")
n = 0
for s, t in pairs:
    if 'levels' in s:
        print("  ", s)
        n += 1
        if n >= 5:
            break
print("\nanim samples:")
n = 0
for s, t in pairs:
    if '/anim/' in s:
        print("  ", s)
        n += 1
        if n >= 5:
            break
