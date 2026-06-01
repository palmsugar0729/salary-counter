"""PySide6 主窗口：表单 + 预览表 + 操作按钮。"""

from datetime import date, time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from config import CLASS_RATES
from excel_exporter import export
from models import MonthData, Record
from storage import load, save


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工资结算表生成器")
        self.resize(1100, 600)

        self._data = MonthData()
        self._current_file: str | None = None
        self._editing_index: int | None = None  # None=新增模式，数字=编辑对应行

        self._setup_ui()
        self._connect_signals()

    # ── UI 搭建 ──────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)

        # 输入区域
        form = QHBoxLayout()
        form.addWidget(QLabel("教师姓名"))
        self.name_edit = QLineEdit()
        self.name_edit.setMaximumWidth(100)
        self.name_edit.setPlaceholderText("姓氏")
        form.addWidget(self.name_edit)

        form.addWidget(QLabel("日期"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(self.date_edit.date().currentDate())
        form.addWidget(self.date_edit)

        form.addWidget(QLabel("时间"))
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        form.addWidget(self.time_edit)

        form.addWidget(QLabel("课时数"))
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0.5, 24.0)
        self.hours_spin.setSingleStep(0.5)
        self.hours_spin.setValue(2.5)
        self.hours_spin.setDecimals(1)
        form.addWidget(self.hours_spin)

        form.addWidget(QLabel("班级"))
        self.class_combo = QComboBox()
        self.class_combo.setEditable(True)
        self.class_combo.addItems(list(CLASS_RATES.keys()))
        form.addWidget(self.class_combo)

        form.addWidget(QLabel("备注"))
        self.note_edit = QLineEdit()
        self.note_edit.setMaximumWidth(120)
        form.addWidget(self.note_edit)

        root.addLayout(form)

        # 按钮行
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.add_btn.setMinimumWidth(80)
        btn_row.addWidget(self.add_btn)

        self.del_btn = QPushButton("删除选中行")
        self.del_btn.setMinimumWidth(100)
        btn_row.addWidget(self.del_btn)

        self.clear_btn = QPushButton("🗑 清除全部")
        self.clear_btn.setMinimumWidth(100)
        self.clear_btn.setStyleSheet("QPushButton { color: #c0392b; }")
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()

        self.cancel_edit_btn = QPushButton("取消编辑")
        self.cancel_edit_btn.setVisible(False)
        btn_row.addWidget(self.cancel_edit_btn)

        self.load_check = QCheckBox("启动时自动加载上次数据")
        self.load_check.setChecked(True)
        btn_row.addWidget(self.load_check)

        self.save_btn = QPushButton("保存数据")
        btn_row.addWidget(self.save_btn)

        self.export_btn = QPushButton("导出 Excel")
        self.export_btn.setMinimumWidth(100)
        self.export_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        btn_row.addWidget(self.export_btn)

        root.addLayout(btn_row)

        # 预览表格
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "日期", "星期", "时间", "小时数", "时薪（元/时）",
            "薪酬", "合计时数", "合计薪酬", "班级", "备注",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.table, stretch=1)

        # 底部汇总
        summary = QHBoxLayout()
        self.total_hours_label = QLabel("合计时数：0")
        self.total_salary_label = QLabel("合计薪酬：0 元")
        summary.addWidget(self.total_hours_label)
        summary.addSpacing(30)
        summary.addWidget(self.total_salary_label)
        summary.addStretch()
        root.addLayout(summary)

    # ── 信号连接 ──────────────────────────────────────

    def _connect_signals(self):
        self.add_btn.clicked.connect(self._on_add)
        self.del_btn.clicked.connect(self._on_delete)
        self.clear_btn.clicked.connect(self._on_clear_all)
        self.cancel_edit_btn.clicked.connect(self._on_cancel_edit)
        self.save_btn.clicked.connect(self._on_save)
        self.export_btn.clicked.connect(self._on_export)
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)

    # ── 槽函数 ────────────────────────────────────────

    def _on_add(self):
        class_type = self.class_combo.currentText().strip()
        if not class_type:
            QMessageBox.warning(self, "提示", "请选择或输入班级类型。")
            return

        qdate = self.date_edit.date()
        qtime = self.time_edit.time()
        rec = Record(
            date=date(qdate.year(), qdate.month(), qdate.day()),
            start_time=time(qtime.hour(), qtime.minute()),
            hours=self.hours_spin.value(),
            class_type=class_type,
            note=self.note_edit.text().strip(),
        )

        if self._editing_index is not None:
            # 更新模式
            self._data.records[self._editing_index] = rec
            self._exit_edit_mode()
        else:
            # 新增模式
            self._data.records.append(rec)

        self._refresh_table()

        # 检查是否为新班级类型
        if class_type not in CLASS_RATES:
            reply = QMessageBox.question(
                self, "新班级类型",
                f"「{class_type}」不在预设费率中，当前默认时薪 {rec.rate} 元/时。\n"
                f"是否将此班级类型添加到配置？（需要修改 config.py）",
            )
            if reply == QMessageBox.StandardButton.Yes:
                CLASS_RATES[class_type] = CLASS_RATES.get(class_type, rec.rate)
                self.class_combo.addItem(class_type)

    def _on_delete(self):
        rows = set(idx.row() for idx in self.table.selectedIndexes())
        if not rows:
            return
        sorted_recs = self._data.sorted_records()
        for row in sorted(rows, reverse=True):
            rec = sorted_recs[row]
            try:
                self._data.records.remove(rec)
            except ValueError:
                pass
        self._refresh_table()

    def _on_clear_all(self):
        if not self._data.records:
            return
        reply = QMessageBox.question(
            self, "确认清除",
            f"确定要清除全部 {len(self._data.records)} 条记录吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._data.records.clear()
            self._refresh_table()

    def _on_row_double_clicked(self, row: int, _col: int):
        if row < 0 or row >= len(self._data.records):
            return
        rec = self._data.sorted_records()[row]
        try:
            self._editing_index = self._data.records.index(rec)
        except ValueError:
            return

        self.date_edit.setDate(rec.date)
        self.time_edit.setTime(rec.start_time)
        self.hours_spin.setValue(rec.hours)
        self.class_combo.setEditText(rec.class_type)
        self.note_edit.setText(rec.note)

        self.add_btn.setText("✎ 更新")
        self.add_btn.setStyleSheet("QPushButton { font-weight: bold; color: #2980b9; }")
        self.cancel_edit_btn.setVisible(True)

    def _exit_edit_mode(self):
        self._editing_index = None
        self.add_btn.setText("添加")
        self.add_btn.setStyleSheet("")
        self.cancel_edit_btn.setVisible(False)

    def _on_cancel_edit(self):
        self._exit_edit_mode()


    def _on_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存数据", "records.json", "JSON 文件 (*.json)",
        )
        if not path:
            return
        self._data.teacher_name = self.name_edit.text().strip()
        save(path, self._data)
        self._current_file = path

    def _on_export(self):
        if not self._data.records:
            QMessageBox.warning(self, "提示", "请先添加至少一条上课记录。")
            return
        teacher = self.name_edit.text().strip()
        if not teacher:
            QMessageBox.warning(self, "提示", "请输入教师姓名。")
            return

        self._data.teacher_name = teacher
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 Excel", f"{teacher}_工资结算表.xlsx", "Excel 文件 (*.xlsx)",
        )
        if not path:
            return
        export(path, self._data)
        QMessageBox.information(self, "完成", f"已导出至：\n{path}")

    def _on_name_changed(self, text: str):
        self._data.teacher_name = text.strip()

    # ── 表格刷新 ──────────────────────────────────────

    def _refresh_table(self):
        records = self._data.sorted_records()
        self.table.setRowCount(len(records))
        for row, rec in enumerate(records):
            items = [
                QTableWidgetItem(rec.date.isoformat()),
                QTableWidgetItem(rec.weekday_str),
                QTableWidgetItem(rec.start_time.strftime("%H:%M")),
                QTableWidgetItem(str(rec.hours)),
                QTableWidgetItem(str(rec.rate)),
                QTableWidgetItem(str(rec.salary)),
                QTableWidgetItem(""),  # 合计时数（数据行留空）
                QTableWidgetItem(""),  # 合计薪酬（数据行留空）
                QTableWidgetItem(rec.class_type),
                QTableWidgetItem(rec.note),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

        self.total_hours_label.setText(f"合计时数：{self._data.total_hours}")
        self.total_salary_label.setText(f"合计薪酬：{self._data.total_salary} 元")

    # ── 窗口关闭 ──────────────────────────────────────

    def closeEvent(self, event):
        if self.load_check.isChecked() and self._data.records:
            from pathlib import Path
            default_path = Path.home() / ".salary-counter" / "autosave.json"
            default_path.parent.mkdir(parents=True, exist_ok=True)
            save(str(default_path), self._data)
        event.accept()

    def try_load_autosave(self):
        if not self.load_check.isChecked():
            return
        from pathlib import Path
        auto = Path.home() / ".salary-counter" / "autosave.json"
        if auto.exists():
            self._data = load(str(auto))
            self.name_edit.setText(self._data.teacher_name)
            self._refresh_table()
