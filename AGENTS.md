# AGENTS.md — AI 开发指引

## 项目简介

Windows 桌面应用：教师上课课时统计 → 自动生成 Excel 工资结算表。
技术栈：**PySide6 + openpyxl + JSON**。
Python 版本：**3.13.11**（当前环境已安装 PySide6 6.11.1, openpyxl 3.1.5）

## 文件夹结构

| 文件夹 | 用途 |
|---|---|
| `docs/` | 产品文档、PRD、需求迭代记录、关键决策文档 |
| `assets/design/` | 设计素材、UI 参考图、效果图 |
| `assets/bug/` | 测试报错截图 |
| `assets/reference/` | 参考图、灵感收集、竞品截图 |
| `notes/` | 学习笔记，开发中踩过的坑和技术方案记录 |
| `codes/` | **所有源代码**，应用程序的唯一代码目录 |

## 开发规则

### 代码组织
- 所有代码必须放在 `codes/` 目录下
- 代码区不得引用根目录或 `docs/` 等外部文件
- 入口文件：`codes/main.py`

### 架构分层（严格遵循）
```
codes/
  main.py              # 入口，组装各模块
  models.py            # 纯数据类（dataclass），不依赖 PySide6 / openpyxl
  config.py            # 班级费率等可配置常量
  storage.py           # JSON 读写，依赖 models
  excel_exporter.py    # openpyxl 导出逻辑
  ui/
    main_window.py     # PySide6 主窗口
    widgets.py         # 可复用组件
```

- `models.py` 是纯净层，只能使用 Python 标准库 + `config.py`
- `codes/build.bat` — 双击即可重新打包为独立 exe
- `codes/dist/` 和 `codes/build/` 是 PyInstaller 产物，不纳入版本管理
- `ui/` 负责所有 PySide6 相关代码
- `excel_exporter.py` 只依赖 openpyxl 和 models
- 新功能从 `main_window.py` 的 signal 连线开始，经过数据层，到输出层

### 设计原则
- 保持简单，不为假设的未来需求写抽象
- 三个一模一样的代码比一个过度设计的抽象好
- 不需要 ORM、不需要数据库、不需要配置文件系统（一个 config.py 足够）
- 不需要注释解释代码在做什么，好命名足够

### 安全与兼容
- 不引入系统级依赖，纯 Python + pip 可安装
- JSON 存储路径放在用户目录下的应用数据文件夹
- Excel 保存路径由用户通过对话框选择

## 当前状态

- [x] 需求讨论完成
- [x] PRD 完成
- [x] 项目结构创建
- [x] v0.1 代码实现完成
- [x] PyInstaller 打包可用

## 构建与打包

双击 `codes/build.bat` 即可重新生成 `codes/dist/SalaryCounter.exe`（约 60MB，无需 Python 环境即可运行）。

## 参考资源

- `docs/2026-05-31-需求讨论记录.md` — 完整需求讨论，含 Excel 格式解析
- `docs/PRD.md` — 产品需求文档
- `assets/design/screenshot_original-effect.png` — 目标效果图
- `assets/reference/2026沐晨_4月工资结算表-梁筱.xlsx` — 参考 Excel 文件
