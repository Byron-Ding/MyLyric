from typing import Optional, Pattern, List
from collections import OrderedDict
from Lyric_Time_tab import Lyric_Time_tab
from Lyric_character import Lyric_character
import re


class Lyric_line_content(OrderedDict):
    """
    歌词行内容类
    接受字符串，预先分割
    根据时间，字符，时间，字符，时间，字符 匹配
    分离每个时间，和字符
    如果该字符没有时间，则填None
    然后，将每个时间和字符组合成一个Lrc_character对象
    最后，将每个Lrc_character对象添加到有序字典中，以字符为键，读音（振假名用）为值
    有宽松匹配模式，还有严格匹配模式
    [[Lrc_char obj, [[读音]， 对应的字符长度]],
    Lrc_char obj, [[读音]， 长对应的字符度]],
    Lrc_char obj, [[读音]， 对应的字符长度]]
    ...
    ]
    读音是一个列表，因为一个字符可能有多个读音，用Lrc_character对象储存（可以包含时间）
    读音也可以填入Lrc_character(None)，表示不显示东西
    """

    def __init__(self, line: str,
                 pronunciation_list: Optional[list[Optional[list[Lyric_character]], int]] = None,
                 separation_mode: str = "normal"):
        # 有序字典，超类重写
        super().__init__()

        # 预分离字符串
        self._time_char_list: list[list[str, str]] = Lyric_line_content.split_line_to_time_and_char(line,
                                                                                                   separation_mode)
        # 时间字符对象列表
        self.time_char_object_list: list[Lyric_character] = []
        # 读音列表
        self.pronunciation_list: Optional[
            list[
                Optional[list[Lyric_character]],
                Optional[int]
            ]
        ] = pronunciation_list if pronunciation_list is not None\
            else Lyric_line_content.extend_pronunciation_list(
            pronunciation_list)

        # 先转为Time_tab对象
        # 再转为Lrc_character对象
        # 再添加到有序字典中
        for time_char in self._time_char_list:
            each_time_tab_object: Lyric_Time_tab = Lyric_Time_tab(time_char[0],
                                                                  separation_mode)

            each_char_object: Lyric_character = Lyric_character(time_char[1],
                                                                each_time_tab_object)

            self.time_char_object_list.append(each_char_object)

        # 开始对应发音（振假名）和字符
        # 如果没有发音，则填入None
        # 但是先检查列表是否等长，如果不等长，就报错
        if len(pronunciation_list) != len(self.time_char_object_list):
            raise ValueError("Length of pronunciation_list and time_char_object_list are not equal")

        # 循环发音列表
        for index in range(len(pronunciation_list)):
            # 对应字符和发音
            self[self.time_char_object_list[index]] = pronunciation_list[index]

    """
    预分离字符串
    输入格式：时间+字符串+时间+字符串+时间+字符串...
    返回格式：[[时间， 单个字符], [时间， 单个字符], [时间， 单个字符]...]
    没有时间的字符，时间填None，没有字符的时间，字符填None
    """
    @staticmethod
    def split_line_to_time_and_char(line: str,
                                    separation_mode: str = "strict"
                                    ) -> list[list[str, str]]:
        """
        预分离字符串
        输入格式：时间+字符串+时间+字符串+时间+字符串...
        返回格式：[[时间， 单个字符], [时间， 单个字符], [时间， 单个字符]...]
        没有时间的字符，时间填None，没有字符的时间，字符填None

        :param line: 字符串
        :param separation_mode: 分离模式
        :return: 分离后的字符串列表
        """

        SEPARATION_PATTERN: Pattern

        # 严格模式 根据Time_tab类的正则表达式分离
        if separation_mode == "strict":
            SEPARATION_PATTERN = Lyric_Time_tab.TIME_TAB_EACH_WORD_STRICT_REGREX

        # 普通模式 根据Time_tab类的正则表达式分离
        elif separation_mode == "normal":
            SEPARATION_PATTERN = Lyric_Time_tab.TIME_TAB_EACH_WORD_NORMAL_REGREX

        # 宽松模式 根据Time_tab类的正则表达式分离
        elif separation_mode == "loose":
            SEPARATION_PATTERN = Lyric_Time_tab.TIME_TAB_EACH_WORD_LOOSE_REGREX

        # 非常宽松模式 根据Time_tab类的正则表达式分离
        elif separation_mode == "very_loose":
            SEPARATION_PATTERN = Lyric_Time_tab.TIME_TAB_EACH_WORD_VERY_LOOSE_REGREX

        # 输入不合法
        else:
            raise ValueError("separation_mode must be strict, normal, loose or very_loose")

        # 初始化结果列表
        result: list[list[str, str]] = []

        # 初始化上一个匹配的结束位置为 0
        prev_end = 0

        # 初始化当前时间标签为 None
        current_time_tag = None

        # 使用正则表达式匹配时间标签和字符
        for matched_char_time_tab in re.finditer(SEPARATION_PATTERN, line):
            # 获取匹配的起始和结束位置
            start, end = matched_char_time_tab.span()

            result.append([current_time_tag, line[prev_end]])

            # 如果匹配的起始位置大于上一个匹配的结束位置，说明两个匹配之间有其他字符
            if start > (prev_end + 1):
                for char in line[prev_end + 1:start]:
                    result.append([None, char])

            # 更新当前时间标签
            current_time_tag = matched_char_time_tab.group()

            # 更新上一个匹配的结束位置
            prev_end = end

        # 如果最后一个匹配的结束位置不是字符串的末尾，说明最后一个匹配之后还有其他字符
        if prev_end < len(line):
            result.append([current_time_tag, line[prev_end]])
            # 如果只有一个字符，那么直接添加[时间标签, char]
            if prev_end == (len(line) - 1):
                pass
            # 如果有多个字符，那么添加[时间标签, char]，然后添加[None, char]
            else:
                for char in line[prev_end + 1:]:
                    result.append([None, char])

        # 如果最后一个匹配的结束位置是字符串的末尾，说明最后一个匹配之后没有其他字符
        else:
            result.append([current_time_tag, None])

        return result

    @staticmethod
    def extend_pronunciation_list(pronunciation_list: Optional[
                                                        list[
                                                            Optional[list[Lyric_character]],
                                                            int
                                                            ]
                                                        ],
                                  character_len: int
                                  ) -> list[
                                        Optional[list[Lyric_character]],
                                        int
                                        ]:
        """
        扩展发音列表 到指定长度
        """
        # 长度必须大于0
        if character_len <= 0:
            raise ValueError("character_len must be greater than or equal to 0")


        # 如果是None，那么直接返回 [[None, 0], .....]
        if pronunciation_list is None:
            return [[None, 0] for _ in range(character_len)]

        # 其他情况
        else:
            # 检查长度是否相等，
            if sum([i[1] for i in pronunciation_list]) == character_len:
                return pronunciation_list
            # 如果长度小于
            elif sum([i[1] for i in pronunciation_list]) < character_len:
                # 计算差值
                difference = character_len - sum([i[1] for i in pronunciation_list])
                # 找到第一个None
                for index, i in enumerate(pronunciation_list):
                    if i[0] is None:
                        # 将None替换为[None, 1]
                        pronunciation_list[index] = [None, 1]
                        # 将差值减1
                        difference -= 1
                        # 如果差值为0，那么结束循环
                        if difference == 0:
                            break
                # 返回结果
                return pronunciation_list
            # 如果长度大于
            else:
                # 提示错误
                raise ValueError("character_len must be greater than or equal to the length of pronunciation_list")



if __name__ == '__main__':
    test_str: str = " <00:0.0>あ <00:01:000>い <00:02:000>う <00:03:000>え <00:04:000>お1 <00:04:000>"
    print(Lyric_line_content.split_line_to_time_and_char(test_str, "strict"))
    print(Lyric_line_content.split_line_to_time_and_char(test_str, "normal"))
    print(Lyric_line_content.split_line_to_time_and_char(test_str, "loose"))
    print(Lyric_line_content.split_line_to_time_and_char(test_str, "very_loose"))
