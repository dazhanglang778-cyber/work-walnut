# Privacy

Work Walnut is a local desktop application. The current release has no account system, cloud sync, advertising, analytics, telemetry, or network data upload.

It reads only its own `config.json` and image assets, and keeps the current timer, state, window position, and animation state in memory. It reads the usable screen area only to constrain dragging and physics effects.

It does not inspect documents, images, clipboard contents, browser pages, chats, keyboard input, mouse history, real working time, or application usage. It does not upload screenshots, device information, or usage data, and does not install startup entries, background services, or remote-control channels.

The work timer is not saved to disk. Closing the app discards the current cycle. Operating systems, security software, or user-installed third-party tools may independently record process, crash, or file information; those activities are outside this project.

Any future networking, persistence, or diagnostics feature must update this notice and be disclosed in the corresponding Release notes before merging.

---

# 隐私说明

“工作坚果”按照本地桌面程序设计，当前版本不包含账号系统、云端同步、广告、分析或遥测。

## 程序会处理什么

- 读取项目自身的 `config.json` 和 `assets` 图片。
- 在内存中记录本次运行的时间、当前状态、窗口位置和动画状态。
- 读取 Windows 或 macOS 的可用屏幕区域，以限制拖动、滚动和弹射边界。

## 程序不会做什么

- 不读取你的文档、图片、剪贴板、浏览器页面或聊天内容。
- 不记录键盘输入、鼠标轨迹、真实工时或应用使用历史。
- 不上传桌面截图、设备信息或使用数据。
- 不创建账号、广告标识符或远程控制通道。
- 不自行添加开机启动项或后台服务。

## 本地状态

当前版本不把工作计时写入磁盘。关闭程序后，本轮计时和当前状态不会保留；再次启动会从正常状态开始。配置文件中的用户修改会保留，因为它本身就是本地项目文件。

Windows 本身、安全软件或用户主动使用的第三方工具可能记录进程、崩溃或文件信息，这些行为不由本项目控制。

如果未来版本加入任何联网、持久化或诊断功能，应在合并前更新本说明，并在 Release 说明中明确告知用户。
