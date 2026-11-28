#!/usr/bin/env python3
"""Batch carve round 2: textures group + fxlists + scaleform_general + models.

Same principle as carve_data_group.py (fixed): place the FULL nested RPF9
archive [off, off+size) at the resolved real path -- the game decrypts the
TOC itself.  Payload-only placement = instant guest fault (proven).

Evidence table (string signatures, see docs/development-log.md):
  textures_concat.rpf nested idx -> path (18 of 20; #6/#9 held back):
    0  glass_crack_decals/defnormbroken      -> breakableglass.rpf
    1  cheatcode_overlays_tv/fisheye/rewind  -> footagepostfx.rpf
    2  blank_white/blank_terrain_ma          -> global_defaults.rpf
    3  gradientmaps                          -> gradientmappostfx.rpf
    4  cloudmap_*/emissives/lightocclusion   -> graphics.rpf
    5  heightmap                            -> heightmaps.rpf
    7  colorblind LUT debug + transitions    -> lutpostfx_hdr.rpf
    8  rope_anim_wave/rope_deg_*             -> rope_light_anim.rpf
    10 snow_coverage/snowdiffusemap          -> snow.rpf
    11 blip_* map icons (1199 names)         -> ui/ui_hud.rpf
    12 filter_exploration_*/filter_activities -> ui/ui_pausemenu.rpf
    13 background_legal/menu_item_zh-*       -> ui/ui_startup_textures.rpf
    14 area_rect/area_oval                   -> level_design.rpf
    15 vehicle_crumple_n                     -> vehicle_common.rpf
    16 lightning_*/curlnoise/windnoisevolume -> vfx_misc.rpf
    17 shore_wave/waterfoam/ocean_sim        -> water.rpf
    18 waterfogatlas_gfb/gfb2 (fc=1315)      -> waterfogatlas/waterfogatlas.rpf
    19 skydustpollution/pressure/onoffshorewind -> weathermaps.rpf
  data_concat.rpf:
    10 ent_anm_*/anm_blood_* (2626 names)    -> data/effects/ptfx/fxlists.rpf
    31 controller_test_*/phone_*/drone_overlay -> ui/scaleform/scaleform_general.rpf
  data.rpf nested @0x40000 (vehicle parts, props, INPUT_*):
                                               -> data/models/models.rpf

Writes logs/carve2-placed-manifest.txt (iron rule: cleanup only deletes
files listed in the manifest).
"""
import json
import os
import struct

DUMP = r'C:\GTAVI\PS5\games\GTA6-dump\GTAVIPS5'
LOGS = r'C:\GTAVI\PS5\logs'
MANIFEST = os.path.join(LOGS, 'carve2-placed-manifest.txt')

TEXTURES = {
    0:  'data/textures/breakableglass.rpf',
    1:  'data/textures/footagepostfx.rpf',
    2:  'data/textures/global_defaults.rpf',
    3:  'data/textures/gradientmappostfx.rpf',
    4:  'data/textures/graphics.rpf',
    5:  'data/textures/heightmaps.rpf',
    7:  'data/textures/lutpostfx_hdr.rpf',
    8:  'data/textures/rope_light_anim.rpf',
    10: 'data/textures/snow.rpf',
    11: 'data/textures/ui/ui_hud.rpf',
    12: 'data/textures/ui/ui_pausemenu.rpf',
    13: 'data/textures/ui/ui_startup_textures.rpf',
    14: 'data/textures/level_design.rpf',
    15: 'data/textures/vehicle_common.rpf',
    16: 'data/textures/vfx_misc.rpf',
    17: 'data/textures/water.rpf',
    18: 'data/textures/waterfogatlas/waterfogatlas.rpf',
    19: 'data/textures/weathermaps.rpf',
}
DATAC = {
    10: 'data/data/effects/ptfx/fxlists.rpf',
    31: 'data/data/ui/scaleform/scaleform_general.rpf',
}


def place(src_f, off, length, rel, mf):
    dst = os.path.join(DUMP, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    src_f.seek(off)
    with open(dst, 'wb') as out:
        remaining = length
        while remaining:
            chunk = src_f.read(min(1 << 20, remaining))
            if not chunk:
                raise IOError('short read at %x' % off)
            out.write(chunk)
            remaining -= len(chunk)
    # verify magic
    with open(dst, 'rb') as f:
        magic = f.read(4)
    assert magic == b'9FPR', 'bad magic %r for %s' % (magic, rel)
    mf.write(dst + '\t%d bytes\n' % length)
    print('placed', rel, length, 'bytes')


def main():
    other = json.load(open(os.path.join(LOGS, 'other-concat-nested.json')))
    nest_c = {t['i']: t for t in json.load(open(os.path.join(LOGS, 'seqmap-headers.json')))}
    with open(MANIFEST, 'w', encoding='utf-8') as mf:
        # textures_concat
        entries = other['textures_concat.rpf']
        with open(os.path.join(DUMP, 'textures_concat.rpf'), 'rb') as src:
            for idx, rel in sorted(TEXTURES.items()):
                e = entries[idx]
                place(src, e['off'], e['size'], rel, mf)
        # data_concat
        with open(os.path.join(DUMP, 'data_concat.rpf'), 'rb') as src:
            for idx, rel in sorted(DATAC.items()):
                t = nest_c[idx]
                place(src, t['off'], t['size'], rel, mf)
        # data.rpf nested archive
        with open(os.path.join(DUMP, 'data.rpf'), 'rb') as src:
            place(src, 0x40000, 121452592, 'data/models/models.rpf', mf)
    print('done; manifest:', MANIFEST)


if __name__ == '__main__':
    main()
