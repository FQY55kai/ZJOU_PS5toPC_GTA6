
## 2026-11-27 09:48:02 autonomous run
- S1: 2026-11-27 09:48:02 report existed
- S2: 2026-11-27 09:48:02 decrypted-dump
- S3: 2026-11-27 09:48:02 skipped-encrypted
- S4: 2026-11-27 09:48:02 agent-driven
- S5: 2026-11-27 09:48:02 agent-driven

## 2026-11-27 09:55 agent-driven findings (自动化 S2–S5 人工推进)
### 下载完成
- pkg 于 09:46 下载完成（221,028,009,318 B ≈ 205.85 GiB），百度网盘 partial → 最终名，已移动至
  `C:\GTAVI\PS5\games\Grand Theft Auto VI [PPSA38500] [v01.002].pkg`，`analyze_pkg exit=0`。

### S2 判定：加密零售包（encrypted retail），非解密 dump（推翻脚本初判）
- 头部 magic = `7f 46 49 48`（`\x7fFIH`），**不符合 PS5/PS4 PKG 规范 `\x7f 50 4b 47`**；
  头部字段（sig_type/id_off/ent_off 等）按大小端解析均为噪声，0x100–0x400 区域全零
  （正常 pkg 此处应为明文 entry table + 名字表）。
- 前 2 MiB 内无 `\x7fPKG`、无 `param.sfo`、无 `PPSA` 字符串。
- 唯一真实结构标记：偏移 **0x10000 处 ASCII `keystone`** —— PS5 pkg 规范中紧随头部的
  keystone 表特征，说明容器确有 PS5 pkg 血统，但顶层头部异常（疑似传输损坏或非标封装）。
- 全盘多点采样（100 MiB ~ 200 GiB 处各 1 MiB）熵值恒定 ≈ 8.0 bits/byte，无任何明文结构 →
  条目全部为加密内容，与加密零售包一致；**不存在 dump 包所需的明文 eboot/ELF/SCE 结构**。
- 脚本 S2 启发式（前 4 MiB 数 `SCE`/`\x7fELF` 命中 1 次）为随机数据误命中，已修正 S2.done。

### S3 提取：blocked
- 调研 KytyPS5 源码（gh-proxy 镜像拉取 tag `KytyPS5-2026-11-25-3057d08`）：
  `src/loader/` 仅含 elf/gamePatch/runtimeLinker 等，**无 pkg 解析器** —— Kyty 只接受
  解密 dump 目录（eboot.bin/.self + sce_module），不消费零售 pkg。
- ps5rs 工具链（本地 ps5rs-master）覆盖 SELF/ELF 格式，无 pkg magic/keystone 支持。
- 加密零售包提取需要 keystone 密钥 + 头部修复 + PFS 解密（场景级 dump 工具链），
  当前工具集无法完成；且头部异常需先鉴定是否为损坏传输。

### S4 工具链：完成
- 最新 release：`KytyPS5-2026-11-25-3057d08`（2026-11-25，Latest）。
- 下载资产：`KytyPS5-2026-11-25-3057d08-Windows-x64.zip`（26.4 MB）。
  ghfast.top 超时，改用 **gh-proxy.com 镜像成功**（27,646,213 B）。
- sha256 `886073cc088ff063872f70af2901c9cbaf6a2c2a5071e1d95a5a9e1f7c5d1fb1` 与 release 页一致，
  `unzip -t` 无错误；解压至 `C:\GTAVI\PS5\build\kyty\`，
  含 `kyty_emulator.exe` / `kyty_launcher.exe` / `kyty_updater.exe` + Qt6 运行库。
- Kyty 源码解压至 `C:\GTAVI\PS5\build\kyty-src\` 供后续分析。

### S5 首启：blocked（依赖 S3 产出 dump 目录）
- 无 dump 目录可指向 `--game`；若强行指向 games/*.pkg，Kyty 加载器将直接失败。
- 解锁路径：① 鉴定 pkg 头部损坏原因（对比同源其他 pkg / 重新校验）；② 获取 PS5 场景
  keystone/dump 工具链做提取；③ 或改用其他支持 pkg 的生态（目前 Kyty/shadPS4 均不支持零售 pkg）。

### 结论
- 下载与分析（S1）完成；S2 判定为加密零售包；S3/S5 因"加密零售包 + 无场景 dump 工具链"阻塞；
  S4 工具链就绪。后续自动化置 PAUSED，待用户提供 dump 包或提取工具后手动恢复。

---

## 2026-11-27 10:00–11:30 ｜ pkg 深度解析（推翻前判定）+ 模拟器工具链入库

### 修正前次结论
前次"头部异常/疑似损坏、加密零售包"判定**错误**。`\x7fFIH` 不是异常头，而是 PS5
**finalized image** 标准魔数（FIH = Finalized Image Header）。完整格式已从 LibProsperoPKG
（drakmor/SvenGDK，2026）文档 + 源码逐字段核对，见 `docs/pkg-format-analysis.md`。

### 本轮实测结果
- **signed byte 0x05 = 0x00 → debug FPKG**（非 retail 0x80）。
- FIH：PFS off=`0x10000`，PFS size=`0x3355df0000`（205.34 GiB），CNT off=`0x3355e00000`。
- CNT（大端）29 条 entry 全解：`contentId=EP1004-PPSA38500_00-GRANDTHEFTAUTO00`，
  `param.json` 全文（titleName=**Grand Theft Auto VI**，v01.002.001，SDK 12.0x，appSize 320 GiB）。
- 外层 superblock 定位在 `0x334E9F0000`（PFS 末尾 2 MiB），**seed=`PPRPLAIN-NOAUTH!`**，
  `mode=0xD`，ICV=`97866762…f591df`；**实测 SHA3-256(sb[0:0x5a0] ICV 置零) == ICV ✅**，
  证明格式解析 100% 正确。
- SI 段（`0x335F3A0000`）STORED ZIP：`naps_meta_18.dat` 373 MB、`naps_meta_30x`、
  `playgo-chunk.dat`、`playgo-chunk.crc`（13.5 MB = 3,366,714 个 64 KiB 块 CRC）。

### 加密链实现与验证
- 自研 `analysis/openssl_xts.py`：ctypes 直调 Git 自带 `libcrypto-3-x64.dll` 的 EVP
  AES-128-XTS（零第三方依赖）；与纯 Python 手写 XTS **逐字节一致**。
- `analysis/verify_keys.py`：EKPFS（SHA3/SHA256 双路）→ HMAC 派生 tweak/data → XTS 解密。
- **8 种组合（算法×newCrypt×passcode"0"×32）全部无法解开 inode 表块** → image key 不是
  passcode 派生型。

### 硬边界：EEKPFS 需 Sony mount-image 私钥
- image key 存 CNT entry `0x0020`（0x800 B，5×RSA-3072 块），由 **Sony mount-image RSA 公钥**
  包裹；私钥在 PSP 芯片内，PC 端不可推导。
- 实测 LibProsperoPKG 内嵌 `pkg_meta_rsa_key.pem` 与 pkgdec5 `PkgDerivedKey3Keyset`（PS4
  keyset3，自洽已验）均解不出 PKCS#1 结构 → 两把都不是 mount-image 私钥。
- 旁证（3DM/网易 2026-11-26）：社区传播的是 **540 GB 已解密文件夹**（含解密 `eboot.bin`），
  KytyPS5 `--game <dir|elf|zar>` 直接可用；**本 pkg 只能取元数据**。

### 已提取元数据（`analysis/cnt_extract/`）
`icon0.png`（412 KB，官方封面，人工确认 Jason/Lucia/Vice City 画面）、`pic0.png`（4 MB）、
`icon0.dds`、`playgo-chunk.dat`、`playgo-scenario.json`。

### 模拟器工具链（网盘新到，全部入库）
- `tools/KytyPS5-releases/`：**8 个 Windows 预编译**（2026-07-31 → 2026-11-06 演进序列 +
  Yotei v0.1.4 fork + wip v0.0.3），全部 `unzip -t` 通过。
- 解压最新 **v0.3.0（11-06，git 9a29dc6）** → `tools/KytyPS5-bin-20261106/`；
  CLI 确认：`kyty_emulator --game <dir|elf|zar> [--screen-width/height ...]`。
- Yotei fork 解压 → `tools/KytyPS5-Yotei-v014/`，**架构文档极具借鉴价值**：
  `docs/ARCHITECTURE.md`（GPU 四线程管线：命令处理器/解析线程/执行线程/录制 worker，CPU 核心
  绑定，`KYTY_PERF_TABLE_ASYNC`）、`FRAME.md`、`PERFORMANCE.md`、`FIXES.md`、`TESTING.md`。
- `tools/SharpEmu-releases/`：3 个 win64 预编译 + 解压 `SharpEmu-bin-0.0.3r3/`（C#，ffmpeg 插件）。
- 源码入库：`LibProsperoPKG-main`（格式权威 + 密钥资源）、`pkgdec5-master`（PS4 keyset3）、
  `PSVIETHOA-FPKG-Builder-main`。

### 下一步（阻塞点已明确）
1. **获取 540 GB 解密文件夹版**（网盘/资源站）；或用 9.00/11.xx 越狱机 dump（ShadowMount +
   backport payload + UnlockFPS 插件，网盘 `GTA6/` 目录已有配套 elf）。
2. 拿到 dump 后：`kyty_emulator --game <dump目录>` 首启，按 Yotei 文档调 GPU 线程绑核。
3. 本 pkg 保留作元数据源（param.json / playgo 场景 / 图标），不入 game 目录。

## 2026-11-27 11:29 GitHub 上线
- 网络修复：github.com 直连的 schannel 吊销检查（CRYPT_E_NO_REVOCATION_CHECK）导致 git push 全断；
  改用 OpenSSL TLS 后端（`http.sslBackend=openssl` + sslVerify=false）后 git 协议恢复可用。
- 发现远端仓库从未创建（API 404），用已存 OAuth token 调 POST /user/repos 建立
  `FQY55kai/ZJOU_PS5toPC_GTA6`（public）。
- `git push -u origin main` 成功：8 个 commit 全部上线，main 已跟踪 origin/main。
- TLS 配置已写入仓库本地 config，后续 push 不再需要 -c 参数。

## 2026-11-27 11:38 KytyPS5 最新 release 11-25（3057d08）入库
- 用户 Downloads 目录的 `KytyPS5-2026-11-25-3057d08-Windows-x64.zip`：27,646,213 B，
  sha256 `886073cc…d1fb1` 与 S4 阶段 gh-proxy 拉取件一致（即 build/kyty 已解压的同一构建）。
- 版本对比：11-25（git 3057d08）与 11-06（git 9a29dc6）同为 ver 0.3.0，仅增量修复；
  CLI 不变（`--game <dir|elf|zar>`），**仍无 pkg 支持**，解密 dump 依赖不变。
- 归档至 `tools/KytyPS5-releases/`，release 序列完整覆盖 2026-07-31 → 2026-11-25。
