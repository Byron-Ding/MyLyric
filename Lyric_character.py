from collections import UserString
from Lyric_Time_tab import Lyric_Time_tab
from typing import Optional, Union

"""
每个字符的类，继承自字符串类，
包含时间和字符
"""


class Lyric_character(UserString):

    # CJKV 汉字字符集Unicode编码范围
    # 汉字和喃字的 Unicode 区间
    CHINESE_OR_CHU_NOM_RANGES: list[tuple[int, int]] = [
        (0x2E80, 0x2EFF),  # CJK 部首补充
        (0x2F00, 0x2FDF),  # 康熙部首
        (0x3007, 0x3007),  # 〇
        (0x3400, 0x4DBF),  # CJK 统一表意符号扩展 A
        (0x4E00, 0x9FFF),  # CJK 统一表意符号
        (0xF900, 0xFAFF),  # CJK 兼容表意符号
        (0x20000, 0x2A6DF),  # CJK 统一表意符号扩展 B
        (0x2A700, 0x2B73F),  # CJK 统一表意符号扩展 C
        (0x2B740, 0x2B81F),  # CJK 统一表意符号扩展 D
        (0x2B820, 0x2CEAF),  # CJK 统一表意符号扩展 E
        (0x2CEB0, 0x2EBEF),  # CJK 统一表意符号扩展 F
        (0xAA60, 0xAA7F)  # 喃字补充
    ]

    """
    重写init，添加时间属性
    """

    def __init__(self, character: str, time_tab: Optional[Lyric_Time_tab] = None):
        super().__init__(character)

        # 时间
        # 调用Time_tab类
        self.global_time_tab: Optional[Lyric_Time_tab] = time_tab

    @staticmethod
    def is_chinese_or_chu_nom_or_chinese_radical_staticmethod(single_character: str) -> bool:
        char_code: int = ord(single_character)  # 获取字符的 Unicode 编码

        start: int
        end: int
        for start, end in Lyric_character.CHINESE_OR_CHU_NOM_RANGES:
            if start <= char_code <= end:  # 判断字符编码是否在汉字或喃字的 Unicode 区间内
                return True  # 如果在区间内，返回 True
        return False  # 如果不在任何区间内，返回 False

    # 非静态方法
    def is_chinese_or_chu_nom_or_chinese_radical(self) -> bool:
        return Lyric_character.is_chinese_or_chu_nom_or_chinese_radical_staticmethod(self.data)



# 测试
if __name__ == '__main__':
    a_time_tab = Lyric_Time_tab("<00:00.50>", "strict")

    a = Lyric_character('a', a_time_tab)
    print(a)
    print(a.global_time_tab)
    print(a.data)
