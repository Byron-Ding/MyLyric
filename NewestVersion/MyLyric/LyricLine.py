import re
import warnings
from collections import UserList
from typing import Optional, Self, Any

from DataTypeInterface import var_type_guard, Comparable
from LyricTimeTab import LyricTimeTab
from LyricLineContent import LyricLineContent, LyricPronunciationGroup


class LyricLine(Comparable):

    def __init__(self,
                 time_tab_list: list[LyricTimeTab] | UserList[LyricTimeTab],
                 lyric_content_list: list[LyricLineContent] | UserList[LyricLineContent]
                 ):

        # ================== Type Guard 🛡️ ==================
        # List of LyricTimeTab OR None
        var_type_guard(time_tab_list, (list,))

        for each_time_tab in time_tab_list:
            var_type_guard(each_time_tab, (LyricTimeTab,))
        # time_tab_list = time_tab_list

        # List of LyricLineContent
        var_type_guard(lyric_content_list, (list, UserList))
        for each_lyric_content in lyric_content_list:
            var_type_guard(each_lyric_content, (LyricLineContent,))

        # ================== 基本属性 ==================
        # 歌词标签，用于适应多行合并的歌词
        # 自动排序 时间标签
        self._time_tabs: list[LyricTimeTab] = sorted(time_tab_list)

        # 向后兼容，用列表存储
        self._lyric_contents: list[LyricLineContent] = lyric_content_list

    @property
    def lyric_contents(self):
        return self._lyric_contents

    @lyric_contents.setter
    def lyric_contents(self, value: list[LyricLineContent] | UserList[LyricLineContent]) -> None:
        # ================== Type Guard 🛡️ ==================
        # List of LyricLineContent
        var_type_guard(value, (list, UserList))
        for each_lyric_content in value:
            var_type_guard(each_lyric_content, (LyricLineContent,))

        # ================== 赋值 ==================
        self._lyric_contents = value

    @property
    def time_tabs(self) -> list[LyricTimeTab]:
        return self._time_tabs

    @time_tabs.setter
    def time_tabs(self, value: list[LyricTimeTab] | UserList[LyricTimeTab]) -> None:
        # ================== Type Guard 🛡️ ==================
        # List of LyricTimeTab OR None
        var_type_guard(value, (list, type(None)))

        if value is not None:
            for each_time_tab in value:
                var_type_guard(each_time_tab, (LyricTimeTab,))
            # time_tab_list = time_tab_list
        else:
            value = []

        # ================== 赋值 ==================
        self._time_tabs = sorted(value)

    def __str__(self):
        return self.format_output_standard(enable_char_tab=True,
                                           enable_char_pronunciation=False)

    def __len__(self):
        return len(self._time_tabs)

    def __getitem__(self, item: int) -> str:
        var_type_guard(item, (int,))

        # 直接合并歌词列表
        lyric_contents_str = ""
        for lyric_content in self._lyric_contents:
            lyric_contents_str += str(lyric_content)

        # 加个时间头输出
        return str(self._time_tabs[item]) + lyric_contents_str

    def __setitem__(self, key: int, value: LyricTimeTab):
        var_type_guard(key, (int,))
        var_type_guard(value, (LyricTimeTab,))

        self._time_tabs[key] = value

    def __delitem__(self, key: int):
        var_type_guard(key, (int,))

        del self._time_tabs[key]

    def __iter__(self):
        # 返回每个时间标签+歌词内容
        for time_tab in self._time_tabs:
            lyric_contents_str = ""
            for lyric_content in self._lyric_contents:
                lyric_contents_str += str(lyric_content)

            yield time_tab + lyric_contents_str

    def __reversed__(self):
        # 返回每个时间标签+歌词内容
        for time_tab in reversed(self._time_tabs):
            lyric_contents_str = ""
            for lyric_content in self._lyric_contents:
                lyric_contents_str += str(lyric_content)

            yield time_tab + lyric_contents_str

    def __contains__(self, item: LyricTimeTab):
        return item in self._time_tabs

    # 大小比较，以第一个时间标签为准
    def __eq__(self, other: Self | LyricTimeTab) -> bool:
        if isinstance(other, LyricTimeTab):
            return self.time_tabs[0] == other
        elif isinstance(other, LyricLine):

        else:
            raise ValueError("Unsupported type for comparison between LyricLine and " + str(type(other)))

    def __lt__(self, other: Self | LyricTimeTab) -> bool:
        if isinstance(other, LyricTimeTab):
            return self.time_tabs[0] < other
        elif isinstance(other, LyricLine):
            self.time_tabs[0]: LyricTimeTab
            other.time_tabs[0]: LyricTimeTab

            return self.time_tabs[0] < other.time_tabs[0]
        else:
            raise ValueError("Unsupported type for comparison between LyricLine and " + str(type(other)))

    def is_empty(self) -> bool:
        """
        判断是否为空

        :return: bool
        """
        for each_time_tab in self._time_tabs:
            if not each_time_tab.is_empty():
                return False

        for each_lyric_content in self._lyric_contents:
            if not each_lyric_content.is_empty():
                return False

        return True

    def is_empty_time_tab(self) -> bool:
        """
        判断是否为空

        :return: bool
        """
        for each_time_tab in self._time_tabs:
            if not each_time_tab.is_empty():
                return False

        return True

    def is_empty_lyric_content(self) -> bool:
        """
        判断是否为空

        :return: bool
        """
        for each_lyric_content in self._lyric_contents:
            if not each_lyric_content.is_empty():
                return False

        return True

    # 不支持加减乘除，防止混乱

    # 解构，返回每个时间标签和歌词内容 的列表
    def decompress_time_tab(self) -> list[Self]:
        output_list: list[Self] = []

        # 返回每个时间标签+歌词内容 的 LyricLine 列表
        for time_tab in self._time_tabs:
            # 用每个时间标签 和 所有的歌词内容，新建一个 LyricLine 对象
            new_lyric_line_object: Self = LyricLine([time_tab], self._lyric_contents)

            # 添加到列表
            output_list.append(new_lyric_line_object)

        return output_list

    @staticmethod
    def is_valid_time_tab_head_under_mode_classmethod(full_line: str,
                                                      mode: tuple[str, re.Pattern]
                                                      ) -> bool:
        """
        判断是否是有效的时间标签头

        Determine whether it is a valid time tag head

        :param full_line: str
        :param mode: list[str, re.Pattern] | tuple[str, re.Pattern]
        :return: bool
        """

        # ================== Type Guard 🛡️ ==================
        var_type_guard(full_line, (str,))
        var_type_guard(mode, (list, tuple))

        var_type_guard(mode[0], (str,))
        var_type_guard(mode[1], (re.Pattern,))

        # Check Within Mode Types
        if mode[0] == "self_defined":
            if mode[1] is None:
                raise ValueError("Mode is self_defined, but regrex is None")
            time_tab_regrex = mode[1]

            full_line_regrex = re.compile(time_tab_regrex.pattern + r".*")
        elif mode[0] in set(LyricTimeTab.MODE_TYPE).remove("self_defined"):
            if mode[1] is not None:
                warnings.warn("Mode is not self_defined, but regrex is not None")

            full_line_regrex = LyricLine.get_full_line_regrex_by_mode(mode[0])
        else:
            raise ValueError("Unsupported mode type")


        # ================== 正则匹配 ==================
        # match result
        match = full_line_regrex.fullmatch(full_line)

        # ================== 返回 ==================
        return match is not None


    def is_valid_time_tab_head_under_mode(self,
                                          mode: tuple[str, re.Pattern]
                                          ) -> bool:
        """
        判断是否是有效的时间标签头

        Determine whether it is a valid time tag head

        :param mode: tuple[str, re.Pattern] Mode of Time Tab, 2nd option is for self_defined
        :return: bool
        """

        # ================== Type Guard 🛡️ ==================
        var_type_guard(mode, (tuple,))
        var_type_guard(mode[0], (str,))
        var_type_guard(mode[1], (re.Pattern,))

        # Check Within Mode Types
        if mode[0] == "self_defined":
            if mode[1] is None:
                raise ValueError("Mode is self_defined, but regrex is None")
            time_tab_regrex = mode[1]

        elif mode[0] in set(LyricTimeTab.MODE_TYPE).remove("self_defined"):
            if mode[1] is not None:
                warnings.warn("Mode is not self_defined, but regrex is not None")

        else:
            raise ValueError("Unsupported mode type")

        return self.is_valid_time_tab_head_under_mode_classmethod(self.format_output_base_on_inner_parm(),
                                                                  mode)



    # 格式化输出
    def format_output(self,
                      main_tab_min_len_of_minutes: int | None = 2,
                      main_tab_min_len_of_seconds: int | None = 2,
                      main_tab_min_len_of_millisecond: int | None = 2,
                      main_tab_cut_off_millisecond: bool = True,
                      main_tab_brackets: list[str] | tuple[str, str] = ("[", "]"),
                      main_tab_seperator: list[str] | tuple[str, str] = (":", "."),
                      enable_char_tab: bool = False,
                      enable_char_pronunciation: bool = False,
                      char_tab_min_len_of_minutes: int | None = 2,
                      char_tab_min_len_of_seconds: int | None = 2,
                      char_tab_min_len_of_millisecond: int | None = 2,
                      char_tab_cut_off_millisecond: bool = True,
                      char_tab_brackets: list[str] | tuple[str, str] = ("<", ">"),
                      char_tab_seperator: list[str] | tuple[str, str] = (":", "."),
                      max_recursion_depth: int = 1,
                      ) -> str:

        # 用于输出字符串
        output_str: str = ""

        time_tab_str: str
        lyric_content_str: str

        # 遍历时间标签
        for time_tab in self._time_tabs:
            # 用于输出字符串
            time_tab_str = time_tab.convert_to_time_tab(min_len_of_minutes=main_tab_min_len_of_minutes,
                                                        min_len_of_seconds=main_tab_min_len_of_seconds,
                                                        min_len_of_millisecond=main_tab_min_len_of_millisecond,
                                                        cut_off_millisecond=main_tab_cut_off_millisecond,
                                                        brackets=main_tab_brackets,
                                                        seperator=main_tab_seperator
                                                        )
            output_str += time_tab_str

        for lyric_content in self._lyric_contents:
            # 用于输出字符串
            lyric_content_str = lyric_content.get_plain_text_format(max_recursion_depth=max_recursion_depth,
                                                                    enable_time=enable_char_tab,
                                                                    enable_pronunciation=enable_char_pronunciation,
                                                                    min_len_of_minutes=char_tab_min_len_of_minutes,
                                                                    min_len_of_seconds=char_tab_min_len_of_seconds,
                                                                    min_len_of_millisecond=char_tab_min_len_of_millisecond,
                                                                    cut_off_millisecond=char_tab_cut_off_millisecond,
                                                                    seperator=char_tab_seperator,
                                                                    bracket=char_tab_brackets)
            output_str += lyric_content_str

        return output_str

    def format_output_base_on_inner_parm(self) -> str:
        # 用于输出字符串
        output_str: str = ""

        time_tab_str: str
        lyric_content_str: str

        # 遍历时间标签
        for time_tab in self._time_tabs:
            # 用于输出字符串
            time_tab_str = time_tab.convert_to_time_tab_base_on_inner_param()
            output_str += time_tab_str

        for lyric_content in self._lyric_contents:
            # 用于输出字符串
            lyric_content_str = lyric_content.get_plain_text_format_base_on_inner_parm()
            output_str += lyric_content_str

        return output_str

    def format_output_standard(self,
                               enable_char_tab: bool = True,
                               enable_char_pronunciation: bool = False,
                               ) -> str:
        return self.format_output(enable_char_tab=enable_char_tab,
                                  enable_char_pronunciation=enable_char_pronunciation,
                                  max_recursion_depth=1)

    # 判断是否是同一句歌词
    def whether_same_lyric(self,
                           other: Self
                           ) -> bool:
        # 不管时间标签
        # 只看歌词内容
        return self._lyric_contents == other._lyric_contents

    def shift_time(self,
                   minutes: int,
                   seconds: int,
                   milliseconds: int,
                   ) -> Self:
        # 时间标签整体向后移动
        # 遍历时间标签
        for time_tab in self._time_tabs:
            time_tab.shift_time(minutes=minutes,
                                seconds=seconds,
                                milliseconds=milliseconds
                                )

        return self

    def get_all_cjkv_char(self) -> list[list[str, int]]:
        # 输出列表
        output_list: list[list[str, int]] = []

        # 逐个拼接
        for each_lyric_content in self._lyric_contents:
            each_lyric_content_cjkv: list[list[str, int]] \
                = each_lyric_content.get_all_cjkv()

            output_list += each_lyric_content_cjkv

        return output_list

    def get_kana_tag(self) -> str:
        output_str = ""
        for each_lyric_line_content in self.lyric_contents:
            output_str += each_lyric_line_content.get_kana_tag()

        return output_str

    def update_pronunciation(self,
                             pronunciation_each_line: list[LyricPronunciationGroup] |
                                                      UserList[LyricPronunciationGroup]
                             ) -> None:
        if len(self.lyric_contents) == 1:
            self.lyric_contents[0]: LyricLineContent
            self.lyric_contents[0].pronunciation_list = pronunciation_each_line
        else:
            raise ValueError("Multiple lyric contents in one lyric line, not supported")

    def recover_pronunciation_by_kana_tag(self,
                                          kana_tag: str
                                          ) -> None:
        if len(self.lyric_contents) == 1:
            self.lyric_contents[0]: LyricLineContent
            self.lyric_contents[0].recover_pronunciation_by_kana_tag(kana_tag)
        else:
            raise ValueError("Multiple lyric contents in one lyric line, not supported")

    @staticmethod
    def get_full_line_regrex_by_mode(mode: str) -> re.Pattern:
        """
        根据模式获取整行的正则表达式

        get the regrex of the whole line by mode

        :param mode: str
        :return: re.Pattern
        
        """

        # ----------------- Type Guard 🛡️ -----------------
        var_type_guard(mode, (str,))

        # ----------------- 获取正则表达式 -----------------
        # 获取时间标签的正则表达式
        time_tab_regrex: re.Pattern = LyricTimeTab.TIME_TAB_MODE_REGREX_PAIR_SQUARE_BRACKETS[mode[0]]
        full_regrex: re.Pattern = re.compile("(?P<time_tab>" + time_tab_regrex.pattern + "*)" +
                                             "(?P<lyric_content>.*)")

        return full_regrex

    @staticmethod
    def from_str(input_str: str,
                 mode: tuple[str, re.Pattern, re.Pattern] = ("standard", None, None)
                 ) -> "LyricLine":
        """
        从字符串中解析出 LyricLine 对象
        如果自定义模式，需要提供Time Tab的正则表达式
        以及整行的正则表达式: 包含 lyric_content 组标签
        如果使用预设模式，只需要提供模式名即可，第二位参数为 None

        Get LyricLine object from string
        If self_defined mode, you need to provide the regrex of time tab
        and the regrex of the whole line, which contains the group tag of lyric_content
        If standard mode, you only need to provide the mode name, and the second parameter should be None

        :param input_str: str
        :param mode: tuple[str, re.Pattern]
        :return: LyricLine
        """
        full_regrex: re.Pattern

        # ----------------- Type Guard 🛡️ -----------------
        var_type_guard(input_str, (str,))
        var_type_guard(mode, (tuple,))
        var_type_guard(mode[0], (str,))
        var_type_guard(mode[1], (type(None), re.Pattern))
        var_type_guard(mode[2], (type(None), re.Pattern))

        if mode[0] == "self_defined":
            if mode[1] is None or mode[2] is None:
                raise ValueError("Mode is self_defined, but regrex is None")
            else:
                pass
        elif mode[0] in set(LyricTimeTab.MODE_TYPE).remove("self_defined"):
            if mode[1] is not None or mode[2] is not None:
                warnings.warn("Mode is not self_defined, but regrex is not None")
            else:
                pass
        else:
            raise ValueError("Unsupported mode type")

        # ----------------- 获取正则表达式 -----------------
        if mode[0] == "self_defined":
            time_tab_regrex = mode[1]
            full_regrex = r"(?P<time_tab>" + time_tab_regrex.pattern + r"*)" + \
                          mode[2].pattern
            time_tab_mode: tuple[str, re.Pattern | None] = (mode[0], time_tab_regrex)
        else:
            # 获取时间标签的正则表达式
            time_tab_regrex = LyricTimeTab.TIME_TAB_MODE_REGREX_PAIR_SQUARE_BRACKETS[mode[0]]
            full_regrex = LyricLine.get_full_line_regrex_by_mode(mode[0])
            time_tab_mode: tuple[str, re.Pattern | None] = (mode[0], None)

        # ----------------- 正则匹配 -----------------
        match = full_regrex.fullmatch(input_str)
        if match is None:
            raise ValueError("Input string does not match the regrex")

        # ----------------- 获取时间标签 -----------------
        time_tab_str: str = match.group("time_tab")

        # 逐个标签剥离
        time_tab_list: list[LyricTimeTab] = []
        time_tab_iter = re.finditer(time_tab_regrex, time_tab_str)
        # 逐个时间标签
        for each_time_tab in time_tab_iter:
            each_time_tab: re.Match
            time_tab_list.append(LyricTimeTab(each_time_tab.group(), time_tab_mode))

        # ----------------- 获取歌词内容 -----------------
        lyric_content_str: str = match.group("lyric_content")
        lyric_content_list: list[LyricLineContent] = [LyricLineContent(lyric_base_char_list=lyric_content_str)]

        # ----------------- 返回 -----------------
        return LyricLine(time_tab_list, lyric_content_list)


if __name__ == '__main__':
    # 测试
    # 新定义几个时间标签
    time_tab1 = LyricTimeTab("[00:00.00]")
    time_tab2 = LyricTimeTab("[00:01.00]")
    time_tab3 = LyricTimeTab("[00:02.00]")
    time_tab4 = LyricTimeTab("[00:03.00]")
    time_tab5 = LyricTimeTab("[00:04.00]")

    # 新定义几个歌词内容
    lyric_content1 = LyricLineContent("歌词1")

    # 打乱顺序，组成乱序列表，用于测试
    time_tabs = [time_tab1, time_tab3, time_tab2, time_tab5, time_tab4]

    # 输入时间标签和歌词内容
    lyric_line = LyricLine(time_tabs, [lyric_content1])

    print(lyric_line.lyric_contents)
    print(lyric_line.time_tabs)

    # 输出
    print(str(lyric_line))
    print(repr(lyric_line))
    print(len(lyric_line))
    print(lyric_line.decompress_time_tab())
