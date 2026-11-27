
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
