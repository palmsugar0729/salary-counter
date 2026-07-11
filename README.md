# 工资结算表生成器

一款 Windows 桌面小工具，输入上课记录后自动生成月度的工资结算表 Excel 文件。

## 功能

- 录入上课信息：日期、时间、课时数、班级类型、备注
- 实时预览与自动计算薪酬
- **班级费率管理**：可视化配置不同班级的时薪（增删改查）
- **历史记录加载**：随时回看之前保存的月度数据
- 导出格式化的 Excel 结算表（同班级同色区分，严格按日期排列）
- 支持手动保存/加载数据，关闭时自动保存
- 双击编辑已有记录，一键清除全部

## 使用方式

### 方式一：直接运行（无需 Python）
下载 `codes/dist/SalaryCounter.exe`，双击即可运行。

### 方式二：从源码运行
```bash
pip install pyside6 openpyxl
python codes/main.py
```

### 重新打包
双击 `codes/build.bat`，或在 codes/ 目录下运行：
```bash
python -m PyInstaller --onefile --windowed --name SalaryCounter main.py
```

## 技术栈

PySide6 · openpyxl · Python 3.13.11

## 项目结构

```
├── codes/           # 源代码 + 打包脚本
│   └── dist/        #   独立 exe 输出
├── docs/            # 产品文档、PRD
├── assets/          # 设计与参考资料
├── notes/           # 学习笔记
└── AGENTS.md        # AI 开发指引
```
