import re
import warnings
from mailbox import FormatError
from typing import Any, Iterator, List
from typing import Optional, Self
from typing import Union
from typing import Pattern, Match
from typing import Callable

from DataTypeInterface import var_type_guard
from .LyricTimeTab import LyricTimeTab
from .LyricLineContent import LyricLineContent
from .LyricLine import LyricLine
from SelfDefinedError import FormatError


class Lyric_file:
    """
    中文：\n
    初始化函数，接受一个参数，参数类型为str或者list，分别对应文件内容和文件内容的列表形式 \n
    \n
    str 为文件内容 \n
    list 为文件内容的列表形式，每个元素为一行歌词

    English: \n
    Initialization function, accepts one parameter,
    the parameter type is str or list,
    which corresponds to the file content
    and the list form of the file content respectively \n
    \n
    str is the file content \n
    list is the list form of the file content, each element is a line of lyrics

    :param lrc_content: Union[str, list]
    :return: None
    """

    """
    同时兼容文件和文件内容
    其实没有必要，可以用另外一个函数生成饭后返回实例化后的本类
    本类专注于处理文件内容，而不是文件本身
    """

    # ==================== 正则表达式区 ====================
    # 信息标签的正则表达式
    # 必须是非数字开头，后面随意字符，直到冒号
    # 冒号作为分隔符，然后是任意字符
    # 括号可以缺失，但是冒号不能缺失，括号必须是中括号
    # groups: 左括号，标签tag，冒号，内容tag_content，右括号
    # 例如：[ar:周杰伦]
    INFORMATION_TAG_REGEX: Pattern = re.compile(r"^(\[)?"
                                                r"(?P<tag>\D.*?)"  # 非数字开头，任意字符，非贪婪（到第一个冒号）
                                                r":"
                                                r"(?P<tag_content>.*)"
                                                r"(])?$")

    # 正式歌词的正则表达式
    # 中括号可以缺失，但是冒号不能缺失，起始标签的括号必须是中括号
    # 分为两组
    # groups: (左括号，分，冒号，秒，冒号或者点，毫秒，右括号)[时间标签组]，歌词内容[歌词内容组]
    # 例如：[00:00.00]歌词内容
    LRC_CONTENT_REGEX: Pattern = re.compile(r"^(?P<_current_time_tab>("
                                            r"(\[)?"
                                            r"(\d?)"
                                            r"(:?)"
                                            r"(\d?)"
                                            r"([.:]?)"
                                            r"(\d+)"
                                            r"(])?)*"
                                            r")"
                                            r"(?P<lrc_content>.*)$")

    # 标准格式
    INFORMATION_TAG_REGEX_STANDARD: Pattern = re.compile(r"^(\[)(?P<tag>[a-zA-Z].*):(?P<tag_content>.*)(])$")
    LRC_CONTENT_REGEX_STANDARD: Pattern = re.compile(r"^(?P<_current_time_tab>((\[)(\d{2})(:)(\d{2})(\.)(\d{2})(])?)*)"
                                                     r"(?P<lrc_content>.*)$")

    EACH_PROUNUNCIATION_GROUP_IN_KANA_REGEX: Pattern = re.compile(r"(?P<all_group>"
                                                                  r"(?P<character_length>\d)"
                                                                  r"(?P<pronounciation>\D*)"
                                                                  r")")

    # ==================== 正则表达式区结束 ====================

    def __init__(self,
                 lrc_content: Union[str, list[LyricLine | str]],
                 mode: tuple[str, Optional[Pattern[str]], Optional[Pattern[str]]] = ("normal", None, None),
                 merge_cross_line_lyrics: bool = True
                 ) -> None:
        """
        中文：\n
        初始化函数，接受一个参数，参数类型为str或者list，分别对应文件内容和文件内容的列表形式 \n
        \n
        str 为文件内容 \n
        list 为文件内容的列表形式，每个元素为一行歌词

        English: \n
        Initialization function, accepts one parameter,
        the parameter type is str or list,
        which corresponds to the file content
        and the list form of the file content respectively \n
        \n
        str is the file content \n
        list is the list form of the file content, each element is a line of lyrics

        :param lrc_content: Union[str, list]
        :return: None
        """
        # ==================== 参数检查区 Var Type Guard 🛡️ ====================
        var_type_guard(lrc_content, (str, list))
        if isinstance(lrc_content, list):
            for each_element in lrc_content:
                var_type_guard(each_element, (LyricLine, str))

        var_type_guard(mode, (tuple,))

        if mode[0] in set(LyricTimeTab.MODE_TYPE).remove("self_defined"):
            if mode[1] is not None:
                warnings.warn("The mode type is not 'self_defined',"
                              " so the second element of the mode tuple will be ignored.")
        elif mode[0] == "self_defined":
            if mode[1] is None:
                raise ValueError("The mode type is 'self_defined',"
                                 " so the second element of the mode tuple cannot be None.")
            else:
                var_type_guard(mode[1], (Pattern,))
        else:
            raise ValueError(f"Invalid mode type: {mode[0]}; should be one of {LyricTimeTab.MODE_TYPE}")

        var_type_guard(merge_cross_line_lyrics, (bool,))

        # ==================== 歌词的内容属性区 ====================

        # 一级列表，每个元素为一行歌词，原始歌词备份区
        self.lrc_lines_primary_initial: list[str] = []
        # 二级列表，每个元素为一行歌词，每行歌词为一个列表，列表第一个元素为时间标签类或者None（表示只有内容），第二个元素为歌词内容(也是一个类)
        # 之后所有的操作都是基于这个列表，这个列表是最终的歌词内容
        self.lrc_lines_secondary: list[LyricLine] = []

        # ==================== 歌词的内容属性区结束 ====================

        # ==================== 歌词的信息属性区 ====================
        # tag 初始化，考虑后期封装
        # 基本 tag 的属性
        # 设定TAG初始值为None
        self.artist: Optional[str] = None
        self.album: Optional[str] = None
        self.lyric_writer: Optional[str] = None
        self.lrc_file_writer: Optional[str] = None
        self.length: Optional[str] = None
        # self.length_int: Optional[int] = None
        self.offset: Optional[str] = None
        self.creating_software: Optional[str] = None
        self.title: Optional[str] = None
        self.version: Optional[str] = None

        # 日语歌词专用，不确定具体含义
        self.kana: Optional[str] = None

        # 非标准 tag 字典
        self.nonstandard_tag_dict: dict[str, str] = {}

        # 提前建立所有标签的列表，字典可能会乱序，为后面json做准备
        self.tag_list = [
            "artist",
            "album",
            "lyric_writer",
            "lrc_file_writer",
            "length",
            "offset",
            "creating_software",
            "title",
            "version",
            "kana"
        ]
        # 字典，方便查找
        # 标签，标签的含义（也是属性名）
        self.tag_dict: Optional[dict[str, str]] = {'ar': 'artist',
                                                   'al': 'album',
                                                   'au': 'lyric_writer',
                                                   'by': 'lrc_file_writer',
                                                   'length': 'length',
                                                   'offset': 'offset',
                                                   're': 'creating_software',
                                                   'ti': 'title',
                                                   've': 'version',
                                                   'kana': 'kana'  # 日语歌词专用，不确定具体含义
                                                   }

        # ==================== 歌词的信息属性区结束 ====================

        # ==================== 歌词总属性区 ====================
        self.mode: tuple[str, Optional[Pattern[str]], Optional[Pattern[str]]] = mode

        self.whether_merge_cross_line_lyrics: bool = merge_cross_line_lyrics

        # 歌词文件的编码，默认是None，即不指定编码，以纯文本的形式读取
        self.lrc_encoding: Optional[str] = None

        # 获取是否为拓展LRC格式，默认为False
        self.whether_extension: bool = False

        # ==================== 歌词总属性区结束 ====================

        # ==================== 内部设置属性区 ====================

        # 定义__next__返回下一个的初始化[clc]
        # 用于自我迭代
        self.__next__index: int = 0

        # ==================== 内部设置属性区结束 ====================

        # ==================== 预分离处理 ====================
        # 预分离处理
        # 调用预分离处理函数
        self.__pre_separation(lrc_content, mode)

        # ==================== 预分离处理结束 ====================

    # ==================== Separation ====================

    def __pre_separation(self,
                         lrc_content: Union[str, list[str, LyricLine]],
                         mode: tuple[str, Optional[Pattern[str]], Optional[Pattern[str]]]
                         ) -> None:
        """
        中文：
        预分离处理，根据接受的参数类型，分别进行处理

        English:
        Pre-separation processing, according to the type of parameters received, respectively processing

        :param lrc_content: Union[str, list]
        :return: None
        """

        information_setter_flag: bool = True

        # 是字符串，按行分割，去除空行（含只有空白字符的行）
        if isinstance(lrc_content, str):
            # 按行分割
            self.lrc_lines_primary_initial = lrc_content.splitlines()
            self.lrc_lines_primary_initial: list[str]
            line: str | LyricLine
            # 去除空行
            self.lrc_lines_primary_initial = [line for line in self.lrc_lines_primary_initial
                                              if not line.isspace()]
        # 是列表，直接赋值，但是依然要去除空行（含只有空白字符的行）
        elif isinstance(lrc_content, list):
            for line in lrc_content:
                if isinstance(line, LyricLine):
                    pass
                else:
                    # goto Another checking
                    # str
                    break
            else:
                # 全部是Lyric_line 不需要 分离信息，信息都是空
                information_setter_flag = False

                lrc_content: list[LyricLine]
                self.lrc_lines_secondary: list[LyricLine] = lrc_content
                line: str | LyricLine

                self.lrc_lines_primary_initial = [line.format_output_base_on_inner_parm() for line in lrc_content
                                                  if not line.is_empty()]

            # Another checking
            for line in lrc_content:
                if isinstance(line, str):
                    pass
                else:
                    # goto Error
                    break
            else:
                lrc_content: list[str]
                line: str
                self.lrc_lines_primary_initial = [line for line in self.lrc_lines_primary_initial
                                                  if not line.isspace()]

            raise TypeError("lrc_content must be str or list[LyricLine | str] divided by lines")
        # 不是字符串也不是列表，抛出异常
        else:
            raise TypeError("lrc_content must be str or list divided by lines")

        if information_setter_flag:
            # 调用信息分离处理函数，分离歌词内容和歌词信息
            # 传入参数为歌词内容的列表
            self.__lrc_information_content_separation(self.lrc_lines_primary_initial,
                                                      mode)

        if self.whether_merge_cross_line_lyrics:
            # 合并跨行歌词
            self.merge_cross_line_lyrics()

    # 歌词内容分离处理函数，分离歌词内容和歌词信息
    # 传入参数为歌词内容的列表
    def __lrc_information_content_separation(self,
                                             lrc_lines: list[str],
                                             mode: tuple[str, Optional[Pattern[str]], Optional[Pattern[str]]]
                                             ) -> None:
        """
        中文：
        歌词内容分离处理函数，分离歌词内容和歌词信息
        判断是否为扩展LRC格式

        English:
        Lyric content separation processing function, separate lyric content and lyric information
        Determine whether it is an extended LRC format

        :param lrc_lines: list of lyric content, divided by lines
        :return: None
        """

        # 逐行处理
        for line_index, line in enumerate(lrc_lines):
            # 扩展LRC在 LyricLineContent 类中处理，然后再传入

            # 按照正则表达式匹配，逐行匹配
            # 如果是歌词信息
            if each_line_match := self.INFORMATION_TAG_REGEX.match(line) is not None:
                # 歌词信息处理函数
                self.__lrc_information_processing(each_line_match)
            # 其他默认为歌词内容
            # 如果是歌词内容，（其他内容可以选择是否合并到上一行歌词）
            elif each_line_match := self.LRC_CONTENT_REGEX.match(line) is not None:
                # 歌词内容处理函数
                self.__lrc_content_processing(each_line_match, mode)

            # 如果都不是，那么就是非法的内容，报错
            else:
                raise FormatError(f"Invalid content in line {line_index + 1}: {line}")

        # 最后处理
        # 考虑到涉及整个文件的内容
        # 处理kana
        pronunciation_each_line = self.extract_kana_tag()
        # 更新每行的读音
        self.update_pronunciation(pronunciation_each_line)

    # ==================== Process ====================

    # 歌词信息处理函数
    # 传入参数为歌词信息的字符串
    def __lrc_information_processing(self, each_line_match: Match) -> None:
        """
        中文：
        歌词信息处理函数

        English:
        Lyric information processing function

        :param each_line_match: 歌词信息的字符串 the string of lyric information
        :return: None
        """
        # 获取标签
        tag = each_line_match.group("tag")
        # 获取属性名
        tag_name = self.tag_dict[tag]
        # 获取属性值
        tag_value = each_line_match.group("tag_content")

        # 识别歌词信息的标签，确定是否为默认标签之一（字典的键），如果是，那么直接复制给对应的属性
        if tag in self.tag_dict.keys():
            # 赋值
            setattr(self, tag_name, tag_value)
        # 如果不是，那么就是自定义的标签，储存到一部字典中
        else:
            # 添加到字典中
            self.nonstandard_tag_dict[tag_name] = tag_value

    # 歌词内容处理函数
    # 传入参数为歌词内容的字符串
    def __lrc_content_processing(self,
                                 each_line: str,
                                 mode: tuple[str, Optional[Pattern[str]], Optional[Pattern[str]]]
                                 ) -> None:
        """
        中文：
        每行歌词内容处理函数
        分离时间标签和歌词内容

        English:
        Each line of lyric content processing function
        Separate the time tag and lyric content

        :param each_line: 每行歌词内容的字符串 the string of each line of lyric content
        :return: None
        """
        # 用正则表达式匹配，获取时间和歌词（时间可能为空）
        each_line_object: LyricLine = LyricLine.from_str(each_line, mode)

        # 放入二级歌词列表中
        self.lrc_lines_secondary.append(each_line_object)

        if self.whether_merge_cross_line_lyrics:
            # 合并跨行歌词
            self.merge_cross_line_lyrics()

    # 合并跨行歌词
    @staticmethod
    def merge_cross_line_lyrics_static(secondary_lyric_list: list[LyricLine]
                                       ) -> list[LyricLine]:
        """
        中文：
        合并跨行歌词

        English:
        Merge cross-line lyrics

        :return: None
        """
        # ========================= Type Guard 🛂🛡️ =========================
        var_type_guard(secondary_lyric_list, (list,))
        for each_line_list in secondary_lyric_list:
            var_type_guard(each_line_list, (LyricLine,))

        # ========================= Check =========================
        # 检测第一行是否有时间标签，第一行空白无法向上合并，没有负一行
        # 没有或者空白字符串，报错
        if secondary_lyric_list[0].time_tabs is None or secondary_lyric_list[0].time_tabs == []:
            raise ValueError("The first line of lyrics does not have a time tag")

        # ========================= Process =========================
        # 返回的列表
        return_list: list[LyricLine] = []

        # 逐行处理
        for each_line_list in secondary_lyric_list:
            # 如果时间标签 有内容，那么就是新的一行歌词
            if each_line_list.time_tabs is not None and each_line_list.time_tabs != []:
                # 添加到列表中
                return_list.append(each_line_list)
            # 如果时间标签 为空，那么就是上一行歌词的延续
            else:
                # 添加到上一行歌词的列表中
                return_list[-1].lyric_contents.extend(each_line_list.lyric_contents)

        return return_list

    # 合并跨行歌词
    # 实例方法
    def merge_cross_line_lyrics(self) -> Self:
        """
        中文：
        合并跨行歌词
        不更新一级列表

        English:
        Merge cross-line lyrics
        Do not update the primary list

        :return: Self
        """
        # 调用静态方法
        self.lrc_lines_secondary = self.merge_cross_line_lyrics_static(self.lrc_lines_secondary)

        # 这里不需要更新一级列表

        # 返回自身
        return self

    @classmethod
    def convert_primary_lyric_list_to_secondary_list_classmethod(cls,
                                                                 lrc_lines: str | list[str],
                                                                 mode: [str, Pattern[str]] = ("normal", None)
                                                                 ) -> list[LyricLine]:
        """
            中文：
            在纯歌词内容的字符串或列表中，分离时间标签和歌词内容

            English:
            In the string or list of pure lyric content, separate the time tag and lyric content

            :param lrc_lines: 歌词内容的字符串 || the string of lyric content
            :param mode: 时间标签检查严格度，可选值为 "strict", "normal", "loose" 和 “very_loose”
                || The strictness of the time tag check,
                 the optional values are "strict", "normal", "loose" and "very_loose"
            :return: list[list[LyricTimeTab, [str]]]
        """
        # 新的空列表
        line_list: list[str] = []

        # 如果是字符串，按行分割，去除空行（含只有空白字符的行）
        if isinstance(lrc_lines, str):
            lrc_lines: str
            # 按行分割
            line_list = lrc_lines.splitlines()
            # 去除空行
            line_list = [line for line in line_list if line.strip()]
        # 是列表，直接赋值，但是依然要去除空行（含只有空白字符的行）
        elif isinstance(lrc_lines, list):
            line_list = [line for line in line_list if line.strip()]
        # 不是字符串也不是列表，抛出异常
        else:
            var_type_guard(lrc_lines, (str, list))

        # 覆盖
        output_list: list[LyricLine] = []
        # 逐行处理
        for lrc_lines in line_list:
            # 按照正则表达式匹配，获取时间和歌词（时间可能为空）
            each_line_object: LyricLine = LyricLine.from_str(lrc_lines, mode)

            # 放入二级歌词列表中
            output_list.append(each_line_object)

        # 合并跨行歌词
        output_list = cls.merge_cross_line_lyrics_static(output_list)

        # 返回新的列表
        return output_list

    # 判断是否为标准格式
    '''
    比如
    [ti:松花江上]
    [ar:张寒晖]
    [al:张寒晖]
    [by:张寒晖]
    [offset:0]
    [00:00.00] 我的家
    [00:01.00] 在那东北松花江上
    [00:03.00] 我的家
    [00:04.00] 那里有森林煤矿
    ......
    '''

    @classmethod
    def judge_standard_form_classmethod(cls,
                                        lrc_content: Union[str, list[str], list[LyricLine]],
                                        mode: tuple[str, Pattern[str]] = ("normal", None)
                                        ) -> bool:
        """
        中文：\n
        判断是否为标准格式
        lrc_content参数可以是字符串，也可以是字符串列表，如果是字符串，那么先按照换行符分割成列表
        之后逐行判断
        歌词行则判断是否符合Mode,不看<00:00.00>这种格式，只看头部[00:00.00]是否符合相应格式

        English: \n
        Determine whether it is standard format
        The lrc_content parameter can be a string or a string list.
        If it is a string, it will be divided into a list according to the line break symbol first.
        Then judge line by line.
        For the lyrics line, judge whether it meets the Mode, not the format like <00:00.00>,
        only whether the head [00:00.00] meets the corresponding format


        For example this is valid under standard mode default \n
        [ti:松花江上]
        [ar:张寒晖]
        ...
        [00:00.00] 我的家
        [00:01.00] 在那东北松花江上
        [00:03.00] 我的家
        [00:04.00] 那里有森林煤矿
        ...

        :return: bool
        """

        # ========================= Type Guard 🛂🛡️ =========================
        var_type_guard(lrc_content, (str, list))
        if isinstance(lrc_content, list):
            for each_element in lrc_content:
                var_type_guard(each_element, (str, LyricLine))

        # ========================= Check =========================
        tag: str = "str"

        # 如果是字符串，那么先按照换行符分割成列表
        if isinstance(lrc_content, str):
            lrc_content = lrc_content.splitlines()
            # 去除空行（包括空白字符行）
            lrc_content = [line for line in lrc_content if line.strip()]
        elif isinstance(lrc_content, list):
            if isinstance(lrc_content[0], LyricLine):
                tag = "LyricLine"
            elif isinstance(lrc_content[0], str):
                pass
            else:
                raise TypeError("lrc_content in list must be str or LyricLine")
        else:
            raise TypeError("lrc_content must be str or list divided by lines")

        # 之后逐行判断
        if tag == "str":
            lrc_content: list[str]
            for line in lrc_content:
                # 如果符合两个标准格式的正则表达式中的一个，那么就是标准格式
                if (cls.INFORMATION_TAG_REGEX_STANDARD.match(line)
                        or cls.LRC_CONTENT_REGEX_STANDARD.match(line)):
                    continue
                # 否则就不是标准格式
                else:
                    return False

        elif tag == "LyricLine":
            lrc_content: list[LyricLine]
            for line in lrc_content:
                # should be full matched
                if not line.is_valid_time_tab_head_under_mode(mode):
                    return False

        return True

    # 针对实例
    # 判断是否为标准格式
    def judge_standard_form(self) -> bool:
        """
        中文：\n
        判断是否为标准格式

        English: \n
        Determine whether it is standard format

        :return: bool
        """
        return Lyric_file.judge_standard_form_classmethod(self.lrc_lines_primary_initial)

    # 合并换行的歌词为连续的行（中间用\n分割），也可以指定分隔符
    # 第一行有时间标签，后面的行没有时间标签，直到下一个有时间标签的行
    '''
    例子：
    [00:00.00] 我的家
    在那东北松花江上
    [00:03.00] 我的家
    那里有森林煤矿
    变成：
    [00:00.00] 我的家\n在那东北松花江上
    [00:03.00] 我的家\n那里有森林煤矿
    '''

    # 默认分隔符为\n
    # 默认输入的是歌词内容的二级列表
    # 默认的第一行有时间标签，所以直接从第二行开始判断，忽略第一行
    @staticmethod
    def combine_lyric_separated_to_continuous_lines_static(input_lyric_lines: list[LyricLine],
                                                           separator: str = "\n",
                                                           ) -> list[LyricLine]:
        """
        中文：\n
        合并换行的歌词为连续的行（中间用\n分割），也可以指定分隔符。
        第一行有时间标签，后面的行没有时间标签，直到下一个有时间标签的行。

        English: \n
        Combine the lyrics separated by each_lyric_line_object breaks into continuous lines (separated by \n in the middle),
        or you can specify a separator.
        The first each_lyric_line_object has a time tag,
         and the following lines do not have a time tag,
         until a each_lyric_line_object with a time tag.

        For example: \n
        [00:00.00] 我的家
        在那东北松花江上
        [00:03.00] 我的家
        那里有森林煤矿
        Become:
        [00:00.00] 我的家\n在那东北松花江上
        [00:03.00] 我的家\n那里有森林煤矿

        :param input_lyric_lines: list[LyricLine]
        :param separator: str
        :return: list[list[LyricTimeTab, str]]
        """

        # 新的列表
        output_list: list[LyricLine] = []

        # 先确认第一行有时间标签或者是非空字符串
        if not input_lyric_lines[0].is_empty_time_tab():
            raise ValueError("The first each_lyric_line_object of the input list"
                             " does not have a time tag or is an empty string.")

        # 遍历每一行
        for each_lyric_line_object in input_lyric_lines:
            each_lyric_line_object: LyricLine
            # 已经封装成Lyric_Time_tab对象了
            # 直接调用加法即可

            # 如果是第一行，那么直接放入新列表
            if each_lyric_line_object == input_lyric_lines[0]:
                output_list.append(each_lyric_line_object)
            # 如果不是第一行
            else:
                # 如果这一行没有时间标签，那么就和前一行合并
                # 注意这里的时间标签可以是Lyric_Time_tab对象，也可以是字符串
                # 只要不是None就行或者不是空字符串就行
                if each_lyric_line_object.is_empty_time_tab() is None:
                    # Extend the LyricLineContent
                    output_list[-1].lyric_contents.extend(each_lyric_line_object.lyric_contents)

                # 如果这一行有时间标签，那么就直接放入新列表
                else:
                    output_list.append(each_lyric_line_object)

        # 返回新列表
        return output_list

    # 实例方法
    def combine_lyric_separated_to_continuous_lines(self,
                                                    separator: str = "\n",
                                                    ) -> list[LyricLine]:
        """
        中文：\n
        合并换行的歌词为连续的行（中间用\n分割），也可以指定分隔符。
        第一行有时间标签，后面的行没有时间标签，直到下一个有时间标签的行。

        English: \n
        Combine the lyrics separated by line breaks into continuous lines (separated by \n in the middle),
        or you can specify a separator.
        The first line has a time tag,
        and the following lines do not have a time tag,
        until a line with a time tag.

        For example: \n
        [00:00.00] 我的家
        在那东北松花江上
        [00:03.00] 我的家
        那里有森林煤矿
        Become:
        [00:00.00] 我的家\n在那东北松花江上
        [00:03.00] 我的家\n那里有森林煤矿

        :param separator: str
        :return: list[list[LyricTimeTab | str, str]]
        """

        # 调用静态方法
        # 赋值回二级列表
        output = Lyric_file.combine_lyric_separated_to_continuous_lines_static(
            input_lyric_lines=self.lrc_lines_secondary,
            separator=separator
        )

        # 记得根据二级列表更新一级列表

        # 返回自身
        return output

    # 将歌词的二级列表转换为一级列表
    # 二级列表的每一行的第一个元素是时间标签，第二个元素是歌词内容
    @staticmethod
    def convert_secondary_lyric_list_to_primary_list_static(input_lyric_lines: list[LyricLine],
                                                            main_tab_min_len_of_minutes: int | None = 2,
                                                            main_tab_min_len_of_seconds: int | None = 2,
                                                            main_tab_min_len_of_millisecond: int | None = 2,
                                                            main_tab_cut_off_millisecond: bool = True,
                                                            main_tab_brackets: list[str] | tuple[str, str] = ("[", "]"),
                                                            main_tab_seperator: list[str] | tuple[str, str] = (
                                                                    ":", "."),
                                                            enable_char_tab: bool = False,
                                                            enable_char_pronunciation: bool = False,
                                                            char_tab_min_len_of_minutes: int | None = 2,
                                                            char_tab_min_len_of_seconds: int | None = 2,
                                                            char_tab_min_len_of_millisecond: int | None = 2,
                                                            char_tab_cut_off_millisecond: bool = True,
                                                            char_tab_brackets: list[str] | tuple[str, str] = ("<", ">"),
                                                            char_tab_seperator: list[str] | tuple[str, str] = (
                                                                    ":", "."),
                                                            max_recursion_depth: int = 1,
                                                            ) -> list[str]:
        """
        中文：\n
        将歌词的二级列表转换为一级列表。

        English: \n
        Convert the secondary list of lyrics into a primary list.

        :param input_lyric_lines: list[LyricLine] original list
        :param main_tab_min_len_of_minutes: int | None = 2
        :param main_tab_min_len_of_seconds: int | None = 2
        :param main_tab_min_len_of_millisecond: int | None = 2
        :param main_tab_cut_off_millisecond: bool = True
        :param main_tab_brackets: list[str] | tuple[str, str] = ("[", "]")
        :param main_tab_seperator: list[str] | tuple[str, str] = (":", ".")
        :param enable_char_tab: bool = False
        :param enable_char_pronunciation: bool = False
        :param char_tab_min_len_of_minutes: int | None = 2
        :param char_tab_min_len_of_seconds: int | None = 2
        :param char_tab_min_len_of_millisecond: int | None = 2
        :param char_tab_cut_off_millisecond: bool = True
        :param char_tab_brackets: list[str] | tuple[str, str] = ("<", ">")
        :param char_tab_seperator: list[str] | tuple[str, str] = (":", ".")
        :param max_recursion_depth: int = 1

        :return: list[str]
        一级列表
        Primary list
        """

        # 新的列表
        output_list: list[str] = []

        # 遍历每一行
        for line in input_lyric_lines:
            each_line: str = line.format_output(main_tab_min_len_of_minutes=main_tab_min_len_of_minutes,
                                                main_tab_min_len_of_seconds=main_tab_min_len_of_seconds,
                                                main_tab_min_len_of_millisecond=main_tab_min_len_of_millisecond,
                                                main_tab_cut_off_millisecond=main_tab_cut_off_millisecond,
                                                main_tab_brackets=main_tab_brackets,
                                                main_tab_seperator=main_tab_seperator,
                                                enable_char_tab=enable_char_tab,
                                                enable_char_pronunciation=enable_char_pronunciation,
                                                char_tab_min_len_of_minutes=char_tab_min_len_of_minutes,
                                                char_tab_min_len_of_seconds=char_tab_min_len_of_seconds,
                                                char_tab_min_len_of_millisecond=char_tab_min_len_of_millisecond,
                                                char_tab_cut_off_millisecond=char_tab_cut_off_millisecond,
                                                char_tab_brackets=char_tab_brackets,
                                                char_tab_seperator=char_tab_seperator,
                                                max_recursion_depth=max_recursion_depth,
                                                )

            # 放入新列表
            output_list.append(each_line)

        # 返回新列表
        return output_list

    # 实例方法
    def convert_secondary_lyric_list_to_primary_list(self,
                                                     main_tab_min_len_of_minutes: int | None = 2,
                                                     main_tab_min_len_of_seconds: int | None = 2,
                                                     main_tab_min_len_of_millisecond: int | None = 2,
                                                     main_tab_cut_off_millisecond: bool = True,
                                                     main_tab_brackets: list[str] | tuple[str, str] = ("[", "]"),
                                                     main_tab_seperator: list[str] | tuple[str, str] = (
                                                             ":", "."),
                                                     enable_char_tab: bool = False,
                                                     enable_char_pronunciation: bool = False,
                                                     char_tab_min_len_of_minutes: int | None = 2,
                                                     char_tab_min_len_of_seconds: int | None = 2,
                                                     char_tab_min_len_of_millisecond: int | None = 2,
                                                     char_tab_cut_off_millisecond: bool = True,
                                                     char_tab_brackets: list[str] | tuple[str, str] = ("<", ">"),
                                                     char_tab_seperator: list[str] | tuple[str, str] = (
                                                             ":", "."),
                                                     max_recursion_depth: int = 1,
                                                     ) -> list[str]:
        """
        中文：\n
        将歌词的二级列表转换为一级列表。

        English: \n
        Convert the secondary list of lyrics into a primary list.

        :param input_lyric_lines: list[LyricLine] original list
        :param main_tab_min_len_of_minutes: int | None = 2
        :param main_tab_min_len_of_seconds: int | None = 2
        :param main_tab_min_len_of_millisecond: int | None = 2
        :param main_tab_cut_off_millisecond: bool = True
        :param main_tab_brackets: list[str] | tuple[str, str] = ("[", "]")
        :param main_tab_seperator: list[str] | tuple[str, str] = (":", ".")
        :param enable_char_tab: bool = False
        :param enable_char_pronunciation: bool = False
        :param char_tab_min_len_of_minutes: int | None = 2
        :param char_tab_min_len_of_seconds: int | None = 2
        :param char_tab_min_len_of_millisecond: int | None = 2
        :param char_tab_cut_off_millisecond: bool = True
        :param char_tab_brackets: list[str] | tuple[str, str] = ("<", ">")
        :param char_tab_seperator: list[str] | tuple[str, str] = (":", ".")
        :param max_recursion_depth: int = 1

        :return: list[str]
        一级列表
        Primary list
        """

        # 调用静态方法
        output = Lyric_file.convert_secondary_lyric_list_to_primary_list_static(
            input_lyric_lines=self.lrc_lines_secondary,
            main_tab_min_len_of_minutes=main_tab_min_len_of_minutes,
            main_tab_min_len_of_seconds=main_tab_min_len_of_seconds,
            main_tab_min_len_of_millisecond=main_tab_min_len_of_millisecond,
            main_tab_cut_off_millisecond=main_tab_cut_off_millisecond,
            main_tab_brackets=main_tab_brackets,
            main_tab_seperator=main_tab_seperator,
            enable_char_tab=enable_char_tab,
            enable_char_pronunciation=enable_char_pronunciation,
            char_tab_min_len_of_minutes=char_tab_min_len_of_minutes,
            char_tab_min_len_of_seconds=char_tab_min_len_of_seconds,
            char_tab_min_len_of_millisecond=char_tab_min_len_of_millisecond,
            char_tab_cut_off_millisecond=char_tab_cut_off_millisecond,
            char_tab_brackets=char_tab_brackets,
            char_tab_seperator=char_tab_seperator,
            max_recursion_depth=max_recursion_depth,
        )

        # 返回新列表
        return output


    # 合并时间标签，把相同的歌词合并
    def compress_time_tab(self):
        # [00:00.00]歌词
        # [00:00.01]歌词
        # [00:00.02]歌词
        # 合并成 [00:00.00][00:00.01][00:00.02]歌词

        # 输出列表
        output_list: list[LyricLine] = []

        for current_index, current_line in enumerate(self.lrc_lines_secondary):
            # 如果是第一行，那么就直接加入
            if current_index == 0:
                output_list.append(current_line)

            # 接下来每一行 都与之前的每一行比较
            # 如果歌词相同，那么就合并时间标签
            # 如果歌词不同，那么就直接加入
            else:
                for each_previous_line in output_list:
                    if each_previous_line.whether_same_lyric(current_line):
                        # 合并时间标签
                        each_previous_line._time_tabs += current_line._time_tabs
                        # 因为是合并，所以不需要再继续比较了，会出现重复
                        break
                else:
                    # 如果没有合并，那么就直接加入
                    output_list.append(current_line)

        # 覆盖原来的列表
        self.lrc_lines_secondary = output_list

        # 返回自身
        return self

    # 解压时间标签，把多个时间标签拆分成多行
    def decompress_time_tab(self) -> Self:
        # 输出列表
        output_list: list[LyricLine] = []

        # 遍历每一行
        # 调用函数解压
        for current_line in self.lrc_lines_secondary:
            output_list += current_line.decompress_time_tab()

        self.lrc_lines_secondary = sorted(output_list)

        # 返回自身
        return self

    '''
    # 普通输出
    def output(self) -> str:
        warnings.WarningMessage("Not implemented yet.")
        pass
    '''

    # 格式化输出
    def format_output(self,
                      len_of_millisecond_output: int = 2,
                      seperator_each_line: tuple[str, str] = (":", "."),
                      seperator_inline: tuple[str, str] = (":", ".")
                      ) -> str:

        # 用于输出字符串
        output_str: str = ""

        # 先添加信息
        if self.artist:
            output_str += "[ar:" + self.artist + "]\n"
        if self.album:
            output_str += "[al:" + self.album + "]\n"
        if self.title:
            output_str += "[ti:" + self.title + "]\n"
        if self.length:
            output_str += "[length:" + self.length + "]\n"
        if self.lyric_writer:
            output_str += "[au:" + self.lyric_writer + "]\n"
        if self.lrc_file_writer:
            output_str += "[by:" + self.lrc_file_writer + "]\n"
        if self.creating_software:
            output_str += "[re:" + self.creating_software + "]\n"
        if self.version:
            output_str += "[ve:" + self.version + "]\n"
        if self.kana:
            output_str += "[kana:" + self.get_total_kana_tag() + "]\n"

        # 对自定义标签，非标准进行输出
        # 名字在之前的列表中
        for each_customized_tag, value in self.nonstandard_tag_dict:
            each_customized_tag: str
            value: str
            output_str += "[" + each_customized_tag + ":" + value + "]\n"

        time_tab_str: str
        # 遍历每一行
        for each_lyric_line in self.lrc_lines_secondary:
            each_lyric_line_str = each_lyric_line.format_output(len_of_millisecond_output=len_of_millisecond_output,
                                                                seperator_each_line=seperator_each_line,
                                                                seperator_inline=seperator_inline)

            output_str += each_lyric_line_str + "\n"

        # 去除最后一个换行符
        output_str = output_str[:-1]

        return output_str

    def update_kana_tag(self) -> Self:
        self.kana = self.get_total_kana_tag()

    def shift_time(self,
                   minutes: int,
                   seconds: int,
                   milliseconds: int,
                   len_of_millisecond: int = 3
                   ) -> Self:
        for each_lyric_line in self.lrc_lines_secondary:
            each_lyric_line.shift_time(minutes=minutes,
                                       seconds=seconds,
                                       milliseconds=milliseconds,
                                       len_of_millisecond=len_of_millisecond)

        return self

    def get_all_chinese_and_chu_nom_and_chinese_radical_list_each_line(self) -> list[list[list[str, int]]]:
        output_list = []
        for each_lyric_line in self.lrc_lines_secondary:
            output_list.append(each_lyric_line.get_all_chinese_and_chu_nom_and_chinese_radical())

        return output_list

    def extract_kana_tag(self) -> list[list[list[LyricLineContent, int]]]:
        CJKV_list = self.get_all_chinese_and_chu_nom_and_chinese_radical_list_each_line()

        # 统计每行有多少个CJKV字符
        CJKV_count_each_line: list[int] = [len(each_line) for each_line in CJKV_list]

        # kana分解
        kana_character_list: list[list[str, int]] = self.split_kana_tag_to_characters(self.kana)
        # 每一行的综合体
        kana_character_line_list: list[list[list[str, int]]] = []
        # 累加器
        clc: int = 0
        # 对应每一行
        for each_line_number in CJKV_count_each_line:
            # 从累加器开始，到累加器+当前行的CJKV字符数
            kana_character_line_list.append(kana_character_list[clc:clc + each_line_number])
            # 累加
            clc += each_line_number

        # 输出列表
        # 输出的长发音列表，发音列表(行的长度，就是那个[])
        output_list: list[list[list[LyricLineContent, int]]] = []
        # 对应每一行
        for each_line_CJKV_index, \
                each_line_pronunciation_list, \
                character_number_each_line \
                in zip(CJKV_list,
                       kana_character_line_list,
                       CJKV_count_each_line):
            # 直接调用方法
            each_line_pronunciation_full_list: list[list[LyricLineContent, int]] \
                = LyricLineContent.extend_pronunciation_list(
                each_line_CJKV_index,
                each_line_pronunciation_list,
                character_number_each_line
            )

            # 加到输出列表
            output_list.append(each_line_pronunciation_full_list)

        return output_list

    @staticmethod
    def split_kana_tag_to_characters(kana_tag_content: str) -> list[list[str, int]]:
        # 第一个必须是数字，表示接下来几个字符是对应该读音
        # 分解kana标签
        kana_tag_list: list[list[str, int]] = []

        if kana_tag_content is None:
            return kana_tag_list

        # 第一个必须是数字，表示接下来几个字符是对应该读音
        elif kana_tag_content[0].isdigit():
            # 否则报错
            raise ValueError("The first character of kana tag must be a number representing the number of characters "
                             " corresponding to the reading.")

        else:
            # 匹配每个读音
            # 格式：[长度][读音（非数字）]
            matched_pronunciation_groups: Iterator[Match[str | bytes | Any]] = \
                Lyric_file.EACH_PROUNUNCIATION_GROUP_IN_KANA_REGEX.finditer(kana_tag_content)

            for each_matched_pronunciation_group in matched_pronunciation_groups:
                # [读音，长度]
                each_small_list: list[str, int] = [each_matched_pronunciation_group.group("pronunciation_line_list"),
                                                   each_matched_pronunciation_group.group("length")]
                kana_tag_list.append(each_small_list)

        return kana_tag_list

    def get_total_kana_tag(self) -> str:

        # 输出字符串
        output_list: str = ""

        for each_line in self.lrc_lines_secondary:
            each_line: LyricLine
            # 调用每行的方法，得到每行的读音
            kana_tag_each_line = each_line.get_kana_tag()

            # 加入每行的读音
            output_list += kana_tag_each_line

        return output_list

    def update_pronunciation(self, pronunciation_each_line: list[list[list[LyricLineContent, int]]]) -> Self:
        # 逐行更新
        for each_line, each_line_pronunciation in zip(self.lrc_lines_secondary, pronunciation_each_line):
            each_line: LyricLine
            each_line_pronunciation: list[list[LyricLineContent, int]]

            # 更新
            each_line.update_pronunciation(each_line_pronunciation)

        return self

    '''
    转为srt字幕
    '''

    def _to_srt(self) -> str:
        pass


if __name__ == '__main__':
    # 测试
    # 读取文件

    with open("../../Test_Files/ブルーバード (青鸟) - 生物股长 (いきものがかり).lrc", mode="r", encoding="utf-8") as f:
        content = f.read()
        print(content)

    a = Lyric_file.LRC_CONTENT_REGEX.match('[00:00.00][10:12:22]ブルーバード - 生物股长 (いきものがかり)')

    print(b := a.group("_current_time_tab"))
    c = LyricTimeTab.TIME_TAB_EACH_LINE_VERY_LOOSE_REGREX.match(b)
    print(c)

    Lyric_file_Test_File_青鸟 = Lyric_file(content)

    print(Lyric_file_Test_File_青鸟.judge_standard_form())
    Lyric_file_Test_File_青鸟.combine_lyric_separated_to_continuous_lines()
    a = Lyric_file_Test_File_青鸟.lrc_lines_secondary
    # print(Lyric_file_Test_File_青鸟.format_output(len_of_millisecond_output=2))
    b = Lyric_file_Test_File_青鸟.compress_time_tab()
    print(Lyric_file_Test_File_青鸟.format_output(len_of_millisecond_output=2))

    print("\n\n\n\n\n")
    c = Lyric_file_Test_File_青鸟.decompress_time_tab()
    print(Lyric_file_Test_File_青鸟.format_output(len_of_millisecond_output=2))

    kana_tag = Lyric_file_Test_File_青鸟.kana
    print(kana_tag)
    print(matched_kana := Lyric_file.EACH_PROUNUNCIATION_GROUP_IN_KANA_REGEX.finditer(kana_tag))
    for i in matched_kana:
        print(i.groups())
