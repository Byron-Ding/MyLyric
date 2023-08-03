from typing import Optional, Pattern, Self
from collections import UserList

from .Lyric_Time_tab import Lyric_Time_tab
from .Lyric_character import Lyric_character
import re


class Lyric_line_content(UserList):
    """
    歌词行内容类
    接受字符串，预先分割
    根据时间，字符，时间，字符，时间，字符 匹配
    分离每个时间，和字符
    如果该字符没有时间，则填None
    然后，将每个时间和字符组合成一个Lrc_character对象
    最后，将每个Lrc_character对象添加到有序字典中，以字符为键，读音（振假名用）为值
    有宽松匹配模式，还有严格匹配模式
    [[Lrc_char obj, [[读音]， 2]], # 2表示显示，两个字符一个读音
    [Lrc_char obj, [""， None]], # None表示前面有读音，是多个字符一个读音
    [Lrc_char obj, [[读音]， 1]] # 1表示显示字符长度个读音
    [Lrc_char obj, [[Any str]， 0]] # 0表示不显示
    没有pronunciation直接None，防止无限递归
    ...
    ]
    读音是一个列表，因为一个字符可能有多个读音，用Lrc_character对象储存（可以包含时间）
    读音也可以填入Lrc_character(None)，表示不显示东西
    """

    def __init__(self, line: str,
                 pronunciation_list: Optional[list[Optional[Self], int]] = None,
                 separation_mode: str = "normal"):
        # 有序字典，超类重写
        super().__init__()

        self.pronunciation_list = pronunciation_list
        self.original_line: str = line

        # 预分离字符串
        self._time_char_list: list[list[str, str]] = Lyric_line_content.split_line_to_time_and_char(line,
                                                                                                    separation_mode)
        # 时间字符对象列表
        self.time_char_object_list: list[Lyric_character] = []

        # 先转为Time_tab对象
        # 再转为Lrc_character对象
        # 再添加到有序字典中
        for time_char in self._time_char_list:
            each_time_tab_object: Lyric_Time_tab = Lyric_Time_tab(time_char[0],
                                                                  separation_mode)

            each_char_object: Lyric_character = Lyric_character(time_char[1],
                                                                each_time_tab_object)

            self.time_char_object_list.append(each_char_object)

        self.data = self.time_char_object_list

        # 读音列表
        self.update_pronunciation_list(pronunciation_list)


    def __add__(self, other):
        if isinstance(other, Lyric_line_content):
            # 判断是否有发音列表
            if self.pronunciation_list is None and other.pronunciation_list is None:
                return Lyric_line_content(self.original_line + other.original_line, None)
            elif self.pronunciation_list is None:
                return Lyric_line_content(self.original_line + other.original_line, other.pronunciation_list)
            elif other.pronunciation_list is None:
                return Lyric_line_content(self.original_line + other.original_line, self.pronunciation_list)
            else:
                return Lyric_line_content(self.original_line + other.original_line,
                                          self.pronunciation_list.append(other.pronunciation_list))

        elif isinstance(other, str):
            return Lyric_line_content(self.original_line + other, self.pronunciation_list.append(["", 0]))

        else:
            raise TypeError("Unsupported operand type(s) for +: 'Lyric_line_content' and '{}'".format(type(other)))

    def __radd__(self, other):
        if isinstance(other, str):
            return Lyric_line_content(other + self.original_line, self.pronunciation_list.append(["", 0]))

        else:
            raise TypeError("Unsupported operand type(s) for +: 'Lyric_line_content' and '{}'".format(type(other)))

    def __str__(self):
        return self.original_line

    def __repr__(self):
        return self.original_line

    def isspace(self):
        return self.original_line.isspace()

    """
    对应发音和自身字符
    """
    def update_pronunciation_list(self, pronunciation_list) -> Self:
        # 更新发音列表
        # None表示全段没有读音
        self.pronunciation_list: Optional[
            list[
                Optional[Self],
                Optional[int]
            ]
        ] = pronunciation_list

        # 验错区
        # 开始对应发音（振假名）和字符
        # 如果没有发音，则填入None
        # 但是先检查列表是否等长，如果不等长，就报错
        if self.pronunciation_list is not None:
            if len(self.pronunciation_list) != len(self.time_char_object_list):
                raise ValueError("Length of pronunciation_list and time_char_object_list are not equal")

            # 测试合法性
            elif self.check_pronunciation_list_validity() is False:
                raise ValueError("Invalid pronunciation_list")

        # 处理区
        # 对应发音和字符
        if self.pronunciation_list is None:
            # 初始化
            self.pronunciation_list = []
            # 循环字符对象列表
            for each_char_object in self.time_char_object_list:
                # print(each_char_object)
                # 对应字符和发音
                self.pronunciation_list.append(["", 0])
        else:
            # 直接对应
            self.pronunciation_list = self.pronunciation_list

        return self

    """
    格式：
    [[Self,  2], # 2表示显示，两个字符一个读音
    [Self,  None], # None表示前面有读音，是多个字符一个读音
    [Self,  1],# 1表示显示字符长度个读音
    [Self， 0]] # 0表示不显示
    测试完毕
    """
    @staticmethod
    def check_pronunciation_list_validity_staticmethod(pronunciation_list: list[Optional[Self], int]) -> bool:
        """
        检查是否符合格式：
        [[Self,  2], # 2表示显示，两个字符一个读音
        [Self,  None], # None表示前面有读音，是多个字符一个读音
        [Self,  1],# 1表示显示字符长度个读音
        [Self， 0]] # 0表示不显示

        :param pronunciation_list: 读音列表
        :return: 是否合法
        """
        # 如果列表为空，返回False
        if not pronunciation_list:
            return False

        # 遍历列表中的每一项
        for i, item in enumerate(pronunciation_list):
            # 如果项不是一个长度为2的列表，返回False
            if not isinstance(item, list) or len(item) != 2:
                return False

            # 如果项的第一个元素不是Lyric_line_content，返回False
            if not isinstance(item[0], Lyric_line_content):
                return False

            # 如果项的第二个元素不是一个整数或None，返回False
            if not isinstance(item[1], (int, type(None))):
                return False

            # 如果项的第二个元素是负数或大于剩余列表长度，返回False
            if (item[1] is not None) and (item[1] < 0 or item[1] > len(pronunciation_list) - i - 1):
                return False

            # 如果项的第二个元素大于1，表示占用了后面的字符，检查后面的字符是否为[Self, None]或[None, None]
            # 0 表示不显示
            if (item[1] is not None) and (item[1] > 1):
                for j in range(i + 1, i + item[1]):
                    if not (isinstance(pronunciation_list[j][0], Lyric_line_content)
                            and pronunciation_list[j][1] is None):
                        return False

            # 如果项的第二个元素是0，表示不显示，跳过后续检查
            if item[1] == 0:
                continue

        # 如果所有项都通过了检查，返回True
        return True

    """
    实例方法
    """
    def check_pronunciation_list_validity(self) -> bool:
        """
        检查是否符合格式：
        [[Self,  2], # 2表示显示，两个字符一个读音
        [Self,  None], # None表示前面有读音，是多个字符一个读音
        [Self,  1],# 1表示显示字符长度个读音
        [Self， 0]] # 0表示不显示

        :return: 是否合法
        """
        return Lyric_line_content.check_pronunciation_list_validity_staticmethod(self.pronunciation_list)


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

        # 如果最后一个匹配的结束位置是字符串的末尾，说明最后一个匹配之后没有其他字符，用""代替表示 空字符串
        else:
            result.append([current_time_tag, ""])

        return result

    """
    将日语kana标签转换为发音列表
    """

    """
    character_indexes: list[list[str | Self, int]] 字符，索引
    character_pronunciations: list[list[str, int]] 字符发音，占用长度
    length: int 总长度
    """
    @staticmethod
    def extend_pronunciation_list(character_indexes: list[list[str | Self, int]],
                                  character_pronunciations: list[list[str, int]],
                                  length: int) -> list[list[Self | int], Optional[int]]:

        # 提取所有索引, 不考虑乱序
        character_indexes_only: list[int] = [character_index[1] for character_index in character_indexes]
        # 判断是否有重复的index，判断是否有index超出范围，判断是否等长
        if len(character_indexes) != sum(character_indexes_only):
            raise ValueError("character_indexes and character_pronunciations must have the same length")
        elif len(set([character_index[1] for character_index in character_indexes])) != len(character_indexes):
            raise ValueError("character_indexes must not have duplicate indexes")
        elif max([character_index[1] for character_index in character_indexes]) >= length:
            raise ValueError("character_indexes must not have index out of range")

        # 初始化
        output_complete_pronunciation_list: list[Self, int] = []

        # 没有发音的默认情况
        no_pronunciation_character = ["", 0]
        # 被占位的情况
        occupied_pronunciation_character = ["", None]

        time_jump: int = 0

        for char_index in range(length):

            # 表示被占用
            if time_jump != 0:
                time_jump -= 1
                # append 被占用的情况
                output_complete_pronunciation_list.append(occupied_pronunciation_character)
                continue

            # 初始化
            # 依次 对号入座
            if char_index == character_indexes_only[0]:
                each_character_pronunciation: list[str, int] = character_pronunciations[0]

                # 设置之后的 n-1（本字符已经添加） 被占位
                time_jump: int = each_character_pronunciation[1] - 1

                # append 一般字符
                output_complete_pronunciation_list.append(each_character_pronunciation)

            # 另外，就是没有发音
            else:
                output_complete_pronunciation_list.append(no_pronunciation_character)

        return output_complete_pronunciation_list




    '''
    利用方法Lyric_character。is_chinese_or_chu_nom_or_chinese_radical_staticmethod
    获取一行中所有的汉字，喃字，以及位置，返回一个列表
    '''

    @staticmethod
    def get_all_chinese_and_chu_nom_and_chinese_radical_staticmethod(line: str) -> list[list[str, int]]:
        """
        获取一行中所有的汉字，喃字，以及位置，返回一个列表
        Get all Chinese characters, Chu Nom characters, and their positions in a line, and return a list

        :param line: 一行歌词 A line of lyrics
        :return: 一个列表，列表中的每个元素都是一个列表，列表中的第一个元素是汉字或者喃字，第二个元素是汉字或者喃字的位置
         A list, each element in the list is a list,
         the first element in the list is a Chinese character or Chu Nom character,
         and the second element is the position of the Chinese character or Chu Nom character

        :rtype: list[list[str, int]]
        """

        # 初始化结果列表
        result = []
        # 逐字检查
        for index, char in enumerate(line):
            # 如果是汉字或者喃字，那么添加到结果列表中
            if Lyric_character.is_chinese_or_chu_nom_or_chinese_radical_staticmethod(char):
                result.append([char, index])

        # 返回结果
        return result

    '''
    利用方法Lyric_character。is_chinese_or_chu_nom_or_chinese_radical_staticmethod
    获取一行中所有的汉字，喃字，以及位置，返回一个列表
    利用自身的静态方法
    '''

    def get_all_chinese_and_chu_nom_and_chinese_radical(self):
        """
        获取一行中所有的汉字，喃字，以及位置，返回一个列表
        Get all Chinese characters, Chu Nom characters, and their positions in a line, and return a list

        :return: 一个列表，列表中的每个元素都是一个列表，列表中的第一个元素是汉字或者喃字，第二个元素是汉字或者喃字的位置
         A list, each element in the list is a list,
         the first element in the list is a Chinese character or Chu Nom character,
         and the second element is the position of the Chinese character or Chu Nom character

        :rtype: list[list[str, int]]
        """

        # 初始化结果列表
        result: list[list[str, int]] = []

        # 提取字符串
        for index, character in enumerate(self):
            if Lyric_character.is_chinese_or_chu_nom_or_chinese_radical_staticmethod(str(character)):
                result.append([character, index])

        return result

    def format_content(self,
                       len_of_millisecond_output: int = 2,
                       seperator: tuple[str, str] = (":", "."),
                       bracket: tuple[str, str] = ("<", ">")
                       ) -> str:
        output_str: str = ""
        for each_lyric_character in self:
            each_lyric_character: Lyric_character

            each_time_tab = each_lyric_character.time_tab
            each_time_tab_str = each_time_tab.convert_to_time_tab(len_of_millisecond_output=len_of_millisecond_output,
                                                                  seperator=seperator,
                                                                  brackets=bracket)

            output_str += (str(each_time_tab_str) + str(each_lyric_character))

        return output_str


if __name__ == '__main__':
    # test_str: str = " <00:0.0>あ <00:01:000>い <00:02:000>う <00:03:000>え <00:04:000>お1 <00:04:000>"
    # print(Lyric_line_content.split_line_to_time_and_char(test_str, "strict"))
    # print(Lyric_line_content.split_line_to_time_and_char(test_str, "normal"))
    # print(Lyric_line_content.split_line_to_time_and_char(test_str, "loose"))
    # print(Lyric_line_content.split_line_to_time_and_char(test_str, "very_loose"))

    # 测试Lyric_line_content.get_all_chinese_and_chu_nom_and_chinese_radical
    test_str: str = " <00:0.0>あNi你他 <00:01:000>い  <00:02:000>う <00:03:000>え <00:04:000>お1 <00:04:000>"
    Lrc_line_content_obj = Lyric_line_content(test_str, separation_mode="very_loose")
    print(Lrc_line_content_obj.get_all_chinese_and_chu_nom_and_chinese_radical())
    print(Lrc_line_content_obj.time_char_object_list)
    print(Lrc_line_content_obj.pronunciation_list)

    # 测试加法
    # print(a := Lyric_line_content("a") + Lyric_line_content("b"))

    # print(a["a"])

    c = Lyric_line_content("")
    print(c.time_char_object_list)
    print(c.pronunciation_list)
    print(c.data)
    output = Lrc_line_content_obj.format_content()
    print(output)