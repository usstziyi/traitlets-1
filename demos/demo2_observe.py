"""
=============================================================================
Demo 2: Traitlets 观察者模式 —— @observe 与 @validate
=============================================================================

学习目标:
  1. 使用 @observe 装饰器监听 trait 属性变化
  2. 使用 @validate 装饰器进行自定义校验与值转换
  3. 使用 hold_trait_notifications 批量修改并保持一致性

运行方式: python demos/demo2_observe.py
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
    validate,
    TraitError,
)


class Thermostat(HasTraits):
    target_temp = Float(26.0, help="目标温度（摄氏度）")
    current_temp = Float(25.0, help="当前温度（摄氏度）")
    mode = Enum(["制冷", "制热", "关闭"], default_value="关闭", help="工作模式")
    power = Bool(False, help="是否开机")
    fan_speed = Int(3, help="风扇档位 (1-5)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._change_log = []

    @observe("target_temp")
    def _on_target_temp_changed(self, change):
        print(f"  [监听] 目标温度: {change['old']} -> {change['new']}")

    @observe("power")
    def _on_power_changed(self, change):
        state = "开机" if change["new"] else "关机"
        print(f"  [监听] 电源: {state}")

    @observe("mode")
    def _on_mode_changed(self, change):
        print(f"  [监听] 模式: {change['old']} -> {change['new']}")

    @validate("target_temp")
    def _validate_target_temp(self, proposal):
        value = proposal["value"]
        if value < 16.0:
            raise TraitError("目标温度不能低于 16°C")
        if value > 30.0:
            raise TraitError("目标温度不能高于 30°C")
        return value

    @validate("fan_speed")
    def _validate_fan_speed(self, proposal):
        value = proposal["value"]
        if value < 1:
            return 1
        if value > 5:
            return 5
        return value

    @observe("current_temp", "target_temp")
    def _on_temp_changed(self, change):
        if self.power and self.target_temp != self.current_temp:
            print(f"  [监听] 温差 = {abs(self.target_temp - self.current_temp):.1f}°C")


def main():
    print("=" * 60)
    print("Demo 2: Traitlets 观察者模式")
    print("=" * 60)

    t = Thermostat()

    print("\n--- 1. @observe 监听单个 trait ---")
    print("设置目标温度为 28°C:")
    t.target_temp = 28.0

    print("\n设置电源为 True:")
    t.power = True

    print("\n--- 2. @observe 监听多个 trait ---")
    print("更新当前温度为 28°C (温差归零):")
    t.current_temp = 28.0

    print("\n--- 3. @validate 校验 ---")
    try:
        t.target_temp = 10.0
    except TraitError as e:
        print(f"  校验失败: {e}")

    try:
        t.target_temp = 35.0
    except TraitError as e:
        print(f"  校验失败: {e}")

    print("\n--- 4. @validate 值修正 ---")
    print(f"  当前风扇档位: {t.fan_speed}")
    t.fan_speed = 0
    print(f"  设置 0 -> 修正为: {t.fan_speed}")
    t.fan_speed = 10
    print(f"  设置 10 -> 修正为: {t.fan_speed}")

    print("\n--- 5. hold_trait_notifications 批量修改 ---")
    print("批量修改温度和模式（一起切换）:")
    with t.hold_trait_notifications():
        t.mode = "制热"
        t.target_temp = 22.0
    print("  (批量修改完成，只触发一次通知)")

    print("\n--- 6. 模式切换 ---")
    t.mode = "制冷"
    t.target_temp = 24.0

    print("\n✅ Demo 2 完成!")


if __name__ == "__main__":
    main()
