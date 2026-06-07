"""
=============================================================================
Demo 1: Traitlets 基础 —— HasTraits 与基本 Trait 类型
=============================================================================

学习目标:
  1. 理解 HasTraits 作为属性管理基类的作用
  2. 掌握常用 Trait 类型: Int, Float, Unicode, Bool, Enum, List, Dict
  3. 理解类型检查、默认值、read_only、allow_none
  4. 了解 trait_names(), traits(), has_trait(), tag() 等元数据方法

运行方式: python demos/demo1_traitlets_basics.py
"""

from traitlets import (
    HasTraits,
    Int,
    Float,
    Unicode,
    Bool,
    Enum,
    List,
    Dict,
    default,
    TraitError,
)


class Person(HasTraits):
    name = Unicode("未命名", help="姓名")
    age = Int(18, help="年龄")
    height = Float(1.70, help="身高（米）")
    is_student = Bool(True, help="是否为学生")
    gender = Enum(["男", "女", "其他"], default_value="男", help="性别")
    hobbies = List(Unicode(), default_value=[], help="爱好列表")
    scores = Dict(key_trait=Unicode(), value_trait=Float(), help="各科成绩")
    nickname = Unicode(allow_none=True, default_value=None, help="昵称（可选）")
    id_number = Unicode(read_only=True, help="身份证号（只读）")

    @default("id_number")
    def _default_id_number(self):
        return "未设置"


def main():
    print("=" * 60)
    print("Demo 1: Traitlets 基础")
    print("=" * 60)

    person = Person(name="小明", age=20, height=1.75)

    print("\n--- 1. 基本属性访问 ---")
    print(f"姓名: {person.name}")
    print(f"年龄: {person.age}")
    print(f"身高: {person.height}")
    print(f"是否学生: {person.is_student}")
    print(f"性别: {person.gender}")
    print(f"昵称: {person.nickname}")
    print(f"身份证号(只读): {person.id_number}")

    print("\n--- 2. 类型检查 ---")
    try:
        person.age = "不是数字"
    except TraitError as e:
        print(f"类型错误: {e}")

    print("\n--- 3. read_only 保护 ---")
    try:
        person.id_number = "123456"
    except TraitError as e:
        print(f"只读保护: {e}")

    print("\n--- 4. Enum 枚举约束 ---")
    try:
        person.gender = "未知"
    except TraitError as e:
        print(f"枚举约束: {e}")

    print("\n--- 5. List 和 Dict 容器 ---")
    person.hobbies = ["篮球", "编程", "阅读"]
    print(f"爱好: {person.hobbies}")

    person.scores = {"数学": 95.5, "语文": 88.0, "英语": 92.5}
    print(f"成绩: {person.scores}")

    try:
        person.hobbies = [1, 2, 3]
    except TraitError as e:
        print(f"List 类型约束: {e}")

    print("\n--- 6. trait_names() —— 获取所有 trait 名称 ---")
    print(person.trait_names())

    print("\n--- 7. traits() —— 获取 trait 元数据 ---")
    for name, trait in person.traits().items():
        print(f"  {name:15s} 类型={trait.__class__.__name__:10s}  help={trait.help}")

    print("\n--- 8. has_trait() 和 trait_has_value() ---")
    print(f"has_trait('name'): {person.has_trait('name')}")
    print(f"has_trait('不存在的属性'): {person.has_trait('不存在的属性')}")
    print(f"name has value: {person.trait_has_value('name')}")
    print(f"nickname has value: {person.trait_has_value('nickname')}")

    print("\n--- 9. tag() 元数据标记 ---")
    scores_trait = person.traits()["scores"]
    scores_trait.tag(config=True, sync=True)
    metadata = person.trait_metadata("scores", "config")
    print(f"scores.config = {metadata}")

    print("\n✅ Demo 1 完成!")


if __name__ == "__main__":
    main()
