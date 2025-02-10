import math
import warnings
from typing import Optional, Pattern, Self, Union, List, Tuple
from collections import UserList, UserString

from LyricTimeTab import LyricTimeTab
from LyricCharacter import LyricCharacter
import re

from DataTypeInterface import var_type_guard

"""
设计读音字符格式
类似HTML br标签
每一个组一个OriginalCharacter的列表，
读音通过属性获取
每一个组都是一个实际的类
"""


class LyricPronunciationGroup(UserList):
    """
    读音字符组类
    """

    KANA_TAB_REGREX: Pattern[str] = re.compile(
                                               r'(?P<pronunciation>\D*)'
                                               r'(?P<num_of_char>\d+)'
                                            )

    def __init__(self,
                 base_str: list[LyricCharacter] | UserList[LyricCharacter],
                 pronunciation_line_list: list[Self] | UserList[Self] | None = None,
                 ) -> None:
        """
        字符组 对应 读音

        character group corresponds to pronunciation_line_list


        """
        # ========= 备份参数 =========
        # 原始字符串备份
        # 不允许套娃
        self.original_annotated_string: list[LyricCharacter] | UserList[LyricCharacter] = base_str
        super().__init__(base_str)

        # 读音,允许套娃
        # [LyricPronunciationGroup, LyricPronunciationGroup, LyricPronunciationGroup]
        # 但是总列表只对应一个 Base_str
        self._pronunciation_line_list: list[Self] | UserList[Self] | None  = pronunciation_line_list

        self._has_pronunciation: bool = False if pronunciation_line_list is None else True
        self._has_time: bool = False
        for each_char in base_str:
            each_char: LyricCharacter
            if each_char.time_tab is not None:
                self._has_time = True
                break

        # ========= Type Guard 🛡️ =========
        # 如果不是列表，抛出异常
        var_type_guard(base_str, (list, UserList))
        # 如果列表中不是LyricCharacter，抛出异常
        for each_char in base_str:
            var_type_guard(each_char, (LyricCharacter,))

        # pronunciations
        self.pronunciation_type_guard(self)

    def __add__(self, other: Self) -> Self:
        """
        拼接
        """
        var_type_guard(other, (LyricPronunciationGroup,))

        # 考虑 读音 为空的情况
        if self.pronunciation_line_list is None:
            self_pronunciation_line_list = []
        else:
            self_pronunciation_line_list = self.pronunciation_line_list

        if other.pronunciation_line_list is None:
            other_pronunciation_line_list = []
        else:
            other_pronunciation_line_list = other.pronunciation_line_list

        return LyricPronunciationGroup(
            base_str=self.original_annotated_string + other.original_annotated_string,
            pronunciation_line_list=self_pronunciation_line_list + other_pronunciation_line_list
        )

    def __mul__(self, other: int) -> Self:
        """
        重复
        """
        var_type_guard(other, (int,))
        return LyricPronunciationGroup(
            base_str=self.original_annotated_string * other,
            pronunciation_line_list=self.pronunciation_line_list * other
        )


    @property
    def pronunciation_line_list(self) -> Self | None:
        """
        读音
        """
        return self._pronunciation_line_list

    @pronunciation_line_list.setter
    def pronunciation_line_list(self, value: Self | None) -> None:
        self._pronunciation_line_list = value

    @property
    def base_str(self) -> str:
        """
        原始字符串
        """
        return "".join([str(each_char) for each_char in self.data])


    def get_base_str_without_number(self) -> str:
        """
        原始字符串
        """
        return "".join([str(each_char) for each_char in self.data if not each_char.isdigit()])

    @property
    def pronunciation(self) -> str:
        """
        读音
        """
        return "" if self._pronunciation_line_list is None\
            else "".join([each_char.base_str for each_char in self._pronunciation_line_list])
            # base str of the 2nd pronunciation


    def get_pronunciation_without_number(self) -> str:
        """
        读音
        """
        return "" if self._pronunciation_line_list is None\
            else "".join([str(each_char) for each_char in self._pronunciation_line_list if not each_char.isdigit()])

    def get_plain_text_format_base_on_inner_parm(self,
                                                 max_recursion_depth: Optional[int] = None,
                                                 current_layer: int = 0
                                                 ) -> str:
        """
        返回 歌词(读音) 根据自带的参数

        Return Lyric(Reading) based on the inner parameters

        :param max_recursion_depth: 最大递归深度
        :param current_layer: 当前递归层数
        :return: 歌词(读音)
        """

        # 如果有时间，返回 Char + 时间
        base_str: str = ""
        for each_char in self.data:
            if each_char.time_tab is not None:
                each_char: LyricCharacter
                base_str += each_char.get_timed_character(
                    min_len_of_minutes=each_char.time_tab.min_len_of_minutes,
                    min_len_of_seconds=each_char.time_tab.min_len_of_seconds,
                    min_len_of_millisecond=each_char.time_tab.min_len_of_millisecond,
                    cut_off_millisecond=each_char.time_tab.cut_off_millisecond,
                    brackets=each_char.time_tab.brackets,
                    seperator=(each_char.time_tab.minutes_seconds_seperator,
                               each_char.time_tab.seconds_milliseconds_seperator
                               )
                )
            # 无，直接拼接
            else:
                base_str: str = "".join([str(each_char) for each_char in self.data])

        # 需要递归-------------------------
        # 在递归层数内
        if max_recursion_depth is not None and current_layer <= max_recursion_depth:
            # 如果没有读音，返回原始字符串，不带()
            if self.pronunciation_line_list is None:
                # 如果没有读音，返回原始字符串，不带()
                pass
            # 否则递归
            else:
                for each_pronunciation in self.pronunciation_line_list:
                    # 需要读音 则 后带后缀
                    if each_pronunciation.pronunciation_line_list is not None:
                        each_pronunciation: Self
                        # 外(内甲(...)内乙(...)内丙(...)...)
                        base_str += ("("
                                     + each_pronunciation.
                                         get_plain_text_format_base_on_inner_parm(
                                        max_recursion_depth=max_recursion_depth,
                                        current_layer=current_layer + 1
                                    )
                                    + ")"
                                    )
        # 超出递归层数
        else:
            ...

        return base_str
    

    # 递归遍历读音的读音，直到没有读音
    def get_plain_text_format(self,
                              max_recursion_depth: Optional[int] = None,
                              enable_time: bool = True,
                              enable_pronunciation: bool = True,
                              min_len_of_minutes: Optional[Union[int, "math.inf"]] = 2,
                              min_len_of_seconds: Optional[int] = 2,
                              min_len_of_millisecond: Optional[Union[int, "math.inf"]] = 2,
                              cut_off_millisecond: bool = True,
                              brackets: List[str] | Tuple[str, str] = ("<", ">"),
                              seperator: List[str] | Tuple[str, str] = (":", "."),
                              current_layer: int = 0
                              ) -> str:
        """
        返回 歌词(读音)

        Return Lyric(Reading)

        :return: 歌词(读音)
        """

        # 如果有时间，返回 Char + 时间
        if enable_time:
            base_str: str = ""
            for each_char in self.data:
                each_char: LyricCharacter
                base_str += each_char.get_timed_character(
                    min_len_of_minutes=min_len_of_minutes,
                    min_len_of_seconds=min_len_of_seconds,
                    min_len_of_millisecond=min_len_of_millisecond,
                    cut_off_millisecond=cut_off_millisecond,
                    brackets=brackets,
                    seperator=seperator
                )
        # 无，直接拼接
        else:
            base_str: str = "".join([str(each_char) for each_char in self.data])

        # 需要递归-------------------------
        # 需要读音 则 后带后缀
        if enable_pronunciation:
            # 在递归层数内
            if max_recursion_depth is not None and current_layer <= max_recursion_depth:
                # 如果没有读音，返回原始字符串，不带()
                if self.pronunciation_line_list is None:
                    # 如果没有读音，返回原始字符串，不带()
                    pass
                # 否则递归
                else:
                    for each_pronunciation in self.pronunciation_line_list:
                        each_pronunciation: Self
                        # 外(内甲(...)内乙(...)内丙(...)...)
                        base_str += ("("
                                     + each_pronunciation.
                                         get_plain_text_format(
                                        max_recursion_depth=max_recursion_depth,
                                        enable_time=enable_time,
                                        enable_pronunciation=enable_pronunciation,
                                        min_len_of_minutes=min_len_of_minutes,
                                        min_len_of_seconds=min_len_of_seconds,
                                        min_len_of_millisecond=min_len_of_millisecond,
                                        cut_off_millisecond=cut_off_millisecond,
                                        brackets=brackets,
                                        seperator=seperator,
                                        current_layer=current_layer + 1
                                    )
                                    + ")"
                                    )
            # 超出递归层数
            else:
                ...

        return base_str

    def get_plain_text_format_standard(self,
                                       enable_time: bool = True,
                                       enable_pronunciation: bool = True
                                       ) -> str:
        """
        返回 歌词(读音)

        Return Lyric(Reading)

        :return: 歌词(读音)
        """

        return self.get_plain_text_format(
            enable_time=enable_time,
            enable_pronunciation=enable_pronunciation
        )

    @staticmethod
    def pronunciation_type_guard(outer_word: "LyricPronunciationGroup") -> None:
        """
        读音类型检查
        """
        # 如果不是Self，抛出异常
        var_type_guard(outer_word, (LyricPronunciationGroup, None))

        if outer_word.pronunciation_line_list is not None:
            # 忽略类型检查，因为目前不支持Property的类型检查
            # outer_word.pronunciation_line_list: LyricPronunciationGroup
            for each_pronunciation in outer_word.pronunciation_line_list:
                LyricPronunciationGroup.pronunciation_type_guard(each_pronunciation)

    def is_cjkv(self) -> bool:
        """
        判断是否是汉字，日语假名，朝鲜字母，越南喃字
        """
        for each_char in self:
            each_char: LyricCharacter
            if not each_char.is_cjkv():
                break
        else:
            return False

        return True

    def contain_cjkv(self) -> bool:
        """
        判断是否包含汉字，日语假名，朝鲜字母，越南喃字
        """
        for each_char in self:
            each_char: LyricCharacter
            if each_char.is_cjkv():
                return True

        return False

    def count_cjkv(self) -> int:
        """
        计算汉字，日语假名，朝鲜字母，越南喃字的数量
        """
        count = 0
        for each_char in self:
            each_char: LyricCharacter
            if each_char.is_cjkv():
                count += 1

        return count


class LyricLineContent(UserList):
    """
    歌词行内容类
    接受字符串，预先分割
    根据时间，字符，时间，字符，时间，字符 匹配
    分离每个时间，和字符
    如果该字符没有时间，则填None
    然后，将每个时间和字符组合成一个Lrc_character对象
    最后，将每个Lrc_character对象添加到有序字典中，以字符为键，读音（振假名用）为值
    有宽松匹配模式，还有严格匹配模式
    [[[Lrc_char obj, Lrc_char obj], [读音]], # 两个字符一个读音
    [Lrc_char obj, [读音]] # 一个字符一个读音
    [Lrc_char obj, [""] # ""表示不显示

    输入格式：
    [[Self,  2], # 2表示显示，两个字符一个读音
    ["", x], # x表示占用x个字符, "" 没有读音
    None 终止
    [Self,  1],# 1表示显示字符长度个读音
    [Self， 0]] # 0 非法，如果没有读音，填None

    没有pronunciation直接None，防止无限递归
    ...
    ]
    读音是一个列表，因为一个字符可能有多个读音，用Lrc_character对象储存（可以包含时间）
    读音也可以填入Lrc_character(None)，表示不显示东西
    """

    def __init__(self,
                 lyric_base_char_list: UserList[LyricPronunciationGroup] |
                                           list[LyricPronunciationGroup] |
                                           Union[str, UserString],
                 mode: Union[tuple[str, Optional[Pattern[str]]], list[str, Optional[Pattern[str]]]] = ('normal', None)
                 ):

        # ========= Type Guard 🛡️ =========
        # pronunciation_list: list, UserList, None
        self.pronunciation_type_guard(lyric_base_char_list)

        # ========= 备份参数 =========
        if isinstance(lyric_base_char_list, (str, UserString)):
            # 预分离字符串
            self._lyric_char_list: list[LyricCharacter]
            self.whether_extension: bool
            self._lyric_char_list, self.whether_extension \
                = LyricLineContent.split_line_to_time_and_char(line=lyric_base_char_list,
                                                               mode=mode
                                                               )
            # Full - None
            self._lyric_pronunciation_list = [
                LyricPronunciationGroup(base_str=self._lyric_char_list, pronunciation_line_list=None)
            ]
        elif isinstance(lyric_base_char_list, (list, UserList)):
            lyric_base_char_list: list[LyricPronunciationGroup]
            # 字符-读音 列表
            self._lyric_pronunciation_list = lyric_base_char_list
            # 单字符串
            self._lyric_char_list = []
            for group in lyric_base_char_list:
                group: LyricPronunciationGroup
                self._lyric_char_list.append(*group.original_annotated_string)

            # 检查是否有时间
            for each_char in self._lyric_char_list:
                each_char: LyricCharacter
                if each_char.time_tab is not None:
                    self.whether_extension = True
                    break
        else:
            raise ValueError("lyric_base_char_list must be in (list, UserList, str, UserString)")

        # 有序双射列表
        super().__init__(self._lyric_char_list)

    @staticmethod
    def pronunciation_type_guard(pronunciation_list: UserList[LyricPronunciationGroup] |
                                                     list[LyricPronunciationGroup] | Union[str, UserString]
                                 ) -> None:

        # Pronunciation_list
        # list, UserList, None
        var_type_guard(pronunciation_list, (list, UserList, str, UserString))

        # If list/UserList
        if isinstance(pronunciation_list, (list, UserList)):
            # If list/UserList
            for each_pronunciation in pronunciation_list:
                # LyricPronunciationGroup
                var_type_guard(each_pronunciation, (LyricPronunciationGroup,))

    def __str__(self):
        return self.base_str

    def __add__(self, other: Self) -> Self:
        """
        拼接
        """
        var_type_guard(other, (LyricLineContent,))

        # 设置读音（类型为 LyricPronunciationGroup）的时候自动生成了 LyricCharacter 列表
        return LyricLineContent(lyric_base_char_list=self._lyric_pronunciation_list + other._lyric_pronunciation_list)

    def __mul__(self, other: int) -> Self:
        """
        重复
        """
        var_type_guard(other, (int,))
        return LyricLineContent(lyric_base_char_list=self._lyric_pronunciation_list * other)


    @property
    def base_str(self) -> str:
        return "".join([str(char) for char in self._lyric_char_list])

    @property
    def pronunciation(self) -> str:
        return "".join([lyric_pronunciation.pronunciation for lyric_pronunciation in self._lyric_pronunciation_list])

    @property
    def lyric_char_list(self) -> list[LyricCharacter]:
        return self._lyric_char_list

    @lyric_char_list.setter
    def lyric_char_list(self, value: list[LyricCharacter]) -> None:
        # ========= Type Guard 🛡️ =========
        var_type_guard(value, (list, UserList))

        # 设置
        self._lyric_char_list = value

    @property
    def pronunciation_list(self) -> UserList[LyricPronunciationGroup] | list[LyricPronunciationGroup]:
        return self._lyric_pronunciation_list

    @pronunciation_list.setter
    def pronunciation_list(self, value: UserList[LyricPronunciationGroup] | list[LyricPronunciationGroup]) -> None:
        # ========= Type Guard 🛡️ =========
        self.pronunciation_type_guard(value)

        self._lyric_pronunciation_list = value

    """
    预分离字符串
    输入格式：时间+字符串+时间+字符串+时间+字符串...
    返回格式：[[时间， 单个字符], [时间， 单个字符], [时间， 单个字符]...]
    没有时间的字符，时间填None，没有字符的时间，字符填None
    """

    @staticmethod
    def split_line_to_time_and_char(line: str,
                                    mode: tuple[str, Optional[Pattern[str]]] = ('normal', None)
                                    ) -> tuple[list[LyricCharacter], bool]:
        """
        预分离字符串
        输入格式：时间+字符串+时间+字符串+时间+字符串...
        返回格式：[LyricTimeTab, ...]
        没有时间的字符，时间填None，没有字符的时间，字符填None

        :param line: 字符串
        :param mode: 分离模式 (分离模式，自定义正则表达式)
        :return: 分离后的字符串列表
        """

        # ================== 决定分离模式 ==================
        separation_pattern: Pattern

        time_tab_separation_mode, self_defined_pattern = mode
        # 自定义
        if time_tab_separation_mode == "self_defined":
            if self_defined_pattern is None:
                raise ValueError("self_defined_pattern must be specified when separation_mode is self_defined")
            separation_pattern = self_defined_pattern
        # 否则按照默认正则表达式分离
        elif time_tab_separation_mode in LyricTimeTab.MODE_TYPE:
            separation_pattern = LyricTimeTab.TIME_TAB_MODE_REGREX_PAIR[time_tab_separation_mode]
            if self_defined_pattern is not None:
                warnings.warn("self_defined_pattern will be ignored when separation_mode is not self_defined")
        # 不合法
        else:
            raise ValueError("separation_mode must be in LyricTimeTab.MODE_TYPE")

        # ================== 预分离字符串 ==================

        # 初始化结果列表
        result: list[LyricCharacter] = []
        # 初始化上一个匹配的结束位置为 0
        prev_end: int = 0

        extension_mode: bool = False

        # 使用正则表达式匹配时间标签
        for matched_char_time_tab in re.finditer(separation_pattern, line):
            # 有匹配到
            extension_mode = True
            # 获取匹配的起始和结束位置
            start, end = matched_char_time_tab.span()

            # 如果匹配的起始位置大于上一个匹配的结束位置，说明两个匹配之间有其他字符(除了对应字符之外的字符)
            if start >= (prev_end + 1):
                # 是否为第一个句首字符
                if prev_end == 0:
                    # 将句首字符添加到结果列表中
                    for char in line[prev_end:start]:
                        result.append(LyricCharacter(character=char, time_tab=None))
                # 不是句首字符
                else:
                    # 将两个匹配之间的字符添加到结果列表中
                    for char in line[prev_end + 1:start]:
                        result.append(LyricCharacter(character=char, time_tab=None))

            # 更新当前时间标签
            current_time_tag = matched_char_time_tab.group()

            # 查看是否有下一个字符
            if end < len(line):
                char = line[end]
                result.append(LyricCharacter(character=char, time_tab=LyricTimeTab(current_time_tag,
                                                                                   mode=(time_tab_separation_mode,
                                                                                         None))))

            # 更新上一个匹配的结束位置
            prev_end = end


        # 如果最后一个匹配的结束位置不是字符串的末尾(带字符本身)，说明最后一个匹配之后还有其他字符
        if prev_end + 1 < len(line):
            # 如果一个都没匹配，说明整个字符串都是字符，没有时间标签，还在句首
            # 否则，仍然需要排除 <Tab>X 的 X
            if prev_end != 0:
                prev_end += 1
            # 添加最后一个匹配之后的字符
            for char in line[prev_end:]:
                result.append(LyricCharacter(character=char, time_tab=None))
        # 否则，说明最后一个匹配之后没有其他字符
        # 啥也不做
        else:
            pass

        return result, extension_mode

    """
    将日语kana标签转换为发音列表
    """

    def is_empty(self) -> bool:
        """
        判断是否为空
        """
        return self.base_str.isspace()

    '''
    利用方法Lyric_character。is_chinese_or_chu_nom_or_chinese_radical_staticmethod
    获取一行中所有的汉字，喃字，以及位置，返回一个列表
    '''

    @staticmethod
    def get_all_cjkv_static(line: str) -> list[list[str | int]]:
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
            if LyricCharacter.is_cjkv_classmethod(char):
                result.append([char, index])

        # 返回结果
        return result

    '''
    利用方法Lyric_character。is_chinese_or_chu_nom_or_chinese_radical_staticmethod
    获取一行中所有的汉字，喃字，以及位置，返回一个列表
    利用自身的静态方法
    '''

    def get_all_cjkv(self):
        """
        获取一行中所有的汉字，喃字，以及位置，返回一个列表
        Get all Chinese characters, Chu Nom characters, and their positions in a line, and return a list

        :return: 一个列表，列表中的每个元素都是一个列表，列表中的第一个元素是汉字或者喃字，第二个元素是汉字或者喃字的位置
         A list, each element in the list is a list,
         the first element in the list is a Chinese character or Chu Nom character,
         and the second element is the position of the Chinese character or Chu Nom character

        :rtype: list[list[str, int]]
        """

        base_str: list[str] = [str(char) for char in self._lyric_char_list]

        # 初始化结果列表
        result: list[list[str | int]] = self.get_all_cjkv_static("".join(base_str))

        return result

    def get_plain_text_format_base_on_inner_parm(self,
                                                 max_recursion_depth: Optional[int] = None,
                                                 ) -> str:
        """
        返回 歌词(读音) 根据自带的参数

        Return Lyric(Reading) based on the inner parameters

        :param max_recursion_depth: 最大递归深度
        :return: 歌词(读音)
        """

        output_str: str = ""
        for each_pronunciation in self.pronunciation_list:
            each_pronunciation: LyricPronunciationGroup
            output_str += each_pronunciation.get_plain_text_format_base_on_inner_parm(
                max_recursion_depth=max_recursion_depth
            )

        return output_str


    def get_plain_text_format(self,
                              max_recursion_depth: Optional[int] = None,
                              enable_time: bool = True,
                              enable_pronunciation: bool = False,
                              min_len_of_minutes: Optional[Union[int, "math.inf"]] = 2,
                              min_len_of_seconds: Optional[int] = 2,
                              min_len_of_millisecond: Optional[Union[int, "math.inf"]] = 2,
                              cut_off_millisecond: bool = True,
                              seperator: tuple[str, str] = (":", "."),
                              bracket: tuple[str, str] = ("<", ">")
                              ) -> str:
        output_str: str = ""
        for each_pronunciation in self.pronunciation_list:
            each_pronunciation: LyricPronunciationGroup
            output_str += each_pronunciation.get_plain_text_format(
                max_recursion_depth=max_recursion_depth,
                enable_time=enable_time,
                enable_pronunciation=enable_pronunciation,
                min_len_of_minutes=min_len_of_minutes,
                min_len_of_seconds=min_len_of_seconds,
                min_len_of_millisecond=min_len_of_millisecond,
                cut_off_millisecond=cut_off_millisecond,
                brackets=bracket,
                seperator=seperator
            )

        return output_str

    def get_plain_text_format_standard(self,
                                       enable_time: bool = True,
                                       enable_pronunciation: bool = False
                                       ) -> str:
        """
        格式化输出
        """
        return self.get_plain_text_format(enable_time=enable_time, enable_pronunciation=enable_pronunciation)


    def get_kana_tag(self) -> str:
        """
        获取假名标签 形式的字符串，只有一层

        Get kana tag type string with only one layer

        :return: 假名标签
         Kana tag

        :rtype: str
        """
        # 获取读音列表
        pronunciation_list: list[LyricPronunciationGroup] = self._lyric_pronunciation_list

        output_str: str = ""

        # 对于每一个 字符组
        for each_pronunciation in pronunciation_list:
            each_pronunciation: LyricPronunciationGroup
            # 如果有CJKV字符，把读音分配到第一个CJKV字符上
            if each_pronunciation.contain_cjkv():
                # 有读音
                if each_pronunciation.pronunciation_line_list is not None:
                    for each_char in each_pronunciation:
                        each_char: LyricCharacter
                        # 如果是CJKV字符
                        if each_char.is_cjkv():
                            # 读音 + len:=1
                            # 去掉数字，否则会和长度冲突
                            output_str += each_pronunciation.get_base_str_without_number() + "1"
                            break
                    output_str += each_pronunciation.count_cjkv() * "1"

                else:
                    # 无读音
                    output_str += each_pronunciation.count_cjkv() * "1"
            else:
                # 没有CJKV字符，不管
                pass



        return output_str

    def get_pronunciation_by_kana_tag(self,
                                      kana_tag: str
                                      ) -> list[LyricPronunciationGroup]:
        """
        使用假名标签刷新所有读音，原读音将被洗掉

        Refresh all pronunciations with kana tag, the original pronunciation will be washed away
        """

        # iterator Char Num
        kana_tag_iterator = re.finditer(LyricPronunciationGroup.KANA_TAB_REGREX, kana_tag)

        # 获取 LyricCharacter 列表
        lyric_char_list: list[LyricCharacter] = self.lyric_char_list

        lyric_pronunciation_list: list[LyricPronunciationGroup] = []
        each_non_cjkv_char_group: List[LyricCharacter] = []

        for each_character_index, each_character in enumerate(lyric_char_list):
            each_character: LyricCharacter
            # 如果是CJKV字符
            if each_character.is_cjkv():
                # ================== 非CJKV字符 ==================
                # 缓冲区不为空结算
                if each_non_cjkv_char_group:
                    # 生成读音列表
                    lyric_pronunciation_list.append(
                        LyricPronunciationGroup(base_str=each_non_cjkv_char_group,
                                                pronunciation_line_list=None)
                    )
                    # 清空缓冲区
                    each_non_cjkv_char_group = []
                # ================== CJKV ==================
                try:
                    # 获取下一个假名标签
                    kana_tag_match = next(kana_tag_iterator)
                except StopIteration:
                    # 没有下一个假名标签，结束
                    break
                except Exception as e:
                    # 其他错误，照常抛出
                    raise e

                # 获取假名标签
                kana_tag_str = kana_tag_match.group("pronunciation")
                # 获取假名标签中的数字
                kana_tag_num = int(kana_tag_match.group("num_of_char"))

                # 读音
                # 获取 kana_tag_num 个字符
                each_cjkv_char_group: List[LyricCharacter] = lyric_char_list[each_character_index
                                                                             :each_character_index + kana_tag_num]
                # kana_tag_str 转LyricCharacter
                kana_tag_char_group: List[LyricCharacter] = [LyricCharacter(character=char, time_tab=None)
                                                             for char in kana_tag_str]
                # 生成读音
                kana_pronunciation = LyricPronunciationGroup(base_str=kana_tag_char_group,
                                                             pronunciation_line_list=None) # 二级读音

                # 字符 + 读音
                # 组合 CJKV 字符和假名读音
                lyric_pronunciation_list.append(
                    LyricPronunciationGroup(base_str=each_cjkv_char_group,
                                            pronunciation_line_list=[kana_pronunciation])
                )

                # 跳过已经处理的字符
                for _ in range(kana_tag_num - 1):
                    next(kana_tag_iterator)

            else:
                # 加入非CJKV字符缓冲区
                each_non_cjkv_char_group.append(each_character)

        # 缓冲区不为空结算
        if each_non_cjkv_char_group:
            # 生成读音列表
            lyric_pronunciation_list.append(
                LyricPronunciationGroup(base_str=each_non_cjkv_char_group,
                                        pronunciation_line_list=None)
            )

        return lyric_pronunciation_list

    def recover_pronunciation_by_kana_tag(self,
                                          kana_tag: str
                                          ) -> None:
        """
        使用假名标签刷新所有读音，原读音将被洗掉

        Refresh all pronunciations with kana tag, the original pronunciation will be washed away
        """

        self.pronunciation_list = self.get_pronunciation_by_kana_tag(kana_tag)

        return None


if __name__ == '__main__':
    # test_str: str = " <00:0.0>あ <00:01:000>い <00:02:000>う <00:03:000>え <00:04:000>お1 <00:04:000>"
    # print(LyricLineContent.split_line_to_time_and_char(test_str, "strict"))
    # print(LyricLineContent.split_line_to_time_and_char(test_str, "normal"))
    # print(LyricLineContent.split_line_to_time_and_char(test_str, "loose"))
    # print(LyricLineContent.split_line_to_time_and_char(test_str, "very_loose"))

    # 测试Lyric_line_content.get_all_chinese_and_chu_nom_and_chinese_radical
    test_str: str = "1<00:0.0>あNi你他 <00:01:000>い  <00:02:000>う <00:03:000>え <00:04:000>お7 <00:04:000>X"
    Lrc_line_content_obj = LyricLineContent(test_str, mode=("very_loose", None))
    Lrc_line_content_obj.pronunciation_list = [
            LyricPronunciationGroup(base_str=Lrc_line_content_obj.lyric_char_list,
                                    pronunciation_line_list=
                                    [LyricPronunciationGroup(base_str=Lrc_line_content_obj.lyric_char_list[:5],
                                                             pronunciation_line_list=None)])
    ]

    print(Lrc_line_content_obj.lyric_char_list)
    print(Lrc_line_content_obj.pronunciation_list)
    print(Lrc_line_content_obj.get_all_cjkv())
    print(Lrc_line_content_obj.get_plain_text_format())
    print(test_str)

    print("==========================================")

    print(Lrc_line_content_obj.get_plain_text_format(min_len_of_minutes=1, min_len_of_seconds=1,
                                                     min_len_of_millisecond=1))
    print(Lrc_line_content_obj.get_plain_text_format(enable_pronunciation=True, min_len_of_minutes=1,
                                                     min_len_of_seconds=1, min_len_of_millisecond=1))
    print(no_tab_line := Lrc_line_content_obj.get_plain_text_format(enable_time=False, min_len_of_minutes=1,
                                                                    min_len_of_seconds=1, min_len_of_millisecond=1))
    print(no_tab_line == "".join([str(char) for char in Lrc_line_content_obj.lyric_char_list]))

    print("==========================================")
    print(Lrc_line_content_obj.pronunciation_list)
    print(Lrc_line_content_obj.pronunciation_list[0].pronunciation)
    print(Lrc_line_content_obj.get_kana_tag())


    print("==========================================")
    KANA_EXAMPLE = "你1い1う1えお2"
    print(iterator := re.finditer(LyricPronunciationGroup.KANA_TAB_REGREX, KANA_EXAMPLE))
    print(next(iterator).group())
    print(Lrc_line_content_obj.get_kana_tag())
    print(Lrc_line_content_obj.recover_pronunciation_by_kana_tag(KANA_EXAMPLE))
    print(Lrc_line_content_obj.pronunciation_list)
    print(Lrc_line_content_obj.base_str)
    print(Lrc_line_content_obj.pronunciation)
    print(type(Lrc_line_content_obj.pronunciation))
    print(
        Lrc_line_content_obj.get_plain_text_format(max_recursion_depth=2, enable_time=True, enable_pronunciation=True))


    # print(Lrc_line_content_obj.time_char_object_list)
    # print(Lrc_line_content_obj._lyric_pronunciation_list)
    #
    # # 测试加法
    # # print(a := LyricLineContent("a") + LyricLineContent("b"))
    #
    # # print(a["a"])
    #
    # c = LyricLineContent("")
    # print(c.time_char_object_list)
    # print(c._lyric_pronunciation_list)
    # print(c.data)
    # output = Lrc_line_content_obj.format_content()
    # print(output)
