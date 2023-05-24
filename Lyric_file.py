import re
from typing import Optional, List
from typing import Union
from typing import Pattern, Match
import Lyric_Time_tab


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
    INFORMATION_TAG_REGEX: Pattern = re.compile(r"^(\[)?(?P<tag>[a-zA-Z].*):(?P<tagcontent>.*)(])?$")

    # 正式歌词的正则表达式
    # 中括号可以缺失，但是冒号不能缺失，起始标签的括号必须是中括号
    # 分为两组
    # groups: (左括号，分，冒号，秒，冒号或者点，毫秒，右括号)[时间标签组]，歌词内容[歌词内容组]
    # 例如：[00:00.00]歌词内容
    LRC_CONTENT_REGEX: Pattern = re.compile(r"^(?P<time_tab>(\[)?(\d+)(:)(\d+)([.:])(\d*)(])?)?"
                                            r"(?P<lrc_content>.*)$")

    # 标准格式
    INFORMATION_TAG_REGEX_STANDARD: Pattern = re.compile(r"^(\[)(?P<tag>[a-zA-Z].*):(?P<tagcontent>.*)(])$")
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

        # 一级列表，每个元素为一行歌词
        self.lrc_lines_primary: list[str] = []
        # 二级列表，每个元素为一行歌词，每行歌词为一个列表，列表第一个元素为时间标签类或者None（表示只有内容），第二个元素为歌词内容
        self.lrc_lines_secondary: list[list[Optional[Lyric_Time_tab], str]] = []

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
            self.lrc_lines_primary = lrc_content.splitlines()
            # 去除空行
            self.lrc_lines_primary = [line for line in self.lrc_lines_primary if line.strip()]
        # 是列表，直接赋值，但是依然要去除空行（含只有空白字符的行）
        elif isinstance(lrc_content, list):
            self.lrc_lines_primary = [line for line in lrc_content if line.strip()]
        # 不是字符串也不是列表，抛出异常
        else:
            raise TypeError("lrc_content must be str or list divided by lines")

        # 调用信息分离处理函数，分离歌词内容和歌词信息
        # 传入参数为歌词内容的列表
        self.__lrc_information_content_separation(self.lrc_lines_primary, mode)

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
            tag_value = each_line_match.group("value")
            # 赋值
            setattr(self, tag_name, tag_value)

        # 如果不是，那么就是自定义的标签，储存到一个字典中
        else:
            # 获取标签名
            tag_name = each_line_match.group("tag")
            # 获取标签值
            tag_value = each_line_match.group("value")
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
        # 获取时间
        time = each_line_match.group("time")
        # 获取歌词
        lrc: str = each_line_match.group("lrc")

        # 判断时间 是否为空
        if time:
            time: Optional[Lyric_Time_tab.Lyric_Time_tab]
            time = Lyric_Time_tab.Lyric_Time_tab(each_line, mode)

        # 放入二级歌词列表中
        self.lrc_lines_secondary.append([time, lrc])


    @classmethod
    def split_general_time_and_lyric(cls,
                                     lrc_lines: str | list[str],
                                     mode: str
                                     ) -> list[list[Lyric_Time_tab.Lyric_Time_tab, str]]:
        """
            中文：
            在纯歌词内容的字符串或列表中，分离时间标签和歌词内容

            English:
            In the string or list of pure lyric content, separate the time tag and lyric content

            :param lrc_lines: 歌词内容的字符串 || the string of lyric content
            :param mode: 时间标签检查严格度，可选值为 "strict", "normal", "loose" 和 “very_loose”
                || The strictness of the time tag check,
                 the optional values are "strict", "normal", "loose" and "very_loose"
            :return: list[list[Lyric_Time_tab.Lyric_Time_tab, str]]
        """
        # 新的空列表
        output_list: list[str | list[Lyric_Time_tab.Lyric_Time_tab, str]]

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
            # 获取时间
            time = each_line_match.group("time")
            # 获取歌词
            lrc: str = each_line_match.group("lrc")

            # 判断时间 是否为空
            if time:
                time: Optional[Lyric_Time_tab.Lyric_Time_tab]
                time = Lyric_Time_tab.Lyric_Time_tab(lrc_lines, mode)

            # 覆盖原项，放入new_list中
            lrc_lines = [time, lrc]
            output_list[output_list.index(lrc_lines)] = lrc_lines

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
        return Lyric_file.judge_standard_form_classmethod(self.lrc_lines_primary)
