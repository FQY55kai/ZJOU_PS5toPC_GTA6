import os
root = r'C:/GTAVI/PS5/games/GTA6-dump/GTAVIPS5'
manifest = []
n = 0
for line in open(r'C:/GTAVI/PS5/logs/auto-scene-20261128-100030.log', encoding='utf-8', errors='replace'):
    if 'APR resolve missing path' not in line:
        continue
    host = line.split(' -> ', 1)[1].strip()
    # normalize: game side uses ./ and mixed slashes
    host = host.replace('\\./', '\\').replace('/./', '/')
    host = host.replace('\\/', '\\')
    p = host.replace('/', '\\')
    p = os.path.normpath(p)
    if not os.path.normpath(p.lower()).startswith(os.path.normpath(root.lower())):
        continue
    if os.path.isfile(p):
        continue
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').close()
    manifest.append(p)
    n += 1
open(r'C:/GTAVI/PS5/logs/stub-manifest.txt', 'w').write('\n'.join(manifest))
print('created stubs:', n)
