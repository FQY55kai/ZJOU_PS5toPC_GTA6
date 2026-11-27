@echo off
rem ============================================================
rem GTA VI (Xbox branch victory-scarlett-3070 "scarlett-fox")
rem One-click launch for RTX 4080 Laptop 12GB - run5 verified combo
rem Build first: cargo build --release --bin victory --locked
rem First time only: run shaders+warm prewarm (see docs/scarlett-fox-4080-config.md)
rem ============================================================
setlocal

rem ---- adjust these two paths to your machine ----
set VICTORY_GAME_DIR=C:\GTAVI\GTA6.Xbox.v1.0.2.1
set VICTORY_EXE=C:\GTAVI\scarlett-fox-src\victory-scarlett-3070-scarlett-fox\target\release\victory.exe

rem ---- crash prevention (DO NOT change, see docs section 3.1) ----
set VICTORY_TEXTURE_MIP_DROP=1
set VICTORY_TEXTURE_BUDGET_MB=6144
set VICTORY_TEXTURE_ROOM_PERCENT=80

rem ---- frame rate: 30fps tier ----
set VICTORY_FRAME_INTERVAL_MS=33.3

rem ---- buffers: keep 1024, 512 caused 4-6fps stall (docs section 3.3) ----
set VICTORY_CARD_BUFFERS_MB=1024
set VICTORY_CARD_WINDOWS_MB=512
set VICTORY_CARD_BUFFERS_MIN_KB=64

rem ---- fork 3070 play script baseline ----
set VICTORY_PIPELINE_BOOK=1
set VICTORY_LOG=info
set VICTORY_DYNAMIC_SLOTS=524288
set VICTORY_MAX_PRELUDES=32
set VICTORY_PAGE_POOL=1
set VICTORY_STAGING_PACK=1
set VICTORY_LEVELS_ON_DEMAND=0
set VICTORY_WAIT_RESIDENT=0
set VICTORY_JOIN_COPIES=0
set VICTORY_REFRESH_ONCE=1
set VICTORY_CARD_REHASH_RUNS=1
set VICTORY_BACK_OWN_VIEW=1
set VICTORY_WIDE_MERGE=1
set VICTORY_MIRROR_FAST=1
set VICTORY_PIPELINE_WAIT_MS=20
set VICTORY_ASYNC_SUBMIT=1
set VICTORY_QUEUE2=1
set VICTORY_INDIRECT_WINDOW=1
set VICTORY_TEXTURE_NO_WAIT=1
set VICTORY_COPY_PLAIN=1
set VICTORY_WIDE_TEXTURES=1
set VICTORY_INDIRECT_GATHER=1
set VICTORY_LATE_WAIT_LISTS=1024
set VICTORY_CARD_FILLS_BATCH=0
set VICTORY_GATHER_DISPATCH=0
set VICTORY_RELAY=2
set VICTORY_WIDE_BACK=1
set VICTORY_RELAY_COPY=1
set VICTORY_CARD_STEPS=2
set VICTORY_INDIRECT_BATCH=2
set VICTORY_MAP_THREADS=1
set VICTORY_CARD_AWAKE=0
set VICTORY_SHOW_AFTER=1
set VICTORY_JOIN_PARTS=8
set VICTORY_UPLOAD_AHEAD=1
set VICTORY_POOL_DISCARD=1
set VICTORY_FILL_TITLE=1
set VICTORY_PARTIAL_DELTA=1
set VICTORY_BAKE_DELTA=1
set VICTORY_MAP_LOCK_FINE=1
set VICTORY_POOL_CAP=1
set VICTORY_TABLE_MEMO=1
set VICTORY_LIST_ALIAS_EXACT=1
set VICTORY_LIST_HOLD=1
set VICTORY_EARLY_TEXTURES_MS=40
set VICTORY_BAKE_TEXTURES_MS=10000
set VICTORY_HEAP_PASS_MAX=0
set VICTORY_HEAP_CHANGED_MAX=0
set VICTORY_LEAVE_OUT=02384a60fda6f2d0
set VICTORY_WC_NO_BACK=1
set VICTORY_WC_NO_BACK_MIN_KB=1024
set VICTORY_SYNC_IN_PLACE=1
set VICTORY_SPANS_QUICK=1
set VICTORY_SYNC_FINE=1
set VICTORY_HEAP_SYNC_FIRST=1
set VICTORY_HEAP_SYNC_AT_SUBMIT=1
set VICTORY_SOFT_VIEWS=copies
set VICTORY_SAMPLERS_MADE=1
set VICTORY_TABLE_NAMED_ONLY=1
set VICTORY_QUEUE_MARKS=1
set VICTORY_PORT_CONSTANTS=1
set VICTORY_EARLY_DEPTH=1
set VICTORY_AMBIENT=0.8
set VICTORY_AMBIENT_AIR=1.5

rem ---- first time only: uncomment the two lines below (takes ~21 min) ----
rem "%VICTORY_EXE%" shaders "%VICTORY_GAME_DIR%"
rem "%VICTORY_EXE%" warm

"%VICTORY_EXE%" run "%VICTORY_GAME_DIR%\game_scarlett_master.exe" --execute --console series-s
