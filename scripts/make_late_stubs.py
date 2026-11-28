import os
root = r'C:\GTAVI\PS5\games\GTA6-dump\GTAVIPS5'
man = [p.strip() for p in open(r'C:\GTAVI\PS5\logs\stub-manifest.txt') if p.strip()]
def norm(p):
    return os.path.normpath(p.lower()).replace('/', '\\')
keep = []
for p in man:
    np = norm(p)
    if np.startswith(norm(root + r'\data\levels')) or np.startswith(norm(root + r'\data\anim')):
        keep.append(p)
n = 0
for p in keep:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.isfile(p):
        open(p, 'wb').close()
        n += 1
with open(r'C:\GTAVI\PS5\logs\stub-manifest-late.txt', 'w') as f:
    f.write('\n'.join(keep))
print('late stubs kept:', n, 'of', len(man))
