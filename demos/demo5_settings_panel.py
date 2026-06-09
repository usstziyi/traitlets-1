"""
=============================================================================
Demo 5: 高级应用 —— 完整设置面板 + JSON 导出与启动加载
=============================================================================

学习目标:
  1. 构建完整的设置面板，包含多种控件类型
  2. 实现 traitlets 参数到 JSON 文件的导出 (to_json)
  3. 实现从 JSON 文件启动加载参数 (from_json)
  4. 使用 @validate 进行跨属性校验
  5. 掌握 traitlets 在实际项目中的应用模式

运行方式: python demos/demo5_settings_panel.py

配置文件默认保存在: ./app_settings.json
=============================================================================
"""

import json
import os
from pathlib import Path
from typing import Any

from traitlets import (
    HasTraits,
    Int,
    Float,
    Unicode,
    Bool,
    Enum,
    List,
    Dict,
    All,
    default,
    observe,
    validate,
    TraitError,
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
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QLabel,
    QSlider,
)
from PySide6.QtCore import Qt


DEFAULT_CONFIG_PATH = Path("./app_settings.json")


class AppSettings(HasTraits):
    """
    应用程序全局设置，由 traitlets 管理所有参数的类型检查和校验。
    每个 trait 都带有 help 描述，tag(config=True) 标记为可配置项。
    """

    window_title = Unicode("我的应用", help="窗口标题")
    window_width = Int(800, help="窗口宽度")
    window_height = Int(600, help="窗口高度")
    theme = Enum(["浅色", "深色", "跟随系统"], default_value="浅色", help="主题")
    language = Enum(["中文", "English", "日本語"], default_value="中文", help="界面语言")

    username = Unicode("", help="用户名")
    auto_login = Bool(False, help="自动登录")
    remember_password = Bool(True, help="记住密码")

    max_items = Int(100, help="最大显示条目数")
    auto_save_interval = Float(5.0, help="自动保存间隔（秒）")
    enable_sound = Bool(True, help="启用音效")
    log_level = Enum(["DEBUG", "INFO", "WARNING", "ERROR"], default_value="INFO", help="日志级别")

    shortcuts = Dict(
        key_trait=Unicode(),
        value_trait=Unicode(),
        default_value={
            "新建": "Ctrl+N",
            "保存": "Ctrl+S",
            "退出": "Ctrl+Q",
        },
        help="快捷键配置",
    )

    recent_files = List(Unicode(), default_value=[], help="最近打开文件列表")

    def __init__(self, config_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self._modified = False
        self._loading = False

    @validate("window_width")
    def _validate_width(self, proposal):
        value = proposal["value"]
        if value < 400:
            return 400
        if value > 3840:
            return 3840
        return value

    @validate("window_height")
    def _validate_height(self, proposal):
        value = proposal["value"]
        if value < 300:
            return 300
        if value > 2160:
            return 2160
        return value

    @validate("auto_save_interval")
    def _validate_interval(self, proposal):
        value = proposal["value"]
        if value < 1.0:
            return 1.0
        if value > 3600.0:
            return 3600.0
        return value
        
    @observe(All)
    def _mark_modified(self, change):
        # 用于区分"程序化加载"和"用户编辑"
        # 只有用户编辑时才标记为修改状态
        if not self._loading:
            # 标记为修改状态
            self._modified = True
            print(f"已修改")

    def to_dict(self) -> dict[str, Any]:
        """
        将所有 trait 属性导出为可序列化的字典。
        只导出 trait_names() 中的属性，忽略私有属性。
        """
        result = {}
        for name in self.trait_names():
            result[name] = getattr(self, name)
        return result

    def to_json(self, path=None) -> str:
        """
        将当前设置导出为 JSON 文件。

        参数:
            path: 文件路径，默认使用 self._config_path

        返回:
            导出文件的路径字符串
        """
        save_path = Path(path) if path else self._config_path
        data = self.to_dict()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(save_path)

    def from_dict(self, data: dict[str, Any]):
        """
        从字典加载设置，只更新存在于 trait_names() 中的属性。
        未知键会被忽略。
        """
        self._loading = True
        available = set(self.trait_names())
        for key, value in data.items():
            if key in available:
                try:
                    setattr(self, key, value)
                except TraitError as e:
                    print(f"  警告: 跳过 '{key}' —— {e}")
        self._loading = False

    def from_json(self, path=None):
        """
        从 JSON 文件加载设置。

        参数:
            path: 文件路径，默认使用 self._config_path

        返回:
            True 表示加载成功，False 表示文件不存在或解析失败
        """
        load_path = Path(path) if path else self._config_path
        if not load_path.exists():
            return False
        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.from_dict(data)
            return True
        except (json.JSONDecodeError, OSError) as e:
            print(f"  JSON 解析失败: {e}")
            return False

    # 这是一个只读属性，向外暴露内部的修改状态
    # @property — 将 modified 变成一个属性而非方法，
    # 外部访问时写成 obj.modified 而不是 obj.modified() ，更简洁。
    @property
    def modified(self):
        return self._modified

    def mark_saved(self):
        self._modified = False


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self._init_ui()
        self._try_auto_load()

    def _init_ui(self):
        self.setWindowTitle("Demo 5: 设置面板 + JSON 导出/加载")
        self.resize(650, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        general_group = QGroupBox("通用设置")
        general_layout = QFormLayout(general_group)

        self.title_edit = QLineEdit()
        general_layout.addRow("窗口标题:", self.title_edit)

        width_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 3840)
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(400, 1920)
        width_layout.addWidget(self.width_spin)
        width_layout.addWidget(self.width_slider)
        general_layout.addRow("窗口宽度:", width_layout)

        height_layout = QHBoxLayout()
        self.height_spin = QSpinBox()
        self.height_spin.setRange(300, 2160)
        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setRange(300, 1200)
        height_layout.addWidget(self.height_spin)
        height_layout.addWidget(self.height_slider)
        general_layout.addRow("窗口高度:", height_layout)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])
        general_layout.addRow("主题:", self.theme_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "English", "日本語"])
        general_layout.addRow("语言:", self.lang_combo)

        main_layout.addWidget(general_group)

        account_group = QGroupBox("账户设置")
        account_layout = QFormLayout(account_group)

        self.username_edit = QLineEdit()
        account_layout.addRow("用户名:", self.username_edit)

        self.auto_login_check = QCheckBox()
        account_layout.addRow("自动登录:", self.auto_login_check)

        self.remember_pwd_check = QCheckBox()
        account_layout.addRow("记住密码:", self.remember_pwd_check)

        main_layout.addWidget(account_group)

        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout(advanced_group)

        self.max_items_spin = QSpinBox()
        self.max_items_spin.setRange(10, 10000)
        self.max_items_spin.setSingleStep(10)
        advanced_layout.addRow("最大条目数:", self.max_items_spin)

        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(1.0, 3600.0)
        self.interval_spin.setSingleStep(5.0)
        self.interval_spin.setDecimals(1)
        self.interval_spin.setSuffix(" 秒")
        advanced_layout.addRow("自动保存间隔:", self.interval_spin)

        self.sound_check = QCheckBox()
        advanced_layout.addRow("启用音效:", self.sound_check)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        advanced_layout.addRow("日志级别:", self.log_level_combo)

        main_layout.addWidget(advanced_group)

        shortcut_group = QGroupBox("快捷键配置（JSON 直接编辑）")
        shortcut_layout = QVBoxLayout(shortcut_group)
        self.shortcut_edit = QTextEdit()
        self.shortcut_edit.setMaximumHeight(100)
        self.shortcut_edit.setPlaceholderText('{"新建": "Ctrl+N", "保存": "Ctrl+S", ...}')
        shortcut_layout.addWidget(self.shortcut_edit)
        main_layout.addWidget(shortcut_group)

        btn_group = QGroupBox("文件操作")
        btn_layout = QHBoxLayout(btn_group)

        self.load_from_ui_btn = QPushButton("UI → Settings")
        self.load_from_ui_btn.clicked.connect(self._ui_to_settings)

        self.load_btn = QPushButton("从 JSON 加载")
        self.load_btn.clicked.connect(self._load_json)

        self.save_btn = QPushButton("导出 JSON")
        self.save_btn.clicked.connect(self._save_json)

        self.export_btn = QPushButton("另存为...")
        self.export_btn.clicked.connect(self._export_json)

        btn_layout.addWidget(self.load_from_ui_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.export_btn)
        main_layout.addWidget(btn_group)

        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(log_group)

        self._settings_to_ui()

        self._connect_signals()

    def _connect_signals(self):
        self.settings.observe(self._on_setting_changed)

    def _on_setting_changed(self, change):
        if change["name"] == "shortcuts":
            return
        self._log(f"[参数变更] {change['name']}: {change['old']} -> {change['new']}")

    def _settings_to_ui(self):
        s = self.settings
        self.title_edit.setText(s.window_title)
        self.width_spin.setValue(s.window_width)
        self.width_slider.setValue(s.window_width)
        self.height_spin.setValue(s.window_height)
        self.height_slider.setValue(s.window_height)
        self.theme_combo.setCurrentText(s.theme)
        self.lang_combo.setCurrentText(s.language)
        self.username_edit.setText(s.username)
        self.auto_login_check.setChecked(s.auto_login)
        self.remember_pwd_check.setChecked(s.remember_password)
        self.max_items_spin.setValue(s.max_items)
        self.interval_spin.setValue(s.auto_save_interval)
        self.sound_check.setChecked(s.enable_sound)
        self.log_level_combo.setCurrentText(s.log_level)
        self.shortcut_edit.setPlainText(json.dumps(s.shortcuts, ensure_ascii=False, indent=2))

    def _ui_to_settings(self):
        s = self.settings
        s.window_title = self.title_edit.text()
        s.window_width = self.width_spin.value()
        s.window_height = self.height_spin.value()
        s.theme = self.theme_combo.currentText()
        s.language = self.lang_combo.currentText()
        s.username = self.username_edit.text()
        s.auto_login = self.auto_login_check.isChecked()
        s.remember_password = self.remember_pwd_check.isChecked()
        s.max_items = self.max_items_spin.value()
        s.auto_save_interval = self.interval_spin.value()
        s.enable_sound = self.sound_check.isChecked()
        s.log_level = self.log_level_combo.currentText()

        try:
            shortcuts = json.loads(self.shortcut_edit.toPlainText())
            s.shortcuts = shortcuts
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON 解析错误", f"快捷键格式错误:\n{e}")

        self._log("[UI → Settings] 已同步所有参数到 AppSettings")

    def _save_json(self):
        path = self.settings.to_json()
        self.settings.mark_saved()
        self._log(f"[导出 JSON] 已保存到: {path}")
        data = self.settings.to_dict()
        self._log(f"  导出的键: {list(data.keys())}")

    def _export_json(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出 JSON 配置文件", "", "JSON 文件 (*.json)"
        )
        if filepath:
            path = self.settings.to_json(filepath)
            self.settings.mark_saved()
            self._log(f"[另存为] 已导出到: {path}")

    def _load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "加载 JSON 配置文件", "", "JSON 文件 (*.json)"
        )
        if not filepath:
            return

        success = self.settings.from_json(filepath)
        if success:
            self._settings_to_ui()
            self._log(f"[加载 JSON] 已从文件加载: {filepath}")
            for name in self.settings.trait_names():
                self._log(f"  {name} = {getattr(self.settings, name)}")
        else:
            QMessageBox.warning(self, "加载失败", f"文件不存在或 JSON 格式错误:\n{filepath}")
            self._log(f"[加载失败] {filepath}")

    def _try_auto_load(self):
        success = self.settings.from_json()
        if success:
            self._settings_to_ui()
            self._log(f"[启动加载] 已自动加载: {DEFAULT_CONFIG_PATH.resolve()}")
        else:
            self._log(f"[启动] 未找到配置文件，使用默认值")

    def _log(self, msg):
        self.log_text.append(msg)

    def closeEvent(self, event):
        if self.settings.modified:
            reply = QMessageBox.question(
                self,
                "未保存的更改",
                "设置有未保存的更改，是否导出 JSON 后再退出？",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_json()
            elif reply == QMessageBox.StandardButton.Cancel:
                # event.ignore() 告诉 Qt："忽略本次关闭事件"，窗口保持打开状态。
                # 这是 Qt 中实现"取消关闭"的标准写法。
                event.ignore()
                return
        event.accept()


def main():
    app = QApplication([])
    window = SettingsWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
