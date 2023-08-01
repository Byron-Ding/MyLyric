import re
import warnings
from typing import Any
from typing import Optional, Self
from typing import Union
from typing import Pattern, Match
from typing import Callable
from Lyric_Time_tab import Lyric_Time_tab
from Lyric_line_content import Lyric_line_content



class Lyric_file:
    """
    同时兼容文件和文件内容
    其实没有必要，可以用另外一个函数生成饭后返回实例化后的本类
    本类专注于处理文件内容，而不是文件本身
    """

    # ==================== 正则表达式区 ====================
    # 信息标签的正则表达式
    # 必须是字母开头，后面随意字符，直到冒号
    # 冒号作为分隔符，然后是任意字符
    # 括号可以缺失，但是冒号不能缺失，括号必须是中括号
    # groups: 左括号，标签tag，冒号，内容tag_content，右括号
    # 例如：[ar:周杰伦]
    INFORMATION_TAG_REGEX: Pattern = re.compile(r"^(\[)?(?P<tag>[a-zA-Z].*):(?P<tag_content>.*)(])?$")

    # 正式歌词的正则表达式
    # 中括号可以缺失，但是冒号不能缺失，起始标签的括号必须是中括号
    # 分为两组
    # groups: (左括号，分，冒号，秒，冒号或者点，毫秒，右括号)[时间标签组]，歌词内容[歌词内容组]
    # 例如：[00:00.00]歌词内容
    LRC_CONTENT_REGEX: Pattern = re.compile(r"^(?P<time_tab>(\[)?(\d+)(:)(\d+)([.:])(\d*)(])?)?"
                                            r"(?P<lrc_content>.*)$")

    # 标准格式
    INFORMATION_TAG_REGEX_STANDARD: Pattern = re.compile(r"^(\[)(?P<tag>[a-zA-Z].*):(?P<tag_content>.*)(])$")
    LRC_CONTENT_REGEX_STANDARD: Pattern = re.compile(r"^(?P<time_tab>(\[)(\d{2})(:)(\d{2})(\.)(\d{2})(])?)"
                                                     r"(?P<lrc_content>.*)$")

    # ==================== 正则表达式区结束 ====================

    def __init__(self, lrc_content: Union[str, list], mode: str = "normal") -> None:
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

        # ==================== 歌词的内容属性区 ====================

        # 一级列表，每个元素为一行歌词，原始歌词备份区
        self.lrc_lines_primary_initial: list[str] = []
        # 二级列表，每个元素为一行歌词，每行歌词为一个列表，列表第一个元素为时间标签类或者None（表示只有内容），第二个元素为歌词内容(也是一个类)
        # 之后所有的操作都是基于这个列表，这个列表是最终的歌词内容
        self.lrc_lines_secondary: list[list[Optional[Lyric_Time_tab],
                                            Lyric_line_content]] = []

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

        self.mode: str = mode

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

    def __pre_separation(self, lrc_content: Union[str, list], mode: str) -> None:
        """
        中文：
        预分离处理，根据接受的参数类型，分别进行处理

        English:
        Pre-separation processing, according to the type of parameters received, respectively processing

        :param lrc_content: Union[str, list]
        :return: None
        """

        # 是字符串，按行分割，去除空行（含只有空白字符的行）
        if isinstance(lrc_content, str):
            # 按行分割
            self.lrc_lines_primary_initial = lrc_content.splitlines()
            # 去除空行
            self.lrc_lines_primary_initial = [line for line in self.lrc_lines_primary_initial if line.strip()]
        # 是列表，直接赋值，但是依然要去除空行（含只有空白字符的行）
        elif isinstance(lrc_content, list):
            self.lrc_lines_primary_initial = [line for line in lrc_content if line.strip()]
        # 不是字符串也不是列表，抛出异常
        else:
            raise TypeError("lrc_content must be str or list divided by lines")

        # 调用信息分离处理函数，分离歌词内容和歌词信息
        # 传入参数为歌词内容的列表
        self.__lrc_information_content_separation(self.lrc_lines_primary_initial, mode)

        # 合并跨行歌词
        self.merge_cross_line_lyrics()

    # 歌词内容分离处理函数，分离歌词内容和歌词信息
    # 传入参数为歌词内容的列表
    def __lrc_information_content_separation(self, lrc_lines: list[str], mode: str) -> None:
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
        for line in lrc_lines:
            # 先判断是否为扩展LRC格式
            # 设置属性
            if self.whether_extension is False:
                # 如果是扩展LRC格式
                if "<" in line or ">" in line:
                    self.whether_extension = True

            # 按照正则表达式匹配，逐行匹配
            # 如果是歌词信息
            if each_line_match := self.INFORMATION_TAG_REGEX.match(line):
                # 歌词信息处理函数
                self.__lrc_information_processing(each_line_match)
            # 其他默认为歌词内容
            # 如果是歌词内容，（其他内容可以选择是否合并到上一行歌词）
            else:
                # 歌词内容处理函数
                self.__lrc_content_processing(line, mode)

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
        # 识别歌词信息的标签，确定是否为默认标签之一（字典的键），如果是，那么直接复制给对应的属性
        if tag in self.tag_dict.keys():
            # 获取属性名
            tag_name = self.tag_dict[tag]
            # 获取属性值
            tag_value = each_line_match.group("tag_content")
            # 赋值
            setattr(self, tag_name, tag_value)

        # 如果不是，那么就是自定义的标签，储存到一部字典中
        else:
            # 获取标签名
            tag_name = each_line_match.group("tag")
            # 获取标签值
            tag_value = each_line_match.group("tag_content")
            # 添加到字典中
            self.nonstandard_tag_dict[tag_name] = tag_value

    # 歌词内容处理函数
    # 传入参数为歌词内容的字符串
    def __lrc_content_processing(self, each_line: str, mode: str) -> None:
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
        each_line_match = self.LRC_CONTENT_REGEX.match(each_line)

        time: str | Optional[Lyric_Time_tab]
        # 获取时间
        time: str = each_line_match.group("time_tab")
        # 获取歌词
        lrc: str = each_line_match.group("lrc_content")

        # 转为类
        lrc_obj: Lyric_line_content = Lyric_line_content(lrc,
                                                                                               separation_mode=mode)

        # 判断时间 是否为空
        if time:
            time_obj: Optional[Lyric_Time_tab] = Lyric_Time_tab(time, mode)
        # 如果为空，转为 None
        else:
            time_obj: Optional[Lyric_Time_tab] = None

        # 放入二级歌词列表中
        self.lrc_lines_secondary.append([time_obj, lrc_obj])
        # 合并跨行歌词
        self.merge_cross_line_lyrics()

    # 合并跨行歌词
    @staticmethod
    def merge_cross_line_lyrics_static(secondary_lyric_list: list[Any,
                                                                  Lyric_line_content]
                                       ) -> list[Any,
                                                 Lyric_line_content]:
        """
        中文：
        合并跨行歌词

        English:
        Merge cross-line lyrics

        :return: None
        """

        # 检测第一行是否有时间标签
        # 没有或者空白字符串，报错
        if secondary_lyric_list[0][0] is None or secondary_lyric_list[0][0].isspace():
            raise ValueError("The first line of lyrics does not have a time tag")

        # 返回的列表
        return_list: list[Any, Lyric_line_content] = []

        # 逐行处理
        for each_line_list in secondary_lyric_list:
            # 如果时间标签 有内容，那么就是新的一行歌词
            if each_line_list[0]:
                # 添加到列表中
                return_list.append(each_line_list)
            # 如果时间标签 为空，那么就是上一行歌词的延续
            else:
                # 添加到上一行歌词的列表中
                return_list[-1][1] += each_line_list[1]

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
                                                                 mode: str
                                                                 ) -> list[list[Lyric_Time_tab,
                                                                                Lyric_line_content]]:
        """
            中文：
            在纯歌词内容的字符串或列表中，分离时间标签和歌词内容

            English:
            In the string or list of pure lyric content, separate the time tag and lyric content

            :param lrc_lines: 歌词内容的字符串 || the string of lyric content
            :param mode: 时间标签检查严格度，可选值为 "strict", "normal", "loose" 和 “very_loose”
                || The strictness of the time tag check,
                 the optional values are "strict", "normal", "loose" and "very_loose"
            :return: list[list[Lyric_Time_tab, [str]]]
        """
        # 新的空列表
        output_list: list[str | list[Lyric_Time_tab], Lyric_line_content]

        # 如果是字符串，按行分割，去除空行（含只有空白字符的行）
        if isinstance(lrc_lines, str):
            # 按行分割
            output_list = lrc_lines.splitlines()
            # 去除空行
            output_list = [line for line in output_list if line.strip()]
        # 是列表，直接赋值，但是依然要去除空行（含只有空白字符的行）
        elif isinstance(lrc_lines, list):
            output_list = [line for line in lrc_lines if line.strip()]
        # 不是字符串也不是列表，抛出异常
        else:
            raise TypeError("lrc_content must be str or list divided by lines")

        # 逐行处理
        for lrc_lines in output_list:
            # 用正则表达式匹配，获取时间和歌词（时间可能为空）
            each_line_match = cls.LRC_CONTENT_REGEX.match(lrc_lines)

            time: str | Optional[Lyric_Time_tab]
            # 获取时间
            time = each_line_match.group("time")
            # 获取歌词
            lrc: str = each_line_match.group("lrc")

            lrc: Lyric_line_content = Lyric_line_content(lrc)

            # 判断时间 是否为空
            if time:
                time = Lyric_Time_tab(time, mode)
            # 否则转为None
            else:
                time = None

            # 覆盖原项，放入new_list中
            lrc_lines = [time, lrc]
            output_list[output_list.index(lrc_lines)] = lrc_lines

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
    def judge_standard_form_classmethod(cls, lrc_content: Union[str, list[str]]) -> bool:
        """
        中文：\n
        判断是否为标准格式
        lrc_content参数可以是字符串，也可以是字符串列表，如果是字符串，那么先按照换行符分割成列表
        之后逐行判断

        English: \n
        Determine whether it is standard format
        The lrc_content parameter can be a string or a string list.
        If it is a string, it will be divided into a list according to the line break symbol first.
        Then judge line by line.

        For example \n
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

        # 如果是字符串，那么先按照换行符分割成列表
        if isinstance(lrc_content, str):
            lrc_content = lrc_content.splitlines()
            # 去除空行（包括空白字符行）
            lrc_content = [line for line in lrc_content if line.strip()]

        # 之后逐行判断
        for line in lrc_content:
            # 如果符合两个标准格式的正则表达式中的一个，那么就是标准格式
            if (cls.INFORMATION_TAG_REGEX_STANDARD.match(line)
                    or cls.LRC_CONTENT_REGEX_STANDARD.match(line)):
                continue
            # 否则就不是标准格式
            else:
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
    def combine_lyric_separated_to_continuous_lines_static(input_lyric_lines: list[
        list[Any,
             Lyric_line_content],
    ],
                                                           separator: str = "\n",
                                                           ) -> list[list[Any,
                                                                          Lyric_line_content]]:
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

        :param input_lyric_lines: list[list[Lyric_Time_tab, str]]
        :param separator: str
        :return: list[list[Lyric_Time_tab, str]]
        """

        # 新的列表
        output_list: list[list[Lyric_Time_tab | str,
                               Lyric_line_content]] = []

        # 先确认第一行有时间标签或者是非空字符串
        if not (input_lyric_lines[0][0]):
            raise ValueError("The first line of the input list does not have a time tag or is an empty string.")

        # 遍历每一行
        for line in input_lyric_lines:
            line: list[Optional[Lyric_Time_tab | str],
                       Lyric_line_content]
            # 已经封装成Lyric_Time_tab对象了
            # 直接调用加法即可

            # 如果是第一行，那么直接放入新列表
            if line == input_lyric_lines[0]:
                output_list.append(line)
            # 如果不是第一行
            else:
                # 如果这一行没有时间标签，那么就和前一行合并
                # 注意这里的时间标签可以是Lyric_Time_tab对象，也可以是字符串
                # 只要不是None就行或者不是空字符串就行
                if line[0] is None:
                    line[0]: None
                    # 直接字符串拼接
                    output_list[-1][1] = output_list[-1][1] + separator + line[1]

                elif isinstance(line[0], str):
                    line[0]: str
                    if line[0] == "":
                        # 直接字符串拼接
                        output_list[-1][1] = output_list[-1][1] + separator + line[1]

                elif isinstance(line[0], Lyric_Time_tab):
                    line[0]: Lyric_Time_tab
                    if line[0].time_tab == "" or line[0].time_tab is None or line[0].time_tab.isspace():
                        # 直接字符串拼接
                        output_list[-1][1] = output_list[-1][1] + separator + line[1]

                # 如果这一行有时间标签，那么就直接放入新列表
                else:
                    output_list.append(line)

        # 返回新列表
        return output_list

    # 实例方法
    def combine_lyric_separated_to_continuous_lines(self,
                                                    separator: str = "\n",
                                                    ) -> list[list[Any,
                                                                   Lyric_line_content]]:
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
        :return: list[list[Lyric_Time_tab | str, str]]
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
    def convert_secondary_lyric_list_to_primary_list_static(input_lyric_lines: list[
        list[Any, Lyric_line_content],
    ],
                                                            time_tab_str_function: Callable[[Any], str]
                                                            = lambda x: str(x),
                                                            lyric_line_content_str_function: Callable[
                                                                [Lyric_line_content], str]
                                                            = lambda x: str(x),
                                                            ) -> list[str]:
        """
        中文：\n
        将歌词的二级列表转换为一级列表。

        English: \n
        Convert the secondary list of lyrics into a primary list.

        :param input_lyric_lines: list[list[Lyric_Time_tab | str, str]]
        原始的二级列表
        Original secondary list
        :param time_tab_str_function: Callable[[Any], str]
        转换时间标签到str的函数
        The function that converts the time tag to str
        :param lyric_line_content_str_function: Callable[[Lyric_line_content], str]
        转换歌词内容到str的函数
        The function that converts the lyrics content to str

        :return: list[str]
        一级列表
        Primary list
        """

        # 新的列表
        output_list: list[str] = []

        # 先合并
        input_lyric_lines = Lyric_file.combine_lyric_separated_to_continuous_lines_static(
            input_lyric_lines=input_lyric_lines
        )

        # 遍历每一行
        for line in input_lyric_lines:
            each_line: str = time_tab_str_function(line[0]) \
                             + lyric_line_content_str_function(line[1])

            # 放入新列表
            output_list.append(each_line)

        # 返回新列表
        return output_list

    # 计算所有的翻译时间标签
    # 参数有
    # 百分比： b - a 的百分之多少 + a = (就是翻译的时间标签)
    # 是否忽略空歌词，空歌词会给占位符[None,None]
    # 最后一行的计算上限（b - a），因为最后一行没有下一行，通常设定为0
    def calculate_all_translated_time_tab(self,
                                          percentage: float = 0.5,
                                          last_line_time_tab_limit: float = 0,
                                          ignore_empty_lyric: bool = False,
                                          ) -> list[
        list[Optional[Lyric_Time_tab],
             Lyric_line_content]
    ]:
        """
        中文：\n
        计算所有的翻译时间标签。

        English: \n
        Calculate all translated time tags.

        :param percentage: float
        :param ignore_empty_lyric: bool
        :param last_line_time_tab_limit: float
        :return: Self
        """

        # 看第一行是否有时间标签
        # 如果没有时间标签 或者 第一行时间标签为空白字符串，那么就抛出异常
        if self.lrc_lines_secondary[0][0] is None:
            raise ValueError("第一行没有时间标签，无法计算。")
        elif isinstance(self.lrc_lines_secondary[0][0], Lyric_Time_tab):
            if self.lrc_lines_secondary[0][0].time_tab.isspace():
                raise ValueError("第一行时间标签为空白字符串，无法计算。")

        # 输出
        output_list: list[list[Optional[Lyric_Time_tab],
                               Lyric_line_content]] = []

        first_line_after_nonempty_index: int = 1

        if ignore_empty_lyric:
            # 找到第一行非空歌词的行号
            # 所有遍历的行，都需要预先添加入返回列表
            for index, line in enumerate(self.lrc_lines_secondary):
                # 添加入返回列表
                output_list.append(line)
                # 第一行非空歌词的行号
                if not line[1].isspace():
                    first_line_after_nonempty_index = index
                    # 时间标签
                    previous_line_time_tab: Lyric_Time_tab = line[0]
                    break
            # 如果全是空歌词，那么就抛出异常
            else:
                raise ValueError("All lines are empty lyrics.")
        else:
            # 前一行的时间标签，初始化为第一行的时间标签
            previous_line_time_tab: Lyric_Time_tab = self.lrc_lines_secondary[0][0]
            output_list.append(self.lrc_lines_secondary[0])

        # 当前行歌词
        # current_line_lyric: Optional[Lyric_line_content] = self.lrc_lines_secondary[0][1]

        # 下一行的时间标签，初始化为None
        # next_line_time_tab: Optional[Lyric_Time_tab] = None

        # 遍历每一行
        # 从第二行开始
        for line in self.lrc_lines_secondary[first_line_after_nonempty_index:]:
            # 先看是否有时间标签
            # 如果没有时间标签 或者 时间标签为空白字符串，跳过，直到找到时间标签为止
            if self.lrc_lines_secondary[0][0] is None:
                continue
            elif isinstance(self.lrc_lines_secondary[0][0], Lyric_Time_tab):
                if self.lrc_lines_secondary[0][0].time_tab.isspace():
                    continue

            # 先赋值给 下一行的时间标签临时变量
            next_line_time_tab = line[0]

            # 忽略空歌词 并且 当前行歌词 不 为空白字符串
            # 执行添加翻译时间标签 操作
            if ignore_empty_lyric and not line[1].isspace():
                # 计算翻译时间标签
                # 结果是time stamp
                translated_time_tab: float = (previous_line_time_tab
                                              + (next_line_time_tab - previous_line_time_tab)
                                              * percentage)

                # 转成时间标签字符串
                translated_time_tab: str = Lyric_Time_tab.convert_time_stamp_to_time_tab_static(
                    time_stamp=translated_time_tab,
                )

                # 转为时间标签对象
                translated_time_tab: Lyric_Time_tab = Lyric_Time_tab(
                    tab=translated_time_tab,
                    mode=self.mode
                )

                # 加入输出列表 [时间标签对象，翻译歌词("")空字符串]
                output_list.append([translated_time_tab, Lyric_line_content("")])

            # 更新前一行的时间标签
            previous_line_time_tab = next_line_time_tab

        # 最后一行的时间标签
        # 涉及到 last_line_time_tab_limit
        # 如果 last_line_time_tab_limit = 0，那么就是最后一行的时间标签
        # 其他情况，（last_line_time_tab_limit
        # - 那么就是最后一行的时间标签）* percentage
        # 计算翻译时间标签
        # 结果是time stamp
        translated_time_tab: float = (previous_line_time_tab
                                      + (last_line_time_tab_limit - previous_line_time_tab)
                                      * percentage)

        # 转成时间标签字符串
        translated_time_tab: str = Lyric_Time_tab.convert_time_stamp_to_time_tab_static(
            time_stamp=translated_time_tab,
        )

        # 转为时间标签对象
        translated_time_tab: Lyric_Time_tab = Lyric_Time_tab(
            tab=translated_time_tab,
            mode=self.mode
        )

        # 加入输出列表 [时间标签对象，翻译歌词(其实默认是空字符串)]
        output_list.append([translated_time_tab, Lyric_line_content("")])

        # 返回输出列表
        return output_list

    # 计算所有的翻译时间标签，然后更新二级列表
    # 和上面的方法不同，这个方法会更新二级列表
    def calculate_all_translated_time_tab_and_update_secondary_lyric_list(self,
                                                                          percentage: float = 0.5,
                                                                          last_line_time_tab_limit: float = 0,
                                                                          ignore_empty_lyric: bool = False
                                                                          ) -> Self:
        """
        中文：\n
        计算所有的翻译时间标签，然后更新二级列表。

        English: \n
        Calculate all translated time tags and update the secondary list.

        :param percentage: float
        :param last_line_time_tab_limit: float
        :param ignore_empty_lyric: bool
        :return: Self
        """

        # 看第一行是否有时间标签
        # 如果没有时间标签 或者 第一行时间标签为空白字符串，那么就抛出异常
        if self.lrc_lines_secondary[0][0] is None:
            raise ValueError("第一行没有时间标签，无法计算。")
        elif isinstance(self.lrc_lines_secondary[0][0], Lyric_Time_tab):
            if self.lrc_lines_secondary[0][0].time_tab.isspace():
                raise ValueError("第一行时间标签为空白字符串，无法计算。")

        # 输出
        output_list: list[list[Optional[Lyric_Time_tab],
                               Lyric_line_content]] = []

        first_line_after_nonempty_index: int = 1

        if ignore_empty_lyric:
            # 找到第一行非空歌词的行号
            # 所有遍历的行，都需要预先添加入返回列表
            for index, line in enumerate(self.lrc_lines_secondary):
                # 添加入返回列表
                output_list.append(line)
                # 第一行非空歌词的行号
                if not line[1].isspace():
                    first_line_after_nonempty_index = index
                    previous_line_time_tab: Lyric_Time_tab = line[0]
                    break

            else:
                # 如果没有非空歌词，那么就返回空列表
                # 说明所有歌词都是空的
                raise ValueError("All lyrics are empty.")

        else:
            # 前一行的时间标签，初始化为第一行的时间标签
            previous_line_time_tab: Lyric_Time_tab = self.lrc_lines_secondary[0][0]
            output_list.append(self.lrc_lines_secondary[0])

        # 下一行的时间标签，初始化为None
        next_line_time_tab: Optional[Lyric_Time_tab]

        # 遍历每一行
        # 从第二行开始
        for line in self.lrc_lines_secondary[first_line_after_nonempty_index:]:
            # 先把原来的歌词加入输出列表，后面跟翻译歌词
            output_list.append(line)
            # 先看是否有时间标签
            # 如果没有时间标签 或者 时间标签为空白字符串，跳过，直到找到时间标签为止
            if self.lrc_lines_secondary[0][0] is None:
                continue
            elif isinstance(self.lrc_lines_secondary[0][0], Lyric_Time_tab):
                if self.lrc_lines_secondary[0][0].time_tab.isspace():
                    continue

            # 先赋值给 下一行的时间标签临时变量
            next_line_time_tab = line[0]

            if ignore_empty_lyric and line[1].isspace():
                #    计算翻译时间标签
                # 结果是time stamp
                translated_time_tab: float = (previous_line_time_tab
                                              + (next_line_time_tab - previous_line_time_tab)
                                              * percentage)

                # 转成时间标签字符串
                translated_time_tab: str = Lyric_Time_tab.convert_time_stamp_to_time_tab_static(
                    time_stamp=translated_time_tab,
                )

                # 转为时间标签对象
                translated_time_tab: Lyric_Time_tab = Lyric_Time_tab(
                    tab=translated_time_tab,
                    mode=self.mode
                )

                # 加入输出列表 [时间标签对象，翻译歌词("")空字符串]
                output_list.append([translated_time_tab, Lyric_line_content("")])

            # 更新前一行的时间标签
            previous_line_time_tab = next_line_time_tab

            # 更新当前行歌词
            # current_line_lyric = line[1]

        # 最后一行的时间标签
        # 涉及到 last_line_time_tab_limit
        # 如果 last_line_time_tab_limit = 0，那么就是最后一行的时间标签
        # 其他情况，（last_line_time_tab_limit
        # - 那么就是最后一行的时间标签）* percentage
        # 计算翻译时间标签
        # 结果是time stamp
        translated_time_tab: float = (previous_line_time_tab
                                      + (last_line_time_tab_limit - previous_line_time_tab)
                                      * percentage)

        # 转成时间标签字符串
        translated_time_tab: str = Lyric_Time_tab.convert_time_stamp_to_time_tab_static(
            time_stamp=translated_time_tab,
        )

        # 转为时间标签对象
        translated_time_tab: Lyric_Time_tab = Lyric_Time_tab(
            tab=translated_time_tab,
            mode=self.mode
        )

        # 加入输出列表 [时间标签对象，翻译歌词(其实默认是空字符串)]
        output_list.append([translated_time_tab, Lyric_line_content("")])

        self.lrc_lines_secondary = output_list

        # 返回输出列表
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

        time_tab_str: str
        # 遍历每一行
        for line in self.lrc_lines_secondary:
            # 两个成分，时间标签和歌词
            # 两个类
            time_tab: Lyric_Time_tab | None = line[0]
            lyric_line_content: Lyric_line_content | None = line[1]

            # 时间标签，排除None
            if time_tab is None:
                time_tab: None
                time_tab_str = ""
            else:
                time_tab: Lyric_Time_tab
                time_tab_str = time_tab.convert_to_time_tab(
                    len_of_millisecond_output=len_of_millisecond_output,
                    seperator=seperator_each_line
                )

            # 歌词，排除None
            if lyric_line_content is None:
                lyric_line_content: None
                lyric_line_content_str = ""
            else:
                lyric_line_content: Lyric_line_content
                lyric_line_content_str = lyric_line_content.format_content(
                    len_of_millisecond_output=len_of_millisecond_output,
                    seperator=seperator_inline
                )

            # 拼接
            output_str += time_tab_str + lyric_line_content_str + "\n"


        return output_str




if __name__ == '__main__':
    # 测试
    # 读取文件

    with open("Test_Files/ブルーバード (青鸟) - 生物股长 (いきものがかり).lrc", mode="r", encoding="utf-8") as f:
        content = f.read()
        print(content)

    Lyric_file_Test_File_青鸟 = Lyric_file(content)

    print(Lyric_file_Test_File_青鸟.judge_standard_form())
    # Lyric_file_Test_File_青鸟.combine_lyric_separated_to_continuous_lines()
    a = Lyric_file_Test_File_青鸟.lrc_lines_secondary
    print(Lyric_file_Test_File_青鸟.format_output(len_of_millisecond_output=2))
