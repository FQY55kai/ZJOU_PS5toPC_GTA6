#!/usr/bin/env python3
"""Launch the scarlett-fox Victory (Xbox->PC) compatibility layer with the
exact env profile from _Start-GTA6.cmd, profile=12 (RTX 4080 Laptop 12GB).

Runs: victory.exe run <game_dir>\game_scarlett_master.exe --execute --console series-s
Stdout/stderr -> log file.  Does NOT touch any game/cache files.
"""
import os
import subprocess
import sys

ROOT = r'C:\GTAVI\Bulid_now\scarlett-fox-\u901a\u7528-2611272152'
ROOT = r'C:\GTAVI\Bulid_now\scarlett-fox-通用-2611272152'
EXE = os.path.join(ROOT, 'victory.exe')
GAME = r'C:\GTAVI\GTA6.Xbox.v1.0.2.1\game_scarlett_master.exe'
LOCAL = os.environ.get('LOCALAPPDATA', r'C:\Users\MACHENIKE\AppData\Local')
LOG = r'C:\Users\MACHENIKE\WorkBuddy\automation-2026-11-28-02-21-05\victory-play.log'

env = os.environ.copy()
env.update({
    'VICTORY_GAME_DIR': r'C:\GTAVI\GTA6.Xbox.v1.0.2.1',
    'VICTORY_CACHE_DIR': os.path.join(LOCAL, 'victory-scarlett-fox'),
    'VICTORY_DATA_DIR': os.path.join(LOCAL, 'victory-scarlett-data'),
    'VICTORY_PROFILE': '12',
    # picture fixes
    'VICTORY_PROBE_RAYS': '1', 'VICTORY_PLANE_NOW': '1',
    # crash prevention
    'VICTORY_TEXTURE_MIP_DROP': '1', 'VICTORY_FRAME_INTERVAL_MS': '33.3',
    'VICTORY_CARD_BUFFERS_MIN_KB': '64', 'VICTORY_PIPELINE_BOOK': '1',
    'VICTORY_LOG': 'info', 'VICTORY_MAX_PRELUDES': '32',
    'VICTORY_LEVELS_ON_DEMAND': '0', 'VICTORY_WAIT_RESIDENT': '0',
    'VICTORY_REFRESH_ONCE': '1', 'VICTORY_CARD_REHASH_RUNS': '1',
    'VICTORY_WIDE_MERGE': '1', 'VICTORY_MIRROR_FAST': '1',
    'VICTORY_PIPELINE_WAIT_MS': '20', 'VICTORY_ASYNC_SUBMIT': '1',
    'VICTORY_INDIRECT_WINDOW': '1', 'VICTORY_TEXTURE_NO_WAIT': '1',
    'VICTORY_COPY_PLAIN': '1', 'VICTORY_WIDE_TEXTURES': '1',
    'VICTORY_INDIRECT_GATHER': '1', 'VICTORY_LATE_WAIT_LISTS': '1024',
    'VICTORY_CARD_FILLS_BATCH': '0', 'VICTORY_GATHER_DISPATCH': '0',
    'VICTORY_RELAY': '2', 'VICTORY_WIDE_BACK': '1',
    'VICTORY_RELAY_COPY': '1', 'VICTORY_CARD_STEPS': '2',
    'VICTORY_INDIRECT_BATCH': '2', 'VICTORY_MAP_THREADS': '1',
    'VICTORY_CARD_AWAKE': '0', 'VICTORY_SHOW_AFTER': '1',
    'VICTORY_JOIN_PARTS': '8', 'VICTORY_UPLOAD_AHEAD': '1',
    'VICTORY_POOL_DISCARD': '1', 'VICTORY_FILL_TITLE': '1',
    'VICTORY_PARTIAL_DELTA': '1', 'VICTORY_BAKE_DELTA': '1',
    'VICTORY_MAP_LOCK_FINE': '1', 'VICTORY_POOL_CAP': '1',
    'VICTORY_TABLE_MEMO': '1', 'VICTORY_LIST_ALIAS_EXACT': '1',
    'VICTORY_LIST_HOLD': '1', 'VICTORY_EARLY_TEXTURES_MS': '40',
    'VICTORY_BAKE_TEXTURES_MS': '10000', 'VICTORY_HEAP_PASS_MAX': '0',
    'VICTORY_HEAP_CHANGED_MAX': '0',
    'VICTORY_LEAVE_OUT': '02384a60fda6f2d0',
    'VICTORY_WC_NO_BACK': '1', 'VICTORY_WC_NO_BACK_MIN_KB': '1024',
    'VICTORY_SYNC_IN_PLACE': '1', 'VICTORY_SPANS_QUICK': '1',
    'VICTORY_SYNC_FINE': '1', 'VICTORY_HEAP_SYNC_FIRST': '1',
    'VICTORY_HEAP_SYNC_AT_SUBMIT': '1',
    'VICTORY_SOFT_VIEWS': 'copies', 'VICTORY_SAMPLERS_MADE': '1',
    'VICTORY_TABLE_NAMED_ONLY': '1', 'VICTORY_QUEUE_MARKS': '1',
    'VICTORY_PORT_CONSTANTS': '1', 'VICTORY_EARLY_DEPTH': '1',
    'VICTORY_AMBIENT': '0.8', 'VICTORY_AMBIENT_AIR': '1.5',
    # profile=12 budget
    'VICTORY_TEXTURE_BUDGET_MB': '8192',
    'VICTORY_TEXTURE_ROOM_PERCENT': '90',
    'VICTORY_CARD_BUFFERS_MB': '1024',
    'VICTORY_CARD_WINDOWS_MB': '512',
    'VICTORY_DYNAMIC_SLOTS': '524288',
})

cmd = [EXE, 'run', GAME, '--execute', '--console', 'series-s']
print('launching:', cmd, flush=True)
with open(LOG, 'w', encoding='utf-8', errors='replace') as fh:
    proc = subprocess.Popen(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT,
                            cwd=ROOT)
print('pid', proc.pid, 'log', LOG, flush=True)
sys.exit(proc.wait())
