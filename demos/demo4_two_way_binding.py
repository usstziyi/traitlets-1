"""
=============================================================================
Demo 4: 双向绑定 —— PySide6 控件与 Traitlets 自动同步
=============================================================================

学习目标:
  1. 实现 UI 控件与 traitlets 属性的自动双向绑定
  2. 封装通用的 bind/unbind 机制，避免手动同步样板代码
  3. 展示多个控件间的联动效果（滑块 + 数值框）

运行方式: python demos/demo4_two_way_binding.py
"""

from traitlets import HasTraits, Int, Float, Unicode, Bool
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
    QSlider,
    QCheckBox,
    QLabel,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Qt, QObject, Signal


class BindingManager:
    """
    通用的双向绑定管理器:
      控件值变化 → 自动更新 trait
      trait 值变化 → 自动更新控件
    """

    def __init__(self):
        self._bindings = []
        # 一个防重入锁,用于打破双向绑定的无限循环
        self._updating = False
        self._count = 0

    def bind(self, trait_obj, trait_name, widget, widget_getter, widget_setter,
             widget_signal):
        """
        trait_obj:   HasTraits 实例
        trait_name:  trait 属性名
        widget:      PySide6 控件
        widget_getter:  无参函数，返回控件当前值
        widget_setter:  单参函数，设置控件值
        widget_signal:  控件值变化信号
        """
        entry = {
            "obj": trait_obj,
            "name": trait_name,
            "widget": widget,
            "get": widget_getter,
            "set": widget_setter,
            "signal": widget_signal,
        }
        # 将绑定配置添加到内部列表，便于后续统一管理和清理
        self._bindings.append(entry)

        # ui -> trait
        # 当控件值变化时，自动更新 trait
        widget_signal.connect(lambda *a: self._widget_to_trait(entry))

        # trait -> ui
        # 当 trait 值变化时，自动更新控件
        trait_obj.observe(lambda change: self._trait_to_widget(entry, change), trait_name)

        # 让输入控件显示 trait 默认值
        widget_setter(getattr(trait_obj, trait_name))

    def unbind_all(self):
        for entry in self._bindings:
            try:
                entry["signal"].disconnect()
            except RuntimeError:
                pass
        self._bindings.clear()

    def _widget_to_trait(self, entry):
        if self._updating:
            return
        self._updating = True
        try:
            # 把控件的当前值写入 trait
            # 等价于 entry["obj"].<trait_name> = entry["get"]()
            # 即：将控件的当前值赋给 trait 对象的指定属性
            setattr(entry["obj"], entry["name"], entry["get"]())
        finally:
            self._updating = False

    def _trait_to_widget(self, entry, change):
        # 为了spin和slider联动，破例放开防重入锁
        # 把守卫工作下放到qt内部
        self._updating = False
        if self._updating:
            return
        self._updating = True
        try:
            entry["set"](change["new"])
        finally:
            self._updating = False


class ColorConfig(HasTraits):
    red = Int(128, help="红色分量 (0-255)")
    green = Int(128, help="绿色分量 (0-255)")
    blue = Int(128, help="蓝色分量 (0-255)")
    alpha = Float(1.0, help="不透明度 (0.0-1.0)")
    label = Unicode("示例文字", help="标签文字")
    uppercase = Bool(False, help="是否大写")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ColorConfig()
        self.binder = BindingManager()
        self._init_ui()
        self._bind_all()

    def _init_ui(self):
        self.setWindowTitle("Demo 4: 双向绑定 —— 自动同步")
        self.resize(550, 500)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        rgb_group = QGroupBox("RGB 颜色设置")
        rgb_layout = QVBoxLayout(rgb_group)
        """
        等价于
        self.red_slider   = QSlider(...)
        self.red_spin     = QSpinBox(...)
        self.green_slider = QSlider(...)
        self.green_spin   = QSpinBox(...)
        self.blue_slider  = QSlider(...)
        self.blue_spin    = QSpinBox(...)
        """
        for name, trait_name in [("R 红色", "red"), ("G 绿色", "green"), ("B 蓝色", "blue")]:
            row = QHBoxLayout()

            # 复用
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 255)
            setattr(self, f"{trait_name}_slider", slider)

            # 复用
            spin = QSpinBox()
            spin.setRange(0, 255)
            setattr(self, f"{trait_name}_spin", spin)

            label = QLabel(name)
            label.setFixedWidth(50)

            row.addWidget(label)
            row.addWidget(slider, 3)
            row.addWidget(spin, 1)
            rgb_layout.addLayout(row)

        main_layout.addWidget(rgb_group)

        other_group = QGroupBox("其他设置")
        other_layout = QFormLayout(other_group)

        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_label = QLabel("1.00")
        alpha_row = QHBoxLayout()
        alpha_row.addWidget(self.alpha_slider, 3)
        alpha_row.addWidget(self.alpha_label, 1)
        other_layout.addRow("Alpha 不透明度:", alpha_row)

        self.label_edit = QLineEdit()
        other_layout.addRow("标签文字:", self.label_edit)

        self.upper_check = QCheckBox("转为大写")
        other_layout.addRow("大写:", self.upper_check)

        main_layout.addWidget(other_group)

        preview_group = QGroupBox("实时预览")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("示例文字")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; border: 2px solid #ccc; border-radius: 8px;"
        )
        preview_layout.addWidget(self.preview_label)

        self.info_label = QLabel()
        preview_layout.addWidget(self.info_label)

        main_layout.addWidget(preview_group)

        self.reset_btn = QPushButton("恢复默认配置")
        self.reset_btn.clicked.connect(self._reset_defaults)
        main_layout.addWidget(self.reset_btn)

    def _bind_all(self):
        b = self.binder

        b.bind(
            self.config, "red",
            self.red_slider,
            lambda: self.red_slider.value(),
            lambda v: self.red_slider.setValue(int(v)),
            self.red_slider.valueChanged,
        )
        b.bind(
            self.config, "red",
            self.red_spin,
            lambda: self.red_spin.value(),
            lambda v: self.red_spin.setValue(int(v)),
            self.red_spin.valueChanged,
        )

        b.bind(
            self.config, "green",
            self.green_slider,
            lambda: self.green_slider.value(),
            lambda v: self.green_slider.setValue(int(v)),
            self.green_slider.valueChanged,
        )
        b.bind(
            self.config, "green",
            self.green_spin,
            lambda: self.green_spin.value(),
            lambda v: self.green_spin.setValue(int(v)),
            self.green_spin.valueChanged,
        )

        b.bind(
            self.config, "blue",
            self.blue_slider,
            lambda: self.blue_slider.value(),
            lambda v: self.blue_slider.setValue(int(v)),
            self.blue_slider.valueChanged,
        )
        b.bind(
            self.config, "blue",
            self.blue_spin,
            lambda: self.blue_spin.value(),
            lambda v: self.blue_spin.setValue(int(v)),
            self.blue_spin.valueChanged,
        )

        b.bind(
            self.config, "alpha",
            self.alpha_slider,
            lambda: self.alpha_slider.value() / 100.0,
            lambda v: self.alpha_slider.setValue(int(v * 100)),
            self.alpha_slider.valueChanged,
        )

        b.bind(
            self.config, "label",
            self.label_edit,
            lambda: self.label_edit.text(),
            lambda v: self.label_edit.setText(str(v)),
            self.label_edit.textChanged,
        )

        b.bind(
            self.config, "uppercase",
            self.upper_check,
            lambda: self.upper_check.isChecked(),
            lambda v: self.upper_check.setChecked(bool(v)),
            self.upper_check.stateChanged,
        )

        self.config.observe(self._update_preview)

        self._update_preview(None)

    # 让预览区渲染默认颜色和文字
    def _update_preview(self, change):
        c = self.config
        display = c.label.upper() if c.uppercase else c.label
        r, g, b = c.red, c.green, c.blue
        """
        等价于
        if c.alpha < 0.0:
            a = 0.0
        elif c.alpha > 1.0:
            a = 1.0
        else:
            a = c.alpha
        """
        a = max(0.0, min(1.0, c.alpha))

        color = f"rgba({r}, {g}, {b}, {a})"

        self.preview_label.setText(display)
        self.preview_label.setStyleSheet(
            f"font-size: 24px; font-weight: bold; border: 2px solid #ccc; border-radius: 8px;"
            f"color: {color}; background-color: rgba({r},{g},{b},0.2);"
        )
        self.info_label.setText(f"颜色: RGB({r},{g},{b})  Alpha: {a:.2f}  |  大写: {c.uppercase}")

    def _reset_defaults(self):
        defaults = {
            "red": 128,
            "green": 128,
            "blue": 128,
            "alpha": 1.0,
            "label": "示例文字",
            "uppercase": False,
        }
        for name, value in defaults.items():
            setattr(self.config, name, value)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()


"""
它们是互补关系:
输入控件归 BindingManager 管理，
预览区走 observe 回调，两者操作的是完全不同的控件。
缺少任何一个都会导致窗口打开时对应区域显示不正确。
"""