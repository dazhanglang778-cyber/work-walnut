# 构建说明

项目采用 PyInstaller 的文件夹模式，不制作 MSI/PKG，也不使用单文件模式。每个平台必须在对应操作系统上分别构建。

## Windows x64

1. 安装 Python 3.12（包含 Tcl/Tk）。
2. 在仓库根目录运行 `python -m pip install -r requirements-build.txt`。
3. 运行 `powershell -ExecutionPolicy Bypass -File build/build_windows.ps1`。

成品输出到 `build-output/release/工作坚果-Windows-x64-v1.0.0.zip`。

## macOS

1. 安装 Python 3.12（官方安装包包含 Tcl/Tk）。
2. 在仓库根目录运行 `python3 -m pip install -r requirements-build.txt`。
3. 运行 `bash build/build_macos.sh`。

Apple Silicon 会输出 `工作坚果-macOS-arm64-v1.0.0.zip`，Intel Mac 会输出 `工作坚果-macOS-x64-v1.0.0.zip`。ZIP 使用 macOS 自带的 `ditto` 生成，以保留 `.app` 的资源属性。

## 自动构建

`.github/workflows/build-binaries.yml` 会在手动触发或推送版本标签时，分别使用 Windows、Apple Silicon Mac 和 Intel Mac 构建三个 Release 候选文件，并附带 SHA-256。

macOS 首发版暂不进行 Apple Developer 签名和公证，因此应标记为测试版，并在真实 Mac 上完成透明窗口、菜单栏/Dock 边界、触控板操作和退出流程测试后再正式推荐。
