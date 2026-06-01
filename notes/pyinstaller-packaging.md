# PyInstaller 打包学习记录

> 2026-06-01 | 基于 salary-counter 项目实际打包经验

## 什么是 PyInstaller

PyInstaller 将 Python 程序打包成**独立可执行文件**（Windows `.exe`），目标机器无需安装 Python 或任何依赖库。

## 基本命令

```bash
# 单文件打包（常用）
python -m PyInstaller --onefile --windowed --name 应用名 入口.py

# 参数说明
# --onefile     → 打包成单个 exe，方便分发
# --windowed    → 不显示命令行黑窗（GUI 应用用）
# --console     → 保留命令行窗口（CLI 工具用）
# --name  xxx   → 输出文件名（默认取脚本名）
```

## 本项目的打包

```bash
cd codes
python -m PyInstaller --onefile --windowed --name SalaryCounter-v0.1.1 main.py
```

### 输出结构

```
codes/
├── main.py                    # 入口
├── SalaryCounter.spec         # PyInstaller 配置文件
├── build/                     # 构建中间文件（可删除）
│   └── SalaryCounter/
└── dist/                      # ← 最终产物在这里
    ├── SalaryCounter.exe      # v0.1 原版
    └── SalaryCounter-v0.1.1.exe  # v0.1.1 新版
```

### 关键点

1. **入口文件**：`main.py` 必须能被 Python 找到，所以要在 `codes/` 目录下执行
2. **隐式导入**：项目用了 `from ui.main_window import MainWindow`，PyInstaller 会自动追踪
3. **PySide6**：PyInstaller 有专门的 hook（`hook-PySide6.*`），能自动收集 Qt DLL
4. **openpyxl**：通过 `_pyinstaller_hooks_contrib` 包的 hook 支持

## 版本共存策略

每次构建用不同的 `--name`，保留旧版本不删：

| 版本 | 文件名 | 说明 |
|------|--------|------|
| v0.1 | `SalaryCounter.exe` | 初始版本 |
| v0.1.1 | `SalaryCounter-v0.1.1.exe` | 体验改进版 |
| v0.2 | `SalaryCounter-v0.2.exe` | 后续版本… |

## 分发注意事项

### ✅ 优点
- 对方无需安装 Python、pip、虚拟环境
- 一个 exe 双击即用
- 约 60 MB（含 Python 运行时 + PySide6 + openpyxl + numpy）

### ⚠️ 注意事项
- **跨平台不兼容**：Win10 上打的包只能在 Windows 用。macOS 需在 Mac 上另行打包
- **杀软误报**：PyInstaller 打包的 exe 偶尔被 Windows Defender 标记，添加信任即可
- **启动稍慢**：首次运行需解压到临时目录，约 2-5 秒
- **数据存储**：用户数据保存在 `%USERPROFILE%\.salary-counter\autosave.json`，与 exe 文件位置无关

## 清理构建残留

```bash
# 删除构建中间文件（不影响 dist 产物）
rm -r build/
rm *.spec
```

## .spec 文件

PyInstaller 可以从 `.spec` 文件完成打包，比命令行更灵活：

```bash
python -m PyInstaller SalaryCounter.spec
```

.spec 文件可配置：隐式导入补丁、数据文件打包、图标、UPX 压缩等。

## 扩展阅读

- [PyInstaller 官方文档](https://pyinstaller.org/en/stable/)
- `--add-data` 打包图片/配置文件等非代码资源
- `--icon` 给 exe 加图标
- `--upx-dir` 用 UPX 进一步压缩体积
