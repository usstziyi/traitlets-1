# PySide6 + Traitlets 学习教程

一套由浅入深的 Demo，帮助你掌握如何将 **traitlets** 的属性管理能力与 **PySide6** 的 UI 控件结合，构建健壮、可维护的桌面应用。

## 环境要求

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) (Python 包管理器)

## 快速开始

```bash
# 安装依赖
uv sync

# 运行命令行 Demo
python3 demos/demo1_traitlets_basics.py
python3 demos/demo2_observe.py

# 运行 GUI Demo
python3 demos/demo3_pyside6_basic.py
python3 demos/demo4_two_way_binding.py
python3 demos/demo5_settings_panel.py
```

## 教程大纲

| Demo | 主题 | 核心知识点 |
|------|------|-----------|
| Demo 1 | Traitlets 基础 | `HasTraits`, 基本 trait 类型 (`Int`/`Float`/`Unicode`/`Bool`/`Enum`/`List`/`Dict`), 类型检查, `read_only`, `allow_none`, trait 元数据 (`trait_names`, `traits`, `tag`) |
| Demo 2 | 观察者与校验 | `@observe` 监听属性变化, `@validate` 自定义校验与值修正, `hold_trait_notifications()` 批量更新 |
| Demo 3 | 控件基础绑定 | `QLineEdit`/`QSpinBox`/`QDoubleSpinBox`/`QComboBox`/`QCheckBox` 与 traits 的手动双向同步 |
| Demo 4 | 自动双向绑定 | 封装通用 `BindingManager`, 实现控件值与 traits 自动同步, 滑块与数值框联动 |
| Demo 5 | JSON 配置持久化 | 完整设置面板, `to_dict()`/`from_dict()`, `to_json()`/`from_json()`, 启动自动加载, 关闭前保存提醒 |

## 核心概念

### Traitlets 是什么？

[Traitlets](https://traitlets.readthedocs.io/) 是一个 Python 库，提供了：

- **类型检查** — 属性赋值时自动校验类型
- **默认值** — 支持静态和动态默认值
- **观察者模式** — 属性变化时自动通知
- **验证与转换** — 自定义校验逻辑和值修正

### 为什么结合 PySide6？

```
┌──────────────────────────────────────────────┐
│                  AppSettings                 │
│              (HasTraits 子类)                │
│                                              │
│  window_title  ←──→  QLineEdit              │
│  window_width  ←──→  QSpinBox + QSlider     │
│  theme         ←──→  QComboBox              │
│  auto_login    ←──→  QCheckBox              │
│  shortcuts     ←──→  QTextEdit (JSON)       │
│                                              │
│  to_json() / from_json()  ←──→  settings.json│
└──────────────────────────────────────────────┘
```

Traitlets 管理**所有业务逻辑状态**（类型校验、默认值、验证规则），PySide6 只负责**界面展示和用户交互**。两者通过观察者模式自动同步。

## 项目结构

```
traitlets-1/
├── pyproject.toml                 # uv 项目配置
├── README.md                      # 本文件
└── demos/
    ├── __init__.py
    ├── demo1_traitlets_basics.py  # Demo 1: Traitlets 基础
    ├── demo2_observe.py           # Demo 2: 观察者与校验
    ├── demo3_pyside6_basic.py     # Demo 3: 控件基础绑定
    ├── demo4_two_way_binding.py   # Demo 4: 自动双向绑定
    └── demo5_settings_panel.py    # Demo 5: JSON 配置持久化
```

## 参考资料

- [Traitlets 官方文档](https://traitlets.readthedocs.io/)
- [PySide6 官方文档](https://doc.qt.io/qtforpython-6/)
- [Traitlets GitHub](https://github.com/ipython/traitlets)

---

<p align="right"><em>Built with ❤️ by SOLO</em></p>
