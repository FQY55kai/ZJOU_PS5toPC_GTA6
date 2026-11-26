# ZJOU_PS5toPC_GTA6

**PlayStation 5 版 Grand Theft Auto VI（PPSA38500）到 Windows PC 的移植路径研究。**

本项目研究如何把 PS5 版 GTA VI 运行在 PC 上——不是盗版传播，不包含任何游戏文件、
密钥或破解代码；所有输入限定为用户自己拥有的明文 dump。

## 背景

GTA VI 无 PC 原生版。社区在 Xbox Series dump 路线上已经投入数周（见致谢），
开放世界场景实测 13–22 fps（PortWatch 社区记录，RTX 4090 级别硬件）。
PS5 dump（pkg）是另一条路线：同为 x86-64 CPU + RDNA 图形栈，
但系统调用面（Orbis ABI）、图形 API（AGC/GNM）和内存布局完全不同。

## 目标

1. **pkg 结构解析**（只读）：头部、entry 表、文件系统映像结构、未解密前提下的静态信息
2. **加载链研究**：PS5 ELF/SELF loader、SCE 模块依赖、Orbis syscall 面（对照 shadPS4 的 HLE 实现）
3. **GPU 翻译可行性**：AGC/PSSL → SPIR-V/DXIL，重点评估 RDNA wave64 → 主机 wave32 的降级问题
4. **统一内存虚拟化方案**：16 GB GDDR6 统一池 → 分裂的 PC 内存，对照 Xbox 侧
   VIctory 的 64 KiB 页 arena + 按需驻留 + 预算上限方案
5. **性能基线**：在 RTX 4080 Laptop（12 GB VRAM）+ i9-13900HX 上建立测量框架

## 已知困难（预判）

| 困难 | 说明 |
|---|---|
| 统一内存 | PS5 按 ~13.5 GB 可用统一池设计；12 GB VRAM 低于预算，必然部分驻留落系统内存，跨 PCIe |
| wave64 → wave32 | RDNA2 shader 以 64 lane 编译；NVIDIA wave 只有 32。Xbox 侧同类问题（LDS 拆分屏障放置）至今 open |
| AGC 极低层图形 API | 描述符表、40 位裸地址、primitive shader；等价于把 VIctory 的 GFX10→DXIL 工作再做一遍 |
| RT 不可用 RT 核心 | 标题的 BVH 遍历是自研 compute + RDNA 指令（`image_bvh_intersect_ray` 类），不是 API 调用 |
| Kraken IO | PS5 硬件解压单元 + 5.5 GB/s；PC 侧只能 CPU 软解或 HLE 异步 IO |
| Tempest 音频 | 专用 DSP 块，只能 CPU 软算 |
| 加密容器 | 本项目不解密、不处理密钥；loader 只接受用户自己的明文 dump |

## 现状与风险声明

截至 2026-11：**尚无可运行 GTA VI 的公开 PS5 模拟器。**
`shadps5.com` 自述相互矛盾（AOT recomp vs JIT、94/119 playable vs "not ready yet"）、
无源码仓库链接，**按钓鱼/假站对待，不使用其任何二进制**。
真实研究前沿：Apple Silicon 的 AOT recomp 实验框架、PS4 模拟器的 PS5 预研。

## 致谢与上游

**PS 侧**
- [shadps4-emu/shadPS4](https://github.com/shadps4-emu/shadPS4) — PS4 模拟器，Orbis HLE 与 GPU 翻译的参考实现
- [error9098x/ps5-native-mac](https://github.com/error9098x/ps5-native-mac) — PS5 AOT recomp 实验框架（Apple Silicon / Metal）
- AnyPS5 — SCE 库移植参考（ps5-native-mac 引用）
- [N64Recomp](https://github.com/N64Recomp/N64Recomp)、[XenonRecomp](https://github.com/hedge-dev/XenonRecomp)、[UnleashedRecomp](https://github.com/hedge-dev/UnleashedRecomp) — 全游戏 AOT 重编译方法论

**Xbox 侧（同标题先行者，方法论直接可迁移）**
- codec-d/CGBJ — cool_fox 原始 runtime 与 pareto residency 架构
- AvatarManz — VIctory-7900XTX：多线程命令录制、帧率解锁、renderer ports
- DoubleGhosty — cool_fox fork：renderer port 1/5（零拷贝常量路径）、光追文档
- fxceless — victory-fork：基础兼容层
- Belobug — VIctory-Belobug-AMD：环境光替身、整数混合保护
- Marvisak — VIctory：起点
- xcl-dev/xcl — Xbox Series 兼容层
- 4lwayz/portwatch-vi — 社区实测跟踪（本项目的性能对照数据源）

## 仓库纪律

与上游一致：不提交任何游戏文件及其派生物（提取的模块、重编译 C、shader dump、截图、
imports dump）；计数和体积可以。引导真实标题只经看门狗化的 harness。

## 许可

GPL-3.0-or-later
