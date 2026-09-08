# Work Walnut

> A walnut worn down by work, remembering to rest for you.

[Download](https://github.com/dazhanglang778-cyber/work-walnut/releases/latest) · [Give it a Star ⭐](https://github.com/dazhanglang778-cyber/work-walnut) · [Feedback & ideas](https://github.com/dazhanglang778-cyber/work-walnut/discussions) · [Report a bug](https://github.com/dazhanglang778-cyber/work-walnut/issues/new/choose)

[English](#work-walnut) · [中文](#工作坚果)

![Work Walnut hero](docs/images/hero.png)

Work Walnut is a tiny Windows desktop companion with a macOS beta. It occasionally wobbles and gradually changes through seven increasingly worn-out states. Each state change may show a warm, sarcastic, or slightly strange reminder to drink water, move around, and take a break.

[English usage guide](docs/USAGE_EN.md) · [English FAQ](docs/FAQ_EN.md) · [Privacy](docs/PRIVACY.md) · [中文说明](#工作坚果)

## Download

Download the latest release from [GitHub Releases](https://github.com/dazhanglang778-cyber/work-walnut/releases/latest).

- Windows x64: `工作坚果-Windows-x64-v1.0.0.zip`
- Apple Silicon Mac: `工作坚果-macOS-arm64-v1.0.0.zip`
- Intel Mac: `工作坚果-macOS-x64-v1.0.0.zip`

On Windows, extract the complete folder and run `启动工作坚果.exe`. Keep the `_internal` folder beside the EXE. On macOS, extract and open `工作坚果.app`. The macOS builds are unsigned, unnotarized betas; keep Gatekeeper enabled and only allow this individual app after verifying its Release source and SHA-256.

## Highlights

- Seven visual states, advancing every 45 minutes while the pet is running and the computer is awake.
- Random break-reminder speech bubbles on state changes.
- A final green overlay at 315 minutes; clicking it resets the cycle.
- Dragging, click-bounce, left-double-click rolling, and right-double-click physics launch.
- A right-click menu for manual states, reset, wobble control, and exit.
- Local-only operation with no accounts, ads, analytics, or telemetry.

![Motion demo](docs/images/demo.gif)

## Controls

| Input | Action |
|---|---|
| Left click | Small bounce |
| Left-button drag | Move the pet and place it against screen edges |
| Left double-click | Roll twice toward the screen interior |
| Right click | Open the state and settings menu |
| Right double-click | Launch diagonally with damped edge collisions |
| Click a bubble or green overlay | Dismiss it; the end-of-cycle overlay also resets the cycle |

On a Mac trackpad, use a two-finger secondary click or Control-click for right-click actions.

![Controls](docs/images/controls.png)

## Timing

The timer measures time while the pet process is running and the computer is awake. It does **not** monitor keyboard activity, mouse activity, or actual labor. Closing and reopening the app starts a new healthy cycle. A running instance also resets at the next calendar day.

![Seven states](docs/images/seven-states.png)

![Timeline](docs/images/timeline.png)

## License and artwork notice

The program code is licensed under **GPL-3.0-only**. Character artwork and derivative visual assets under `app/assets/` are explicitly outside the GPL grant.

The current artwork is derived from or related to *Plants vs. Zombies* visual material, and some states were based on online images whose complete authorship and license history could not be reliably traced. Free distribution and a disclaimer do not create permission. This is a free, non-commercial fan project and is not affiliated with, authorized, sponsored, or endorsed by Electronic Arts, PopCap Games, or their affiliates. Read [ASSET_NOTICE.md](ASSET_NOTICE.md) and [DISCLAIMER.md](DISCLAIMER.md) before reuse or redistribution.

Maintainer: `dazhanglang`

---

# 工作坚果

> 一颗会被工作啃坏的坚果，替你记得休息。

![工作坚果主视觉](docs/images/hero.png)

“工作坚果”是一款小巧的 Windows 桌面宠物，并提供 macOS 测试版。它会在桌面上偶尔晃动，也会随着运行时间逐渐从正常变成轻伤、受伤、海盗、重伤、疯狂和红温。每次状态变化时，它会随机说一句暖心、毒舌或有点奇怪的话，提醒你喝水、走动和休息。

[English](#work-walnut) · [完整玩法](docs/USAGE.md) · [常见问题](docs/FAQ.md) · [隐私说明](docs/PRIVACY.md)

## 下载与运行

### Windows 便携版（推荐）

请在 [GitHub Releases](https://github.com/dazhanglang778-cyber/work-walnut/releases/latest) 下载：

`工作坚果-Windows-x64-v1.0.0.zip`

解压完整文件夹后，双击 `启动工作坚果.exe`。便携版不需要安装 Python，也不会制作 MSI 安装包。请不要只复制 EXE；它需要与压缩包中的 `_internal` 文件夹保持在一起。

### macOS 测试版

Release 将同时提供：

- Apple Silicon（M1/M2/M3/M4 等）：`工作坚果-macOS-arm64-v1.0.0.zip`
- Intel Mac：`工作坚果-macOS-x64-v1.0.0.zip`

解压后打开 `工作坚果.app`。macOS 版目前未经 Apple Developer 签名与公证，应视为测试版；不要关闭 Gatekeeper。首次运行提示无法验证开发者时，请确认文件来自本仓库正式 Release 且 SHA-256 一致，再在系统“隐私与安全性”中单独允许这一个应用。

### 源码版

1. 安装 Python 3.10 或更高版本，并确认安装中包含 Tkinter。
2. 在仓库根目录运行 `python -m pip install -r requirements.txt`。
3. 双击 `启动源码版.bat`，或运行 `python app/wallnut_pet.py`。

## 它会做什么

- 每天和每次重新启动时从正常状态开始。
- 桌宠保持运行且电脑清醒时，每 45 分钟进入下一个状态。
- 状态变化时出现随机休息气泡；单击气泡即可关闭。
- 315 分钟后出现随机绿字并覆盖坚果正脸；单击绿字后恢复正常并重新计时。
- 支持自由拖动，并能贴到屏幕上、左、右边缘及任务栏上沿。
- 支持单击弹跳、左键双击滚动和右键双击物理弹射。
- 右键菜单可以切换状态、恢复精神、暂停晃动或退出。
- 无账号、无广告、无遥测，也不会联网发送数据。

![动作演示](docs/images/demo.gif)

## 操作方式

| 操作 | 效果 |
|---|---|
| 左键单击 | 轻轻弹一下 |
| 按住左键拖动 | 移动桌宠，可贴近屏幕边缘 |
| 左键双击 | 朝屏幕内侧快速滚动两圈 |
| 右键单击 | 打开状态和设置菜单 |
| 右键双击 | 沿随机对角线弹射并在屏幕边缘反弹 |
| 单击气泡或绿字 | 关闭提醒；单击周期末绿字还会重置状态 |

在 Mac 触控板上，“右键”指双指点按；也支持 `Control` + 单击。不同 Dock 位置可能需要在 `app/config.json` 调整 `mac_safe_margins`。

![鼠标操作说明](docs/images/controls.png)

## 状态循环

程序统计的是“桌宠运行且电脑处于清醒状态的时间”，不是键盘、鼠标或真实工时监控。电脑休眠、长时间卡顿和关闭程序的时间不会被直接累加。关闭后重新启动会从正常状态重新计时；跨自然日继续运行也会回到正常状态。

| 时间 | 状态 |
|---:|---|
| 0 分钟 | 正常 |
| 45 分钟 | 轻伤 |
| 90 分钟 | 受伤 |
| 135 分钟 | 海盗（高坚果） |
| 180 分钟 | 重伤（高坚果） |
| 225 分钟 | 疯狂 |
| 270 分钟 | 红温 |
| 315 分钟 | 随机绿字；单击后回到正常 |

![七状态全家福](docs/images/seven-states.png)

![在线工作时间线](docs/images/timeline.png)

## 配置

常用参数位于 [`app/config.json`](app/config.json)。你可以调整桌宠尺寸、晃动间隔、滚动距离、弹射速度、状态时间点和是否自动变化状态。修改前建议保留备份；JSON 格式错误会导致程序无法启动。

完整说明见 [docs/USAGE.md](docs/USAGE.md)。

## 隐私与安全

工作坚果只在本地运行，不要求账号，不读取文档、浏览器内容或输入记录，也不包含网络请求、广告与分析代码。详情见 [隐私说明](docs/PRIVACY.md) 和 [安全说明](SECURITY.md)。

## 许可与素材边界

程序代码采用 **GPL-3.0-only**。你可以依据 GPL 查看、修改和再发布代码，但必须保留相同许可证并提供相应源代码。

`app/assets/` 中的角色形象、美术图片及衍生内容**不属于 GPL 授权范围**。当前视觉内容源自或改编自《植物大战僵尸》相关形象，部分状态参考过来源无法完整追溯的网络图片。免费发布、免责声明和开源代码都不等于获得了素材授权。

本项目是免费、非商业同人项目，与 Electronic Arts、PopCap Games 及其关联方不存在隶属、授权、赞助或认可关系。下载、转载或制作修改版前，请阅读 [素材与权利说明](ASSET_NOTICE.md) 与 [免责声明](DISCLAIMER.md)。权利人可以使用“版权或素材问题”模板要求补充署名、替换或移除内容。

## 参与项目

欢迎报告 Bug、投稿提醒语或提交代码改进。Fork 不会改变原仓库；只有维护者审查并主动合并的 Pull Request 才会进入正式版本。请勿提交来源不明或无权公开的素材。详情见 [贡献指南](CONTRIBUTING.md)。

作者：`dazhanglang`
