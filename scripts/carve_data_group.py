#!/usr/bin/env python3
"""Carve high-confidence nested archives out of data_concat.rpf (RPF9) and
place them at the real paths the game resolves (Ampr /app0 -> dump dir).

Mapping evidence = plaintext strings found in each archive's data area
(see docs/development-log.md 2026-11-28 14:10 entry and
logs/nested-archive-signatures.json).  Byte ranges are exact: nested
archive occupies [off, off+size) inside data_concat.rpf; the FULL archive
(header + encrypted TOC + payload) must be placed, because the game opens
the file as RPF9 and decrypts the TOC itself (payload-only carve = guest
fault in seconds, proven 2026-11-28 15:00 run).

Writes logs/carve-placed-manifest.txt (used for cleanup; iron rule: only
delete files listed in the manifest)."""
import json
import os

DUMP = r'C:\GTAVI\PS5\games\GTA6-dump\GTAVIPS5'
CONCAT = os.path.join(DUMP, 'data_concat.rpf')
HEADERS = r'C:\GTAVI\PS5\logs\seqmap-headers.json'
MANIFEST = r'C:\GTAVI\PS5\logs\carve-placed-manifest.txt'

# archive index -> relative path under dump root (evidence-backed only)
MAPPING = {
    25: 'data/data/legal.rpf',                                 # DE/EU legal text
    26: 'data/data/moviesubs.rpf',                             # CMovieSubtitleEventArg/TVPROMO
    27: 'data/data/control/common.rpf',                        # STANDARD_LAYOUT/PAD_* inputs
    12: 'data/data/lang/american_final.rpf',                   # English dictionary strings
    29: 'data/data/ui/scaleform/scaleform_decorations.rpf',    # decorations.square.Main_Svg
    30: 'data/data/ui/scaleform/scaleform_fontlib.rpf',        # gfxfontlib_* per language
    32: 'data/data/ui/scaleform/scaleform_loading_screens.rpf',# loading_screen_00_*
    33: 'data/data/ui/scaleform/scaleform_platform_ps5.rpf',   # platform_ps5.generic_movie/hud
    35: 'data/data/ui/scaleform/scaleform_vehicle_instruments.rpf', # analog/generic_instruments
    36: 'data/data/ui/ui_content.rpf',                         # launcher_menu/FlowRoot/State
    8:  'data/data/effects/ptfx/drawables.rpf',                # ptfx_model_* drawables
    34: 'data/textures/ui_minimap.rpf',                        # BLIP_*
    38: 'data/textures/skydome.rpf',                           # skydome.
    39: 'data/models/weapons.rpf',                             # w_ar_adb_01 weapon drawables
    5:  'data/data/camera/cam_core.rpf',                       # cam* settings, fc=181 (largest)
    3:  'data/data/camera/cam_generic.rpf',                    # cam* settings, fc=17
}


def main():
    nest = {t['i']: t for t in json.load(open(HEADERS))}
    placed = []
    with open(CONCAT, 'rb') as src, open(MANIFEST, 'w', encoding='utf-8') as mf:
        for idx, rel in sorted(MAPPING.items()):
            t = nest[idx]
            # FULL nested archive: [off, off+size) includes RPF9 header + TOC + payload
            length = t['size']
            dst = os.path.join(DUMP, rel.replace('/', os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            src.seek(t['off'])
            with open(dst, 'wb') as out:
                remaining = length
                while remaining:
                    chunk = src.read(min(1 << 20, remaining))
                    if not chunk:
                        break
                    out.write(chunk)
                    remaining -= len(chunk)
            placed.append(dst)
            mf.write(dst + '\t%d bytes\tarchive#%d\n' % (length, idx))
            print('placed', rel, length, 'bytes (full archive)')
    print('total placed:', len(placed))


if __name__ == '__main__':
    main()
