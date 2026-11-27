# GTA VI Xbox 分支（victory-scarlett-3070 "scarlett-fox"）RTX 4080 Laptop 复现配置

> 实测机型：机械师曙光 16 Pro（i9-13900HX + RTX 4080 Laptop 12GB）
> 游戏数据：GTA6.Xbox.v1.0.2.1（`game_scarlett_master.exe`）
> 实测性能：稳定 **21-26 fps**（38.4 ms/帧），显存受控不崩
> 日期：2026-11-27　run5 验证

## 1. 构建

```powershell
# 需要 Rust（rust-toolchain.toml 会自动选对版本）
cd victory-scarlett-3070-scarlett-fox
cargo build --release --bin victory --locked
# 产物: target\release\victory.exe
```

## 2. 着色器预热（首次必做，约 21 分钟，之后跳过）

```cmd
set VICTORY_GAME_DIR=C:\GTAVI\GTA6.Xbox.v1.0.2.1
victory.exe shaders C:\GTAVI\GTA6.Xbox.v1.0.2.1
victory.exe warm
```

缓存热后可免预热直启（见 `Start-4080-GTA6.cmd`）。

## 3. 关键环境变量（实测敲定，勿乱改）

### 3.1 防崩溃三项（run2 崩溃教训）

| 变量 | 值 | 原因 |
|---|---|---|
| `VICTORY_TEXTURE_MIP_DROP` | `1` | 纹理降 mip，省约 75% 纹理显存（12GB 卡必开） |
| `VICTORY_TEXTURE_BUDGET_MB` | `6144` | **硬限** shader-index 纹理副本字节数。源码注释：*"Past the budget the system moves the card's memory into the PC's, which ended runs 20 and 24"*——超预算 Windows 会把显存挪进内存，进程静默死亡（无任何日志） |
| `VICTORY_TEXTURE_ROOM_PERCENT` | `80` | 显存余量 20% 留给系统（默认 94% 在 12GB 卡上必撞墙） |

### 3.2 帧率档位

| 变量 | 值 | 说明 |
|---|---|---|
| `VICTORY_FRAME_INTERVAL_MS` | `33.3` | **30fps 档**。CPU 翻译线程实际 25-40ms/帧，60fps 档（16.667）根本追不上反而积压 |

### 3.3 缓冲区（run3 卡顿教训）

| 变量 | 值 | 原因 |
|---|---|---|
| `VICTORY_CARD_BUFFERS_MB` | `1024` | **不要降到 512**。实测：512 导致 GPU 复制碎片化，GPU 时间 150ms/帧（正常 0-5ms），帧率从 26 跌到 5，buffer copies 流量翻倍 |
| `VICTORY_CARD_WINDOWS_MB` | `512` | 保持默认 |
| `VICTORY_CARD_BUFFERS_MIN_KB` | `64` | 保持默认 |

### 3.4 其余开关（fork 作者 3070 play 脚本直译，全部保留）

```bat
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
```

## 4. 启动

```cmd
victory.exe run C:\GTAVI\GTA6.Xbox.v1.0.2.1\game_scarlett_master.exe --execute --console series-s
```

完整一键脚本见仓库根目录 `Start-4080-GTA6.cmd`（免预热直启版）。

## 5. 正常启动过程（别把加载期当卡顿）

1. 菜单/开场：跑满 30fps
2. 世界加载流送期：**4-17fps 正常**，持续 1-3 分钟（13 万张纹理上传，GPU detile 压顶）
3. 流送完成：回升稳定 **21-26fps**

`dropped NNNN without a host pipeline` 在流送期是正常的。

## 6. 排错速查

| 症状 | 日志特征 | 处理 |
|---|---|---|
| 静默崩溃（无 ERROR 无 WER） | 显存 >85%，日志末尾正常统计戛然而止 | 加 `VICTORY_TEXTURE_BUDGET_MB`（6144 或更低）+ `ROOM_PERCENT=80` |
| 持续 4-6fps，GPU 时间 >100ms/帧 | `copies XX ms XXX MB` 流量 >90MB/帧 | `CARD_BUFFERS_MB` 回到 1024 |
| 持续卡但 GPU 时间 0ms | preparing >25ms | 关诊断统计（`TABLE_MEMO`/`QUEUE_MARKS`/`LIST_ALIAS_EXACT`），或 `MAP_THREADS=2` |
| Windows 事件查看器出现 `RADAR_PRE_LEAK_64` | — | host 内存泄漏警告，是崩溃前兆，同上减预算 |
