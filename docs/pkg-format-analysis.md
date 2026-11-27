# PS5 pkg 包体分析报告 — GTA VI (PPSA38500)

> 分析对象：`Grand Theft Auto VI [PPSA38500] [v01.002].pkg`，221,028,009,318 字节（205.85 GiB）
> 分析时间：2026-11-27　｜　方法：纯只读解析 + 公开工具链（LibProsperoPKG）格式文档交叉验证

## 1. 结论摘要

| 项目 | 结果 |
|---|---|
| 容器类型 | PS5 **finalized image**，magic `\x7fFIH` |
| 签名字节 0x05 | **0x00 = debug FPKG**（非 retail 0x80） |
| 游戏身份 | `PPSA38500` / `EP1004-PPSA38500_00-GRANDTHEFTAUTO00` / **Grand Theft Auto VI** |
| 内容版本 | `01.002.001`，SDK `0x1200`（12.0x），要求系统 ≥ 12.00 |
| 安装体积 | `kernel.appSizeInGib = 320`（pkg 206GB 是 playgo 分块下载格式） |
| 外层 PFS | 205.34 GiB，AES-XTS，**superblock 明文 + ICV 验证通过** |
| 外层 seed | `PPRPLAIN-NOAUTH!`（ASCII，社区 FPKG 固定 seed） |
| image key（EEKPFS） | CNT entry `0x0020`，**RSA-3072 包裹，需 Sony mount-image 私钥** |
| 可提取性 | 元数据（图标/param.json/playgo）✅ 已提取；游戏本体 ❌ 卡在 image key |

## 2. 四段布局（实测）

```
0x00000000  FIH   头 + 终结摘要表（0x10000 字节，小端头）
0x00010000  PFS   外层共享 PFS 镜像，205.34 GiB（AES-XTS，4KiB 扇区 / 64KiB 块）
0x3355E00000  SC  \x7fCNT 元数据容器（29 条 entry，大端头）
0x335F3A0000  SI  install-metadata STORED ZIP（naps_meta_18 373MB + naps_meta_30x + playgo-chunk + crc）
```

- FIH 头（小端）：`0x00 magic` / `0x05 signed` / `0x10 PFS off=0x10000` / `0x18 PFS size=0x3355df0000` / `0x58 CNT off` / `0xA0 CNT size`
- PFS 段**块 0 = keystone**（明文，`keystone` + ver 3 + HMAC），块尾 = 外层 superblock（明文）

## 3. 外层 superblock（已完整验证）

绝对偏移 `0x334E9F0000`（PFS 内块 #3,362,462，镜像末尾 2MB 处）：

| 字段 | 值 |
|---|---|
| version / magic | 2 / 20130315（PS5） |
| mode | `0xD`（signed + 64bit + encrypted + always） |
| block_size | `0x10000`（**每块一个 XTS data unit**） |
| ndblock | 3,364,319 |
| dinode_count | 5（外层只装 keystone + pfs_image.dat + 元数据） |
| seed @0x370 | `PPRPLAIN-NOAUTH!` |
| inode 表 hash @0xb8 | `b6d15a78…fb043c`（SHA3-256） |
| inode 表块号 @0xd8 | 3,362,463 |
| ICV @0x380 | `97866762…f591df` — **SHA3-256(sb[0:0x5a0] ICV 置零) 实测匹配 ✅** |

**加密规则（LibProsperoPKG 已验证方案）**：数据块 tweak = 块号；signed 元数据块 tweak = `0x800000000000 | 块号`；superblock 块明文。

## 4. CNT 元数据（29 条 entry 全解）

`content_id`、`param.json`（7746 字节）完整读出：

- `titleName`: Grand Theft Auto VI（13 语言）
- `contentVersion`: 01.002.001，`masterVersion`: 01.00
- `kernel.appSizeInGib`: 320，`flexibleMemorySize`: 312,475,648
- `sdkVersion` / `requiredSystemSoftwareVersion`: `0x1200000000000000`
- `playgo.supportedApplicationOperationModes`: 6
- `psml.mfsrVersion`: 13.60

文件清单（19 个可读名）：`playgo-chunk.dat`、`icon0.png`、`pic0.png`、`pic2.png`、`icon0.dds`、`pic0.dds`、`snd0.at9`、`param.json`、`playgo-hash-table.dat`、`playgo-ficm.dat`、`playgo-scenario.json`、`trophy2/trophy00.ucp`、`uds/uds00.ucp`、`npbind.dat` 等。

**已成功导出**（`analysis/cnt_extract/`）：icon0.png（412KB，官方封面 ✅）、pic0.png（4.0MB）、icon0.dds（BC7）、playgo-chunk.dat、playgo-scenario.json。

## 5. image key 硬边界（本轮核心发现）

解密链完整实现并验证：

1. `EKPFS = H(H(BE(index=1)) ‖ H(content_id·NUL→48) ‖ passcode)`，H = SHA3-256 / SHA-256 双候选
2. `encKey = HMAC-SHA256(HMAC-SHA256(ekpfs, seed), LE(1)‖seed)`，tweak=前16B / data=后16B
3. XTS：OpenSSL EVP 实现 + 纯 Python 手写实现**交叉验证一致**（IEEE P1619 参数）

**结果**：8 种组合（SHA3/SHA256 × newCrypt true/false × passcode `"0"×32`）全部解不开 inode 表块（SHA3 不等于 0xb8 记录值）。

原因定位：本包 image key（EEKPFS）存放在 **CNT entry `0x0020`**，格式为 **RSA-3072 EME-PKCS#1 v1.5**（5 个 384B 块），加密公钥是 Sony **mount-image key**。实测：

- LibProsperoPKG 内嵌 `pkg_meta_rsa_key.pem`（RSA-3072 私钥）→ 解出无 PKCS#1 结构
- pkgdec5 的 `PkgDerivedKey3Keyset`（PS4 keyset 3 完整私钥，自洽验证通过）→ 同上
- 结论：mount-image RSA **私钥只存在于 Sony PSP 芯片 / 发布工具**，PC 端无从推导；retail→debug 重打包的包若沿用 Sony 公钥包裹，则**在 PC 上不可能解出**

## 6. 对移植路线的影响

社区（11-25 起，3DM/网易报道）传播的最终交付物是 **540GB 已解密游戏文件夹**（含解密 `eboot.bin` + `sce_sys/`），KytyPS5 的 `--game <dir|elf|zar>` 恰好直接吃这种结构。

因此：

- **本 pkg（206GB）→ 只能取元数据，不能作为移植输入**；
- **需要获取 540GB 解密文件夹版**（网盘/资源站），或从破解机 dump（需 9.00/11.xx 越狱机 + ShadowMount + backport payload）；
- 模拟器侧准备已就绪（KytyPS5 v0.3.0 + Yotei fork 架构文档 + SharpEmu 预编译）。

## 7. 工具与脚本

| 文件 | 作用 |
|---|---|
| `analysis/analyze_fih.py` | FIH/CNT 头解析（magic、signed、PFS/CNT 偏移） |
| `analysis/openssl_xts.py` | ctypes 调 Git 自带 libcrypto 的 AES-XTS（零依赖） |
| `analysis/verify_keys.py` | EKPFS 派生 + XTS 解密验证 |
| `analysis/cnt_extract/` | 已导出的元数据文件 |
| `tools/LibProsperoPKG-main/` | 格式权威参考 + 密钥资源（公钥/passcode moduli/私钥 pem） |
| `tools/pkgdec5-master/` | PS4 keyset3 完整私钥（交叉测试用） |

> 注：游戏美术资源（图标/封面）仅作身份验证，不入库。
