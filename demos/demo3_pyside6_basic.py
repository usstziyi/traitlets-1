"""
=============================================================================
Demo 3: PySide6 基础控件绑定 Traitlets 属性
=============================================================================

学习目标:
  1. 创建 PySide6 窗口
  2. 将 HasTraits 实例的属性绑定到 QLineEdit、QSpinBox、QComboBox 等控件
  3. 通过按钮操作修改 trait 值，观察 UI 同步更新

运行方式: python demos/demo3_pyside6_basic.py
"""

from traitlets import (
    HasTraits,
    Int,
    Float,
    Unicode,
    Bool,
    Enum,
    default,
    observe,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QLabel,
    QTextEdit,
)
from PySide6.QtCore import Qt


class UserSettings(HasTraits):
    username = Unicode("默认用户", help="用户名")
    age = Int(25, help="年龄")
    score = Float(88.5, help="分数")
    level = Enum(["初级", "中级", "高级"], default_value="中级", help="等级")
    vip = Bool(False, help="是否VIP")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = UserSettings()
        self._building_ui = False
        self._init_ui()
        self._connect_trait_signals()

    def _init_ui(self):
        self.setWindowTitle("Demo 3: PySide6 控件绑定 Traitlets")
        self.resize(500, 450)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        form_group = QGroupBox("用户设置 (由 Traitlets 管理)")
        form_layout = QFormLayout(form_group)

        self.username_edit = QLineEdit()
        form_layout.addRow("用户名:", self.username_edit)

        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 150)
        form_layout.addRow("年龄:", self.age_spin)

        self.score_spin = QDoubleSpinBox()
        self.score_spin.setRange(0, 100)
        self.score_spin.setSingleStep(0.5)
        self.score_spin.setDecimals(1)
        form_layout.addRow("分数:", self.score_spin)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["初级", "中级", "高级"])
        form_layout.addRow("等级:", self.level_combo)

        self.vip_check = QCheckBox("VIP 用户")
        form_layout.addRow("VIP:", self.vip_check)

        main_layout.addWidget(form_group)

        control_group = QGroupBox("操作")
        control_layout = QHBoxLayout(control_group)

        self.load_btn = QPushButton("从 Traitlets 加载 → UI")
        self.load_btn.clicked.connect(self._traits_to_ui)

        self.save_btn = QPushButton("UI → 更新 Traitlets")
        self.save_btn.clicked.connect(self._ui_to_traits)

        self.reset_btn = QPushButton("增量年龄")
        self.reset_btn.clicked.connect(self._increment_age)

        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.save_btn)
        control_layout.addWidget(self.reset_btn)

        main_layout.addWidget(control_group)

        log_group = QGroupBox("Trait 变化日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(log_group)

        self._traits_to_ui()

    def _connect_trait_signals(self):
        self.settings.observe(self._on_any_trait_change)

        self.username_edit.textChanged.connect(self._on_ui_changed)
        self.age_spin.valueChanged.connect(self._on_ui_changed)
        self.score_spin.valueChanged.connect(self._on_ui_changed)
        self.level_combo.currentTextChanged.connect(self._on_ui_changed)
        self.vip_check.stateChanged.connect(self._on_ui_changed)

    def _on_any_trait_change(self, change):
        if self._building_ui:
            return
        msg = f"[Trait 变更] {change['name']}: {change['old']} -> {change['new']}"
        self.log_text.append(msg)

    def _on_ui_changed(self):
        if self._building_ui:
            return
        self._ui_to_traits()

    def _traits_to_ui(self):
        self._building_ui = True
        s = self.settings
        self.username_edit.setText(s.username)
        self.age_spin.setValue(s.age)
        self.score_spin.setValue(s.score)
        self.level_combo.setCurrentText(s.level)
        self.vip_check.setChecked(s.vip)
        self._building_ui = False
        self.log_text.append(f"[UI 加载] 已从 Traitlets 同步到界面")

    def _ui_to_traits(self):
        self._building_ui = True
        self.settings.username = self.username_edit.text()
        self.settings.age = self.age_spin.value()
        self.settings.score = self.score_spin.value()
        self.settings.level = self.level_combo.currentText()
        self.settings.vip = self.vip_check.isChecked()
        self._building_ui = False
        self.log_text.append(f"[UI 保存] 已从界面同步到 Traitlets")

    def _increment_age(self):
        self.settings.age += 1


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
