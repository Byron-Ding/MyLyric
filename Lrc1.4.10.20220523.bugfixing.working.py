import re  # as re
import sf  # as sf
import os
from typing import Optional
from typing import Union
from typing import Pattern
import typing
import Time_tab

# import _io


# constant

CONVERSION_TIME_60: int = 60
CONVERSION_TIME_100: int = 100
CONVERSION_TIME_1000: int = 1000

# 旧版  r'\[?\d*:\d{1,2}\.\d*]?.*'
general_match_for_both_info_and_lyric: Pattern[typing.AnyStr] \
    = re.compile(r'\['
                 r'.*'  # 规范里面说了，分钟位和秒钟位必须有数字
                 r':'  # 分钟 秒钟 之间必须有冒号 info也是冒号
                 r'.*'  # 毫
                 r']'  # 必须关闭 括号
                 r'.*')

# 旧版  r'\[?\d*:\d{1,2}\.\d*]?.*'
general_match_for_info: Pattern[typing.AnyStr] \
    = re.compile(r'\['

                 r'('  # 组一开始，代表信息属性
                 r'[^\d]'  # info 宽松模式 只要第一位不是数字就行，否则会和歌词部分格式冲突
                 r'.*'
                 r')'  # 组一结束

                 r':'  # 后面冒号分隔符

                 r'\d{0,2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error

                 r'('  # 组二开始，代表信息属性的对应字典
                 r'.*'  # 对应的字典随意字符
                 r')'  # 组二结束

                 # 必须关闭 括号
                 r']')

general_match_for_info_left_bracket_missing: Pattern[typing.AnyStr] \
    = re.compile(r'\[?'
                 r'('  # 组一开始，代表信息属性
                 r'[^\d]'  # info 宽松模式 只要第一位不是数字就行，否则会和歌词部分格式冲突
                 r'.*'
                 r')'  # 组一结束

                 r':'  # 后面冒号分隔符

                 r'\d{0,2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error

                 r'('  # 组二开始，代表信息属性的对应字典
                 r'.*'  # 对应的字典随意字符
                 r')'  # 组二结束

                 # 必须关闭 括号
                 r']')

general_match_for_info_right_bracket_missing: Pattern[typing.AnyStr] \
    = re.compile(r'\['
                 r'('  # 组一开始，代表信息属性
                 r'[^\d]'  # info 宽松模式 只要第一位不是数字就行，否则会和歌词部分格式冲突
                 r'.*'
                 r')'  # 组一结束

                 r':'  # 后面冒号分隔符

                 r'\d{0,2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error

                 r'('  # 组二开始，代表信息属性的对应字典
                 r'.*'  # 对应的字典随意字符
                 r')'  # 组二结束

                 # 必须关闭 括号 
                 r']?')

# Constant:
general_match_for_lyric_standard_form: Pattern[typing.AnyStr] \
    = re.compile(r'\['

                 r'('  # 组一开始，代表分钟
                 r'\d{2}'  # 规范里面说了，分钟位和秒钟位必须有数字
                 r')'  # 组一结束

                 r':'  # 分钟 秒钟 之间必须有冒号

                 r'('  # 组二开始，代表秒钟
                 r'\d{2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error
                 r')'  # 组二结束

                 r'.'  # . 在 [] 内会被自动转义 

                 r'('  # 组三开始，代表毫秒
                 r'\d{2}'  # 毫秒位可以缺失 
                 r')'  # 组三结束

                 r']'  # 必须关闭 括号
                 r'.*')

general_match_for_lyric: Pattern[typing.AnyStr] \
    = re.compile(r'\['

                 r'('  # 组一开始，代表分钟
                 r'\d+'  # 规范里面说了，分钟位和秒钟位必须有数字
                 r')'  # 组一结束

                 r':'  # 分钟 秒钟 之间必须有冒号

                 r'('  # 组二开始，代表秒钟
                 r'\d{0,2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error
                 r')'  # 组二结束

                 # 毫秒位可以缺失，考虑到有人用 ":" 隔开      ·目前先这样，之后遇到非预料情况再说
                 r'[.:]?'  # . 在 [] 内会被自动转义 

                 r'('  # 组三开始，代表毫秒
                 r'\d*'  # 毫秒位可以缺失 
                 r')'  # 组三结束

                 r']'  # 必须关闭 括号
                 r'.*')

general_match_for_lyric_left_bracket_missing: Pattern[typing.AnyStr] \
    = re.compile(r'\[?'

                 r'('  # 组一开始，代表分钟
                 r'\d+'  # 规范里面说了，分钟位和秒钟位必须有数字
                 r')'  # 组一结束

                 r':'  # 分钟 秒钟 之间必须有冒号

                 r'('  # 组二开始，代表秒钟
                 r'\d{0,2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error
                 r')'  # 组二结束

                 # 毫秒位可以缺失，考虑到有人用 ":" 隔开      ·目前先这样，之后遇到非预料情况再说
                 r'[.:]?'  # . 在 [] 内会被自动转义 

                 r'('  # 组三开始，代表毫秒
                 r'\d*'  # 毫秒位可以缺失 
                 r')'  # 组三结束

                 r']'  # 必须关闭 括号
                 r'.*')

general_match_for_lyric_right_bracket_missing: Pattern[typing.AnyStr] \
    = re.compile(r'\['

                 r'('  # 组一开始，代表分钟
                 r'\d+'  # 规范里面说了，分钟位和秒钟位必须有数字
                 r')'  # 组一结束

                 r':'  # 分钟 秒钟 之间必须有冒号

                 r'('  # 组二开始，代表秒钟
                 r'\d{0,2}'  # 可以处理>=60秒钟的秒 这是个bug， 应该报Error
                 r')'  # 组二结束

                 # 毫秒位可以缺失，考虑到有人用 ":" 隔开      ·目前先这样，之后遇到非预料情况再说
                 r'[.:]?'  # . 在 [] 内会被自动转义 

                 r'('  # 组三开始，代表毫秒
                 r'\d*'  # 毫秒位可以缺失 
                 r')'  # 组三结束

                 r']?'  # 必须关闭 括号
                 r'.*')


def version():
    v = 'Version 1.4.5.1.20210224'
    return v


# 或许可以 re.compile(r'\[?\d*:\d{1,2}\.\d*]?')
def convert_to_int(time_tag: str) -> int:
    """
    param time_tag:
        Time tag in string form
        字符串形式的时间标签
    :return:
        Return a time tab in millisecond form
        返回时间戳（毫秒计数）

    This function help to convert the time tab in lrc file into integer with 10×milliseconds.

    这个方法转换LRC的时间戳到整数

    This function is used in the tag of the standard form. if it is not in standard form,

    please use the one in the Time_tab object.

    请尽量使用标准时间戳格式

    input must be [ : . ] or without bracket

    输入必须符合规范 [ : . ]
    """

    minutes: int
    seconds: int
    milliseconds: int
    time_list_in_tab: list

    time_list_in_tab = [i for i in re.split(r'[\[\]:.]', time_tag) if i != '']

    '''
    后期改进
    注： 如果分钟大于3位建议报warning然后程序继续运行
    '''

    minutes = int(time_list_in_tab[0])
    seconds = int(time_list_in_tab[1])
    milliseconds = int(time_list_in_tab[2])

    time: int = (minutes * 60 * 100) + (seconds * 100) + milliseconds

    return time


def convert_to_tab(time_stamp_milliseconds: int, with_bracket: bool = False,
                   whether_decimal_place3: bool = False) -> str:
    """
    :param time_stamp_milliseconds:
        Input milliseconds time stamp;
        整数毫秒时间戳

    :param with_bracket:
        Whether there is a bracket after conversion;
        转换完是否有中括号

    :param whether_decimal_place3:
        Whether keep 3 decimal place in the millisecond position.(The standard is 2)
        毫秒位是否保留三位整数（标准格式是两位）

    :return:
        Return a time tab in string form.
        返回一个时间标签字符串

    This function help to convert the integer with milliseconds into the time tab in lrc file.

    这个方法将时间转换 以毫秒计数的时间戳到时间标签

    This function is only used in the tab of the standard form.

    这个function仅支持标准格式

    If it is not in standard form, please use the one in the Time_tab object.

    如果非标准格式，请使用 Time_tab 类（待完善）

    input must be a integer

    输入必须是整数
    """

    if type(time_stamp_milliseconds) != int:
        raise TypeError('time_milliseconds should be integer')

    minutes: str
    seconds: str
    millisecond: str
    time: str

    # 如果不是三位小数，毫秒位，直接 // 10 保留两位小数
    if not whether_decimal_place3:
        time_milliseconds = time_stamp_milliseconds % 1000 // 10
    else:
        time_milliseconds = time_stamp_milliseconds % 1000

    # 优化，通过格式化，将补0和转字符串操作合二为一。
    # 补位至两位
    str_minutes = "{time:0>2}".format(time=time_stamp_milliseconds // 1000 // 60)
    str_seconds = "{time:0>2}".format(time=time_stamp_milliseconds // 1000 % 60)
    str_millisecond = "{time:0>2}".format(time=time_milliseconds)

    # print(minutes, seconds, milliseconds)

    time = str_minutes + ':' + str_seconds + '.' + str_millisecond

    if with_bracket:
        time = '[' + time + ']'

    return time


class Lyric_file:
    """
    同时兼容文件和文件内容
    """

    def __init__(self,
                 lrc_file: Union[None, str, list[Union[list, str]]] = None,
                 mode: str = 'r+',
                 buffering=-1,
                 encoding: str = 'utf-8-sig',
                 errors=None,
                 newline=None,
                 closefd=True,
                 opener=None):

        # super().__init__()

        # ————————————————————————————————————————文件预处理（打开）区————————————————————————————————————————
        # 设置文件打开初始属性
        # 为后面的保存函数做准备    ##保存函数无法保存说文件已经被关闭的问题已经被解决
        # 这些是元组（目前未查明原因）
        # 需要补齐类型注解
        self.open_mode: tuple[str] = mode,
        self.open_buffering: tuple[int] = buffering,
        self.open_encoding: tuple[str] = encoding,
        self.open_errors: tuple = errors,
        self.open_newline = newline,
        self.open_closefd = closefd,
        self.open_opener = opener
        self.path: Optional[str] = None
        # 判断是否为类型
        self.input_type: Optional[str]
        if os.path.isfile(lrc_file):
            self.input_type = "file"
        elif type(lrc_file) == list:
            self.input_type = "list"
        else:
            self.input_type = "str"

        # 判断是否类型正确
        # 如果输入不是 str，则报错
        if type(lrc_file) not in [str, list]:
            raise TypeError("Should input str to the var lrc_file!")

        self.filename: Optional[str] = None
        self.file = None

        # 预 打开 文件，如果传路径
        # 如果是个路径
        if type(lrc_file) == str and self.input_type == "file":
            # 取路径最后部分（文件名）
            self.filename = re.split(r'[/\\]', lrc_file)[-1]
            # print(mode)

            self.file = open(lrc_file,
                             mode,
                             buffering,
                             encoding,
                             errors,
                             newline,
                             closefd,
                             opener
                             )

            # 如果 模式是 a， a+ 记得操作指针到开头，否则读取为空
            # 后面会操作回去的
            if 'a' in self.open_mode:
                self.file.seek(0)

            # self.text = f.read()
            # f.seek(0)
            self.path = lrc_file

        # 如果是路径不存在（包括别的字符串）,则判定为Lrc文本
        elif type(lrc_file) == str and not os.path.isfile(lrc_file):
            # self.path 已经赋值为 None 了，不需要改动
            pass
        # 是列表的话暂时放着
        elif type(lrc_file) == list:
            pass
        # 空直接pass
        elif lrc_file is None:
            pass
        # ————————————————————————————————————————文件预处理（打开）区————————————————————————————————————————

        # ————————————————————————————————————————属性区————————————————————————————————————————
        self.artist: Optional[str]
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

        # 提前建立所有标签的列表，字典可能会乱序，为后面json做准备
        self.lrc_basic_property: list = [
            self.artist,
            self.album,
            self.lyric_writer,
            self.lrc_file_writer,
            self.length,
            self.offset,
            self.creating_software,
            self.title,
            self.version,
            self.kana
        ]

        # ————————————————————————————————————————属性区————————————————————————————————————————

        # ————————————————————————————————————————歌词处理区————————————————————————————————————————
        # 按行分割的 Lrc 内容列表
        self.pure_lyric_lines: Optional[list[str]] = None

        # 如果是个文件，处理其内容
        # 前面已经打开了文件，读取了内容
        # ########## 前面打开文件的时候已经判断了非字符串情况，会报错的，这里不用判断了
        if self.input_type == "file":
            self.pure_lyric_lines = self.__separate_basic_information(self.file.read())

            # self.extend(self.pure_lyric_lines)
            # 如果本来就是 a 或者 a+ 直接忽略
            if 'a' in self.open_mode:
                pass
            # 读完文件，恢复文件指针到开头
            else:
                self.file.seek(0)

            # 是否为标准格式
            self.__judge_standard_form()

        # 如果是文本，直接处理
        elif not os.path.isfile(lrc_file):
            self.pure_lyric_lines = self.__separate_basic_information(lrc_file)

            # 是否为标准格式
            self.__judge_standard_form()

        # 如果是个包含lrc歌词的列表，判断正误
        # ########## BUG， 注意 如果这个列表包含歌词的基本属性信息
        elif type(lrc_file) == list:
            # 每一行是否符合规范
            # 不符合规范就没法匹配，直接返回None 然后转为0
            # 储存对象导致太大，直接当场判断掉
            temp_list = [0 if re.match(general_match_for_lyric, each_line) else 1
                         for each_line in lrc_file]

            # 判断格式是否标准
            if any(temp_list):
                raise TypeError('The list is not in format. The lines do not pass the judgement!')
            else:
                self.pure_lyric_lines = lrc_file

        # 空的话直接创建空对象
        elif lrc_file is None:
            self.__separate_basic_information('')
        # ————————————————————————————————————————歌词处理区————————————————————————————————————————

        # ————————————————————————————————————————杂项区————————————————————————————————————————
        # 字典，方便查找
        self.tag_dic_long_short: Optional[dict[str, str]] = {'artist': 'ar',
                                                             'album': 'al',
                                                             'lyric_writer': 'au',
                                                             'lrc_file_writer': 'by',
                                                             'length': 'length',
                                                             'offset': 'offset',
                                                             'creating_software': 're',
                                                             'title': 'ti',
                                                             'version': 've',
                                                             'kana': 'kana'  # 日语歌词专用，不确定具体含义
                                                             }

        self.tag_dic_short_long: Optional[dict[str, str]] = {'ar': 'artist',
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

        # 定义__next__返回下一个的初始化[clc]
        # 用于自我迭代
        self.__next_clc: int = 0

        # 获取是否为拓展LRC格式
        self.whether_extension: bool = False

        # 已经移回去了
        """
        # 前面 操作了 a, a+ 模式下的指针，现在操作回去
        if 'a' in self.open_mode:
            # 第一个参数代表偏移量
            # 第二个参数代表从文件开头开始算起，1代表从当前位置开始算起，2代表从文件末尾算起。
            self.file.seek(0, 2)
        """
        # ————————————————————————————————————————杂项区————————————————————————————————————————

    # 定义len方法时的操作
    def __len__(self):
        if self.pure_lyric_lines is None:
            return None
        else:
            return len(self.pure_lyric_lines)

    # 定义获取属性时的操作
    def __getitem__(self, key):
        if self.pure_lyric_lines is None:
            raise TypeError("The lyric lines list is None. Not iterable!")
        else:
            return self.pure_lyric_lines[key]

    # 定义属性赋值时的操作
    # 不能再该方法内赋值 self.name = value 会死循环
    def __setitem__(self, key, value):
        if self.pure_lyric_lines is None:
            raise TypeError("The lyric lines list is None. Not iterable!")
        else:
            self.pure_lyric_lines[key] = value

    # 定义删除属性的操作
    def __delitem__(self, key):
        if self.pure_lyric_lines is None:
            raise TypeError("The lyric lines list is None. Not iterable!")
        else:
            del self.pure_lyric_lines[key]

    # 定义迭代器
    def __iter__(self):
        """
        text = lrc_file.read()

        full_lyric_list = re.split(r'\n',text)

        return full_lyric_list[0]
        """
        if self.pure_lyric_lines is None:
            raise TypeError("The lyric lines list is None. Not iterable!")
        else:
            return self

    # 返回下一个迭代值
    def __next__(self):
        if self.pure_lyric_lines is None:
            raise TypeError("The lyric lines list is None. Not iterable!")
        else:
            try:
                item_returned = self.pure_lyric_lines[self.__next_clc]

            except IndexError:
                # 想要停止迭代那么就报如下错误即可。
                self.__next_clc = 0
                raise StopIteration

            self.__next_clc += 1

            return item_returned

    def __separate_basic_information(self, origin_lrc_text: str) -> list:
        """
        This function separate the basic information and the lyric lines

        这个方程勇于分开原本的

        :param origin_lrc_text:
        :return:
        """
        lines: list
        lyric_list_without_information: list

        # 获取是否为拓展LRC格式
        if (re.search(r'<?\d*:\d{1,2}\.\d*>', origin_lrc_text) is not None
                or
                re.search(r'<\d*:\d{1,2}\.\d*>?', origin_lrc_text) is not None):
            self.whether_extension = True

        # 自动删除空行
        lines = [i for i in re.split(r'\n|\r|\r\n', origin_lrc_text) if i]
        # 分离标签信息
        lyric_list_without_information = []

        for line in lines:
            # type_of_num_head = re.match(r'\[\d', line)

            # Future：注意有 左右括号缺失 的容错，但还没添加
            if matched_line_obj := re.match(general_match_for_info, line) is not None:
                info_key_name = matched_line_obj.group(1)
                info_value_name = matched_line_obj.group(2)

                each_sentence = 'self.' + info_key_name + '=' + info_value_name \
                                + '\n' \
                                + 'if ' + 'self.' + info_key_name + ' not in self.lrc_basic_property:' \
                                + '    self.lrc_basic_property.append(' + 'self.' + info_key_name + ")"
                print(each_sentence)
                del info_key_name, info_value_name
                # 将lrc的属性值变成本对象的属性值
                exec(each_sentence)

            # 标准格式 [ : . ]
            # 其他格式① [ : ]
            # 其他格式② [ : : ]
            # Future：注意有 左右括号缺失 的容错，但还没添加
            elif re.match(general_match_for_lyric, line) is not None:
                # 不要冒号直接报错先，后期再想办法填补试图标准化
                if ":" not in line:
                    raise TypeError("':' not existed")
                # 要添加''
                # if re.match(r'\[')
                lyric_list_without_information.append(line)

            # 没写ELSE, 已经去除了空行和不符合规范的行

        return lyric_list_without_information

    def __judge_standard_form(self):

        self.standard_form: set = set()

        for i in self.pure_lyric_lines:

            if i == '':
                continue

            if re.fullmatch(general_match_for_lyric_standard_form, i) is not None:
                self.standard_form.add('standard form')

                if re.fullmatch(r'\[\d*:\d*\.\d{3}].*', i) is not None:
                    self.standard_form.add('3 decimal places')

                    if re.fullmatch(r'\[\d{3,}:\d*\.\d*].*', i) is not None:
                        self.standard_form.add('larger than 99 minutes')
                    else:
                        self.standard_form.add('Other not standard form')

    def split_general_time_and_lyric(self, lyric_list: None or list = None, with_time_bracket: bool = False) -> list:

        """
        'lyric_list' must be a list of lyric lines splitted by lines.(A primary list)
        
        with_time_bracket means whether the time tab having bracket in output.
        
        This function not only fill the blank lyric into '',
        but also do a further split in each element.

        It also deletes the blank line automatically.
        
        output:
            [[time,lyric],[time,lyric],[time,lyric],[time,lyric]...]
        """

        # lyric = full_lyric_list = re.split(r'\n',text)

        if lyric_list is None:
            lyric_list = self.pure_lyric_lines

        # 正常函数
        # 准备最外层嵌套的空列表
        # ☆★同时具备深拷贝的功能，防止原始文件列表被修改
        lyric_splitted = []
        for lyric_line in lyric_list:
            # i for i in XX if XX 可以写成一行
            line_splitted: list = [i for i in re.split(r'[\[\]]', lyric_line) if i != '']

            # 执行附加条件（可选参数）
            # 判断是否要括号
            if with_time_bracket:
                line_splitted[0] = '[' + line_splitted[0] + ']'

            lyric_splitted.append(line_splitted)

        # print(lyric_splitted)

        # 纠正歌词为空的i情况
        clc: int = 0
        while clc < len(lyric_splitted):
            if len(lyric_splitted[clc]) == 1:
                lyric_splitted[clc].append('')
            clc += 1

        return lyric_splitted

    '''
    def further_splitting(self,secondary_list:list):
        return_list = [ [i[0], re.split('[<>]',i[1])[1:] ] for i in secondary_list]
        return return_list
    '''

    # ########## 准备修补
    def calculate_all_translated_time_tab(self,
                                          lyric_list: list = None,
                                          ignore_blank: bool = False,
                                          numerator: int = 0,
                                          denominator: int = 1,
                                          line_shift: int = 0,
                                          last_limit: int = 0) -> list:
        """
        This function let you add translation between the lyrics

        |||ATTENTION The format of lyric_list must be the secondary list!!|||

        ignore_blank means whether ignore the blank lyirc which has only a time tab.

        numerator/denominator is the way to calculate the new translated time tab.

        line_shift is the start line of lyric, in order to avoid the head information but with time tab.

        last_limit is the last time tab to calculate(in milliseconds).

        (without the basic information)
        lyric_list = [[time,lyric],[time,lyric],[time,lyric]...]

        It return a secondary list.
        """
        # 可以控制已经翻译的行数来插入%^%

        # 提前判断除数是否为0
        if denominator == 0:
            raise ZeroDivisionError('the "denominator" cannot be 0')

        if lyric_list is None:
            lyric_list = self.split_general_time_and_lyric()

        # 处理最后一项
        Temp_tab = Time_tab(lyric_list[-1][0])
        temp = Temp_tab.convert_to_time_stamp()
        temp = Temp_tab.convert_to_tab(temp + last_limit, with_bracket=False)

        lyric_list.append([temp, ''])

        # 定义头部
        time_tab_list_of_translated = []

        clc = line_shift

        while True:
            try:
                if lyric_list[clc][1] != '':
                    before = lyric_list[clc][0]
                    after = lyric_list[clc + 1][0]

                    time_before: int
                    time_after: int

                    time_before = convert_to_int(before)
                    time_after = convert_to_int(after)
                    # 计算差值
                    add_time: int
                    add_time_float: float

                    add_time_float = (time_after - time_before) * \
                                     numerator / \
                                     denominator
                    # 取整
                    # 保留两位有效数字
                    ##$$
                    add_time = int(sf.significant_figure(add_time_float, 2))
                    ##$$

                    translated_time = time_before + add_time
                    # 返回无括号时间标签
                    translated_time_tab = convert_to_tab(translated_time)
                    # 加入列表
                    time_tab_list_of_translated.append(translated_time_tab)
                    # 计算下一个
                    # 可以修改%^%
                    clc += 1
                    # print(time_before,time_after,add_time,translated_time,translated_time_tab)
                else:
                    clc += 1
                    # 如果忽略空行歌词为（假的假）【不忽略空格】
                    if not ignore_blank:
                        time_tab_list_of_translated.append('')

            except IndexError:
                break

        return time_tab_list_of_translated

    def format_lyric_return_list(self, lyric_list=None,
                                 length_of_millisecond: int = 2,
                                 with_bracket=True) -> list:

        """
        It is used to format the time tab having un-standard format,
        such as [xx:xx.xxx]

        It return a secondary list.
        """

        if lyric_list == None:
            lyric = self.split_general_time_and_lyric()

        else:
            lyric = self.split_general_time_and_lyric(lyric_list)

        temp_full_list = []

        for i in lyric:
            # [[, ],[, ],[, ],[, ]...]
            no_milliseconds = False
            no_minutes = False

            if '.' not in i[0]:
                no_milliseconds = True
            if ':' not in i[0]:
                no_minutes = True

            i[0] = re.split(r'[:\.]', i[0])

            if no_minutes:
                i[0].insert(0, '00')
            if no_milliseconds:
                i[0].append('00')

        for i in lyric:
            # 处理时间标签格式不规范

            # 默认有数字
            if len(i[0][0]) < 2:
                i[0][0] = i[0][0].zfill(2)

            if len(i[0][1]) < 2:
                i[0][1] = i[0][1].zfill(2)

            if len(i[0][2]) < length_of_millisecond:
                i[0][2] = i[0][2].ljust(length_of_millisecond, '0')

            # 处理最经常的错误（毫秒位有三位及以上）
            elif len(i[0][2]) > length_of_millisecond:

                str_millisecond = i[0][2]

                left = i[0][2][:length_of_millisecond]
                right = i[0][2][length_of_millisecond:]

                if int(right[0]) >= 5:
                    left = str(int(left) + 1)
                    # 补回因为int 失去的0
                    left = left.zfill(length_of_millisecond)

                i[0][2] = left

        for i in lyric:
            i[0] = i[0][0] + ':' + \
                   i[0][1] + '.' + \
                   i[0][2]

        if with_bracket:
            for i in lyric:
                i[0] = '[' + i[0] + ']'

        return lyric

    def add_translate(self,
                      lyric_list: list = None,
                      time_tab_list_of_translated: list = None,
                      list_of_translate: list = None,
                      line_shift: int = 0,
                      whether_ignore_blank: bool = False
                      ) -> list:
        # 可以增加translte_step = 1（翻译步长）可以判断是否大于0，要不然死循环

        if lyric_list == None:
            lyric_list = self.split_general_time_and_lyric()

        else:
            lyric_list = self.split_general_time_and_lyric(lyric_list)

        clc: int = 0

        # time_tab_list_of_translated = []

        """
        if len(time_tab_list_of_translated) != len(list_of_translate):
            raise 
        """
        clc: int = 0
        translated_lyric_line_list: list = []
        while True:
            conbined_list: list = []
            # 可以加入显示那个长度长（歌词长度，时间长度不匹配）
            try:
                # 合并时间 与 歌词
                conbined_list.append(time_tab_list_of_translated[clc])
                conbined_list.append(list_of_translate[clc])
                # 加入总翻译列表
                translated_lyric_line_list.append(conbined_list)
            except IndexError:
                break

            # 下一轮循环
            clc += 1

        clc: int = 1
        new_lyric_list: list = []

        while True:
            # 大循环，当有一个歌词超出列表范围的时候，报错，并退出循环
            try:
                # 忽略空歌词
                if not whether_ignore_blank:
                    # 判断是否有此项，否则后面continue会导致死循环。
                    # 为了代码便于理解，此处有括号。
                    assert (lyric_list[clc] and translated_lyric_line_list[clc])

                    # 情况一，没有此项（空）。
                    try:
                        lyric_list[clc][1]
                    except IndexError:
                        continue
                    else:
                        # 情况二，此项为空。
                        if not lyric_list[clc][1]:
                            continue

                        new_lyric_list.append(lyric_list[clc])
                        new_lyric_list.append(translated_lyric_line_list[clc])

                    finally:
                        clc += 1
                # 不忽略空歌词
                elif whether_ignore_blank:

                    new_lyric_list.append(lyric_list[clc])
                    new_lyric_list.append(translated_lyric_line_list[clc])

                    clc += 1

            except IndexError:
                break

        return new_lyric_list

    def simple_lrc(self, lyric=None) -> list:
        '''
        It simplify the whole lyric file by conbining same lyrics but having different time tab.
        The 'lyric' must be in format:(primary list)
            lyric = [lyric_line,lyric_line,lyric_line...]

        It return a secondary list.
        '''

        if lyric == None:
            lyric = self.pure_lyric_lines

        # 进一步分割列表
        list_splited = self.split_general_time_and_lyric(lyric, True)

        insert_order_of_tiem_tab = 0

        # 创建空列表
        reflaction = []
        '''
        for lyric_line_list in lyirc:
            pure_lyric = [lyric_line_list[-1]]
            reflaction.append(pure_lyric)
            
            for lyric_line_list1 in lyirc:
                time_tab = lyric_line_list1[0]
                if lyric_line_list1[-1] == pure_lyric:
                    pass
        '''

        clc, cli, tl = 1, 1, len(list_splited)

        # 修BUG 时间添加倒置
        for lyric_line_list in list_splited:

            lrc = lyric_line_list[1]
            order_ori = list_splited.index(lyric_line_list)

            for j in range(clc, tl):
                # 当列表元素大于列表长度上限，直接退出一轮循环
                if j >= len(list_splited):
                    # print(j)
                    # continue 或许可以优化为 break
                    continue
                if lrc == list_splited[j][1]:
                    # print(list_splited[j][0])
                    # order = lyric.index(i)
                    list_splited[order_ori].insert(cli, list_splited[j][0])
                    cli += 1
                    del list_splited[j]
                    tl -= 1

            cli = 1
            clc += 1

        return list_splited

    def complex_lrc_into_standard_form(self, lyric=None, insert_after_lastly=None) -> list:

        '''
        The lyric should be a first ordered list with each line of the lyric as an element without the basic information.
        lyric = [[lyric_line],[lyric_line],[lyric_line]...]

        insert_after_lastly is the way of adding the same lyric into the right order while having the same time tab,

        which has three choises:
            None means that insert in the place which the lyric has the same time tab.
            'after' means that insert in the place which the lyric has the same time tab +1.
            '←' means that insert in the place if the last way of finding is towards the smaller place, then +1.
            '→' means that insert in the place if the last way of finding is towards the larger place, then +1.

        It return a secondary list.
        '''
        len_of_ori_list: int  # 原列表长度
        extra_time_tab: list  # 插入的时间列表

        if lyric == None:
            # 不可以对该列表有任何修改，这没在内存中拷贝。
            # split_general_time_and_lyric 已经新建列表，可以修改%^%
            list_splited = self.split_general_time_and_lyric()

        else:
            list_splited = lyric

        # 提取时间及其对应歌词，并防止修改源列表。
        extra_time_tab = []

        for line in list_splited:
            clc_of_element = 0

            for element in line:
                # 忽略首个（原始标签）
                if line.index(element) == 0:
                    continue

                if re.match(r'\[?\d*:\d{1,2}\.\d*]?', element) != None:
                    # 创建新列表，不在源列表上提取，并且合并歌词和标签
                    iner_list = [element, line[-1]]

                    extra_time_tab.append(iner_list)

        # 测试代码
        '''
        for i in j:
            for k in i:
                if i.index(k) == 0:
                    continue
                u = re.match(r'[(\[\d\d:\d\d\.\d\d\])(\d\d:\d\d\.\d\d)]',k)
                if u != None:
                     print(u)
        
        '''
        # 转换要插入的列表的所有的时间至整数
        for item in list_splited:
            # 记住查找所有时间标签
            for i in item:
                order_of_item = list_splited.index(item)

                if re.match(r'\[?\d*:\d{1,2}\.\d*]?', i) != None:
                    # item[0] = convert_to_int(item[0])
                    order_of_i = item.index(i)
                    list_splited[order_of_item][order_of_i] = convert_to_int(i)

        # 转换插入时间为整数
        for line in extra_time_tab:
            line[0] = convert_to_int(line[0])

        # 二分法核心算法！！！
        # 遍历时间列表
        '''
        列表取中
        如果大于原来的值向左//2
        1！设置值（）
        如果小于则(len-position)//2 +position
        1！设置值（）
        如果等于那么写入后面（默认），可以增加一个参数。
        1！设置值（）

        判断两次列表index是否相同，相同则
        比较插入值和原值大小，
        大于原值则在后面写入，
        小于原值在前面写入

        1！设置值（初始化）
        '''

        # 设置从左插入，从右插入。
        # 可以增加纯列表参数，重新拷贝列表
        def half_insertion(secondary_list_inserted, insert_time_list, insert_after_lastly) -> list:  # 已在外部函数输入，不需要默认值

            # insert_time_list是一个二维列表，第一位是时间，第二位是歌词
            for i in insert_time_list:
                # 初始化，用于后期定位歌词位置，列表长度在变
                high = len(secondary_list_inserted) - 1  # 插入的位置
                low = 0
                position_inserted = (high + low) // 2

                # 设置死循环，条件退出
                while True:

                    # 比较大小
                    if i[0] < secondary_list_inserted[position_inserted][0]:

                        high = position_inserted
                        position_inserted = (high + low) // 2

                        approaching = '←'

                        # print(0.1)
                    elif i[0] > secondary_list_inserted[position_inserted][0]:
                        # print(i[0],secondary_list_inserted[position_inserted][0],2)
                        low = position_inserted
                        position_inserted = (high + low) // 2

                        approaching = '→'

                        # print(0.2)

                    # 设置从左插入，从右插入。
                    # 位置一样，数值也一样。
                    elif i[0] == secondary_list_inserted[position_inserted][0]:
                        # print(i[0],secondary_list_inserted[position_inserted][0],3)

                        '''
                        #如果歌词和当前一样往后插入
                        if insert_after_lastly =='auto':
                            if i[1] == secondary_list_inserted[position_inserted][1]:
                                position_inserted += 1
                        '''
                        if insert_after_lastly == None:
                            pass

                        # 当最后一次查找方向从。。。往后插入
                        elif insert_after_lastly == 'right_to_left':
                            if approaching == '←':
                                position_inserted += 1

                        elif insert_after_lastly == 'left_to_right':
                            if approaching == '→':
                                position_inserted += 1

                        # 全部往后插入
                        elif insert_after_lastly == 'after':
                            position_inserted += 1

                        # 插入整行
                        secondary_list_inserted.insert(position_inserted, i)
                        # 插入完成，退出循环，开始下一个数。

                        # print(0.3)

                        break

                    # 判断位置是否重复（被锁定位置）
                    # 位置一样，但是数值不一样
                    # or 左右如果是数字那么直接0为Flase。。。
                    if position_inserted == high or position_inserted == low:

                        # 为考虑代码可读性，不合起来操作了。
                        # 如果小于原数值，则直接插入。
                        if i[0] < secondary_list_inserted[position_inserted][0]:

                            # 插入整行
                            secondary_list_inserted.insert(position_inserted, i)

                            # print(1.1)
                            break

                        # 如果大于原数值，则往后插入。
                        elif i[0] > secondary_list_inserted[position_inserted][0]:
                            position_inserted += 1

                            # 插入整行
                            secondary_list_inserted.insert(position_inserted, i)

                            # print(1.2)
                            break
                '''
                if not (secondary_list_inserted[position_inserted-2][0] < i[0] < secondary_list_inserted[position_inserted+2][0]):
                    raise AssertionError
                '''
            # 其实不需要return，因为insert 已经修改了二维列表        
            return secondary_list_inserted

        list_splited = half_insertion(list_splited, extra_time_tab, insert_after_lastly)

        # 将时间转换为时间标签

        for l in list_splited:
            l[0] = convert_to_tab(l[0], True)

        def removed_all_transfered_time(secondary_list_inserted) -> list:
            # 因为没有把多余的标签转换回str ， 通过这个删除不需要的元素
            for line in secondary_list_inserted:
                order1 = secondary_list_inserted.index(line)
                # len_of_line = len(line)
                '''
                for i in line:
                    if type(i) == int:
                        order2 = line.index(i)
                        del secondary_list_inserted[order1][order2]

                '''
                order2 = 0
                while True:
                    try:
                        # print(line[order2],type(line[order2]))
                        if type(line[order2]) == int:
                            del secondary_list_inserted[order1][order2]
                        else:
                            # 因为for 函数和while 一样 删除之后序号还是会加+1
                            # 这里删除元素之后序号不变，不需要序号加一
                            order2 += 1
                    except IndexError:
                        break

            return secondary_list_inserted

        list_splited = removed_all_transfered_time(list_splited)

        return list_splited

    # 没考虑只有歌词标签的情况，需要修改

    def get_all_time_tab(self, lyric=None, whether_pure_time=True) -> list:
        # 可以考虑增加with_braket参数。
        '''
        The lyric should be a secondary list.
        
        It return a list with all time tab.
        '''

        pure_time_tab_list: list
        element_list: list

        # lyric = Lrc_object.read()

        if lyric == None:
            lyric = self.pure_lyric_lines

        # 进一步分割列表
        list_splited = self.split_general_time_and_lyric(lyric)

        # 定义返回时间空列表
        # ☆★同时具备深拷贝的功能，防止原始文件列表被修改

        pure_time_tab_list = []
        # 加入元素
        for i in list_splited:
            element_list = []

            for j in i:
                if re.match(r'\[?\d*:\d{1,2}\.\d*]?', j) != None:
                    element_list.append(j)

            pure_time_tab_list.append(element_list)

        if not whether_pure_time:
            # 可以递归，但这里只有两层，目前没必要 def add()... return add()
            for i in pure_time_tab_list:
                order1 = pure_time_tab_list.index(i)

                if type(i) == str:
                    pure_time_tab_list[order1] = '[' + i + ']'

                elif type(i) == list:
                    for j in i:
                        order2 = i.index(j)
                        pure_time_tab_list[order1][order2] = '[' + j + ']'

        return pure_time_tab_list

    def shift_time(self, minutes, seconds, milliseconds, splited_lyrics=None) -> list:
        '''
        Tag should be in standard form.([  :  .  ])
        The splited_lyrics shoul be a secondary list.
        
        It returns a list after time shifting.
        '''

        if splited_lyrics == None:
            splited_lyrics = self.split_general_time_and_lyric()

        for i in splited_lyrics:
            order_of_i = splited_lyrics.index(i)

            tab = Time_tab(i[0])  # 似乎不用转化成类了，直接利用函数代入。但是失败了

            # time_list = re.split(r'\[|]',i[0])[0]

            time_output = tab.shift_time(minutes,
                                         seconds,
                                         milliseconds
                                         )

            splited_lyrics[order_of_i][0] = time_output

        return splited_lyrics

    # #########到json
    def to_json(self, lyric_text: None or list = None):
        if lyric_text == None:
            lyric_text = self.split_general_time_and_lyric()

        else:
            pass

        main_dict: dict = {}

        # for i in

    # 未测试,已经增加 headline=0 可以分开 #基本信息没有添加
    def to_srt(self, lyric_text: None or list = None, numerator=1, denominator=1, headline=0, save_into_a_file=False,
               whether_blank=False, translate_line=None) -> list or None:
        '''
        Return a secondary list include splited lyrics for each element.
        OR save it as a srt file with same name to the name of lrc file and return nothing. 
        '''
        if translate_line == None:
            translate_line = 1

        # if translate_line < 1:
        # raise translate_line

        if lyric_text == None:
            lyric_text = self.pure_lyric_lines
            # 初始分割成二维列表
            lyric_text = self.split_general_time_and_lyric(lyric_text)

        #
        def change_time_into_srt_form(time_list) -> list:
            # 纠正毫秒位在srt中为三位
            if len(time_list[2]) < 3:
                time_list[2] = time_list[2].ljust(3, '0')

            elif len(time_list[2]) > 3:
                # 简易取整，不用自己写的sf模块。
                if int(time_list[2][4]) >= 5:
                    time_list[2] = str(int(time_list[:3] + 1))

                elif int(time_list[2][4]) < 5:
                    time_list[2] = str(int(time_list[:3]))

            # 象征性的写一下，方便后期逻辑
            elif int(time_list[2]) == 3:
                pass

            # 纠正在srt中有小时位

            if int(time_list[0]) >= 60:
                # 自动转换为字符串类型
                hours = str(int(time_list[0]) // 60)
                minutes = str(int(time_list[0]) % 60)

                # 长度为一时补为两位
                if len(hours) == 1:
                    hours = '0' + hours

                if len(minutes) == 1:
                    minutes = '0' + minutes

                # 替换分钟位
                time_list[0] = minutes
                # 增加小时位
                time_list.insert(0, hours)

            else:
                time_list.insert(0, '00')

            return time_list

        # 设置计数器，srt文件要计数器
        clc_line: int = 0  # 列表计数器
        clc_order_of_subtitle: int = 1  # SRT字幕计数器
        srt_list = []

        # 需要加上
        # 第一轮循环是基本信息，
        # 第二轮循环是跳过开头的几行信息（带有标签）
        while True:
            # 每个部分（歌词）一个列表
            # str转序号为字符串，为后边写入文件做准备
            each_part = [str(clc_order_of_subtitle)]
            clc_order_of_subtitle += 1  # 字幕序号加一

            # 本段时间
            try:
                This_time_tab = Time_tab(lyric_text[clc_line][0])

            except IndexError:
                break

            this_time_stamp = This_time_tab.convert_to_time_stamp(len_of_millisecond=This_time_tab.len_of_millisecond)
            # 下段时间
            try:
                # ③如果有开头，又是第一次循环，则设定headline。
                if (headline > 0) and (clc_order_of_subtitle == 1):
                    Next_time_tab = Time_tab(lyric_text[clc_line + headline][0])
                else:
                    Next_time_tab = Time_tab(lyric_text[clc_line + translate_line][0])
                out_of_range = False

            except IndexError:
                # ②如果超出范围，取原数值+2.5s，实例化原数值
                Next_time_tab = Time_tab(lyric_text[clc_line][0])
                out_of_range = True

            next_time_stamp = Next_time_tab.convert_to_time_stamp(len_of_millisecond=Next_time_tab.len_of_millisecond)

            # 解决小数位数前后两项不一样
            if This_time_tab.len_of_millisecond == Next_time_tab.len_of_millisecond:
                len_of_millisecond = This_time_tab.len_of_millisecond

            elif This_time_tab.len_of_millisecond > Next_time_tab.len_of_millisecond:
                next_time_stamp = int(str(next_time_stamp).ljust(
                    This_time_tab.len_of_millisecond,
                    '0'))

                len_of_millisecond = This_time_tab.len_of_millisecond

            elif This_time_tab.len_of_millisecond < Next_time_tab.len_of_millisecond:
                #
                this_time_stamp = int(str(this_time_stamp).ljust(
                    Next_time_tab.len_of_millisecond,
                    '0'))

                len_of_millisecond = Next_time_tab.len_of_millisecond

            # ②超出范围（最后一项+2.5s（可增加参数可调））
            if out_of_range:
                next_time_stamp = next_time_stamp + int(10 ** len_of_millisecond * 2.5)

            # 计算歌词持续显示的结束时间
            middle_time_stamp: float = this_time_stamp + \
                                       (next_time_stamp - this_time_stamp) * \
                                       numerator / \
                                       denominator

            this_time_list = This_time_tab.time_list
            # This_time_tab是Time_tab的实例化对象
            middle_time_tab = Time_tab.convert_to_tab(middle_time_stamp, len_of_millisecond, with_bracket=False)

            middle_time_list = re.split(r'\.|:', middle_time_tab)

            this_time_list = change_time_into_srt_form(this_time_list)
            middle_time_list = change_time_into_srt_form(middle_time_list)

            # 拼接字符串
            srt_time = \
                this_time_list[0] + ':' + \
                this_time_list[1] + ':' + \
                this_time_list[2] + ',' + \
                this_time_list[3] + \
                '-->' + \
                middle_time_list[0] + ':' + \
                middle_time_list[1] + ':' + \
                middle_time_list[2] + ',' + \
                middle_time_list[3]

            # 添加时间行
            each_part.append(srt_time)
            # 添加歌词字幕行
            # 依次添加翻译行（忽略除第一行的歌词）
            try:
                # ③如果有开头，又是第一次循环，则headline个歌词全部合并。#后期可以试图增加外部参数拆分。
                if (headline > 0) and (clc_order_of_subtitle == 1):
                    number_of_lyrics = headline
                else:
                    number_of_lyrics = translate_line
                for i in range(0, number_of_lyrics):
                    each_part.append(lyric_text[clc_line + i][1])

            # 如果超出（行数不为整数（未翻译完全）），忽略。
            except IndexError:
                pass

            # 添加空行
            if whether_blank:
                each_part.append('\n')

            # 添加是各个元素
            srt_list.append(each_part)

            # 计数器加上歌词行数，添加下一行。（列表计数器）
            # ③如果有开头，又是第一次循环，则跳过headline个歌词（步长为 headline）。
            if (headline > 0) and (clc_order_of_subtitle == 1):
                clc_line += headline
            else:
                clc_line += translate_line

        # 如果是保存到文件选项
        if save_into_a_file:
            # 提取文件名
            ##########需要和os.path.split os.path.splitext 比较一下速度
            name: list
            name = re.split(r'\\|/', self.filename)[-1]
            # name = re.split(r'../../../Python/C-python', name)
            if len(name) != 1:
                name.pop()
                real_name = ''
                for i in name:

                    if i == name[-1]:
                        real_name = real_name + i
                    else:
                        real_name = real_name + i + '.'
            else:
                real_name = name[1]

            # 加后缀名
            real_name += '.srt'

            # 可以优化效率，提前合并字符串？
            # 可以设置文件编码encoding，后期更新。
            with open(real_name, 'a') as f:
                for i in srt_list:
                    subtitle_group = ''
                    # j代表组里面的每一行，每一行换行隔开
                    for j in i:
                        subtitle_group = subtitle_group + j + '\n'

                    f.write(subtitle_group)

        elif not save_into_a_file:
            return srt_list

    def save_as(self,
                path: str,
                mode='w',
                buffering=-1,
                encoding='utf-8-sig',
                errors=None,
                newline=None,
                closefd=True,
                opener=None) -> None:
        '''
        Save_the_lrc use attributions.
        Remember the self.pure_lyric_lines should be a primary list.
        歌词主体格式必须是按行分割的一级列表。
        '''
        file = open(path,
                    mode,
                    buffering,
                    encoding,
                    errors,
                    newline,
                    closefd,
                    opener)

        information_list = ['']

        # 将信息组合成列表
        if self.artist != None:
            artist = '[ar:' + self.artist + ']'
            information_list.append(artist)

        if self.album != None:
            album = '[al:' + self.album + ']'
            information_list.append(album)

        if self.lyric_writer != None:
            lyric_writer = '[au:' + self.lyric_writer + ']'
            information_list.append(lyric_writer)

        if self.lrc_file_writer != None:
            lrc_file_writer = '[by:' + self.lrc_file_writer + ']'
            information_list.append(lrc_file_writer)

        if self.kana != None:  # 日语歌词专用，不确定具体含义
            tag_kana = '[kana:' + self.kana + ']'
            information_list.append(tag_kana)

        if self.length != None:
            length = '[length:' + self.length + ']'
            information_list.append(length)

        if self.offset != None:
            offset = '[offset:' + self.offset + ']'
            information_list.append(offset)

        if self.creating_software != None:
            creating_software = '[re:' + self.creating_software + ']'
            information_list.append(creating_software)

        if self.title != None:
            title = '[ti:' + self.title + ']'
            information_list.append(title)

        if self.version != None:
            version = '[ve:' + self.version + ']'
            information_list.append(version)

        # 写入信息
        for information in information_list:
            if information == '':
                pass
            else:
                information += '\n'

                # ①防止出现编码BUG而保留这一行作为备选项，方便应急修改。
                # information = information.encode(self.open_encoding[0]).decode(self.open_encoding[0])

                file.write(information)

        # 计数，最后一行没有空行
        length = len(self.pure_lyric_lines)

        # 写入歌词
        for each_line_of_lyric in self.pure_lyric_lines:

            ##########可以增加嵌套（为了标准化，暂时不增加嵌套）

            order = self.pure_lyric_lines.index(each_line_of_lyric)

            if length != order:
                each_line_of_lyric += '\n'

            # 同①
            # file.write(each_line_of_lyric.encode(self.open_encoding[0]).decode(self.open_encoding[0]))

            file.write(each_line_of_lyric)

        file.close()

    def save_lrc(self) -> None:
        '''
        Save_the_lrc use attributions.
        Remember the self.pure_lyric_lines should be a primary list.
        歌词主体格式必须是按行分割的一级列表。
        '''

        information_list = ['']

        # 将信息组合成列表
        if self.artist != None:
            artist = '[ar:' + self.artist + ']'
            information_list.append(artist)

        if self.album != None:
            album = '[al:' + self.album + ']'
            information_list.append(album)

        if self.lyric_writer != None:
            lyric_writer = '[au:' + self.lyric_writer + ']'
            information_list.append(lyric_writer)

        if self.lrc_file_writer != None:
            lrc_file_writer = '[by:' + self.lrc_file_writer + ']'
            information_list.append(lrc_file_writer)

        if self.kana != None:  # 日语歌词专用，不确定具体含义
            tag_kana = '[kana:' + self.kana + ']'
            information_list.append(tag_kana)

        if self.length != None:
            length = '[length:' + self.length + ']'
            information_list.append(length)

        if self.offset != None:
            offset = '[offset:' + self.offset + ']'
            information_list.append(offset)

        if self.creating_software != None:
            creating_software = '[re:' + self.creating_software + ']'
            information_list.append(creating_software)

        if self.title != None:
            title = '[ti:' + self.title + ']'
            information_list.append(title)

        if self.version != None:
            version = '[ve:' + self.version + ']'
            information_list.append(version)

        # 有 'r+ '清空文件 清空不干净的bug
        # 清空文件
        self.file.truncate()

        # 恢复文件指针到开头，要不然会出现一堆NULL
        self.file.seek(0)

        # 写入信息
        for information in information_list:
            if information == '':
                pass
            else:
                information += '\n'

                # ①防止出现编码BUG而保留这一行作为备选项，方便应急修改。
                # information = information.encode(self.open_encoding[0]).decode(self.open_encoding[0])

                self.file.write(information)

        # 计数，最后一行没有空行
        length = len(self.pure_lyric_lines)

        # 写入歌词
        for each_line_of_lyric in self.pure_lyric_lines:

            ##########可以增加嵌套（为了标准化，暂时不增加嵌套）

            order = self.pure_lyric_lines.index(each_line_of_lyric)

            if length != order:
                each_line_of_lyric += '\n'

            # 同①
            # self.file.write(each_line_of_lyric.encode(self.open_encoding[0]).decode(self.open_encoding[0]))

            self.file.write(each_line_of_lyric)

        # 嵌套有很大的问题
        '''
        #嵌套
        def get_final_string(lyric_list) -> str:
            final_string = ''
            for each_line_of_lyric in lyric_list:
                
                order = lyric_list.index(each_line_of_lyric)
                
                if type(each_line_of_lyric) == list:
                    lyric_element = get_final_string(each_line_of_lyric)
                    
                elif type(each_line_of_lyric) == str:
                    if length != order:
                        each_line_of_lyric += '\n'
                        #不晓得二次调用的同名变量会不会互相影响
                        lyric_element = each_line_of_lyric
                    
                    final_string += lyric_element
                
            return final_string
            
        final_string = get_final_string(self.pure_lyric_lines)
        print(final_string)
        self.file.write(final_string)
        '''
        self.file.close()

# 最后修改
def load_lrc_file(LrcFile, mode='r+', buffering=-1, encoding='utf-8-sig', errors=None, newline=None, closefd=True,
                  opener=None) -> 'file':
    lrc_file = Lyric_file(LrcFile, mode, buffering, encoding, errors, newline, closefd, opener)

    # text = lrc_file.read()

    # full_lyric_list = re.split(r'\n',text)

    # return full_lyric_list
    # lrc_file.close()

    return lrc_file


if __name__ == '__main__':
    print(version())
    print(convert_to_int("[10:0.0]"))
    print(convert_to_tab(600666, True, True))
    Test_lrc = Lyric_file("test.lrc")
    print("FINISHED")
"""
Inportance:
每次新建函数记得新建列表，深拷贝，防止源文件列表被修改
#☆★同时具备深拷贝的功能，防止原始文件列表被修改

#只能进行split_time_and_lyric操作，因为split_time_and_lyric自带新建。
"""

'''
1.0.0.23

修正了文件清空不干净和毫秒数写入左边0缺失的bug

1.0.0.24

加入了获取翻译时间标签的行数位移（从第n行开始计算）
正在扩展一个新函数用于整合拥有相同时间标签的歌词
修复了最后一行空行的BUG(1.0.0.23.1)，并且删除了重编码解码的步骤
加入了若干注释

1.0.0.25
用于整合拥有相同时间标签的歌词的新函数编写完成， 核心算法添加
修复新函数整合标签时间倒序,变量出错等一系列BUG
增加split_time_and_lyric 新参数，是否保留标签括号

1.0.0.26
正在增加一个分离标签函数
注释了一下save方法

1.0.0.27
算法开始，增加时间转换，排序算法。
隐藏import 的模块

1.0.0.28(1.3.9)
complex_lrc_into_standard_form核心算法：二分法插入核心二维列表 编写完成。
完成complex_lrc_into_standard_form方法，增加一个可选左右插入的新方法。

修复若干bug
1.0.0.29(1.3.9)
complex_lrc_into_standard_form 测试完成
优化正则表达式

1.0.0.30(1.3.10)
设置二分解开歌词时为None,改字符串变量值为空值
准备添加几个新函数
完善Time_tab类
增加注释

1.0.0.31(1.4.0)
引入对时间类对扩展时间标签的支持（<>）
增加批量移动时间
增加部分日文歌词有的[kana:]标签    #日语歌词专用，不确定具体含义
加入若干文档说明
删掉遗漏的print()
让get_all_time_tab函数适应精简版歌词
增加get_all_time_tab函数时间标签分组，改一级列表为二级列表。
增加Lrc_file类识别是否拓展lrc格式
增加shift_time函数空情况的自动填充原始字符串以适应类
改变conver_to_time_stamp输入类型list为tab，符合常人使用习惯
修正shift_time的代码若干互相引用以及算术bug
改conver_to_tab为@classmethod


1.0.0.32(1.4.1)
增加to_srt函数(未测试)
增加其translate_line参数，代表翻译的行数

1.0.0.32.1(1.4.2)
增加 headline 参数 单独分离头部（整合成同一个时间标签）
1.0.0.32.2
万一没有分钟和毫秒参数，修正split_time_and_lyric

1.0.0.33(1.5.0)
增加add_translate函数（第一次以顺理成章的使用try: except: else: finally:）（未测试）$
使得Lrc_file能够以空对象的形式调用（未测试）（已测试，可用）
更改self.__clc属性名为__next_clc

1.0.0.33(1.5.1)
在保存时恢复文件指针为0，避免文件头一堆NULL的可能情况。
增加LRC保存时的列表可以嵌套（未测试）$!!!

1.0.0.33.2(1.6.0)
使Time_tab类可以适应空对象，
初始化Time_tab类时预先定义若干原来只在__pre_seperating才定义的的self.（默认为None）

1.0.0.33.3
改判断是否为拓展格式时适应只有一个尖括号的错误清况

1.0.0.33.4
增加返回值类型注释

1.0.0.33.5(1.7.0)
通过测试to_srt，修正了Time_tab类实例化之后，若干属性被覆盖的问题。
（to_srt 已测试）
改whether_blank为whether_double_blank
修复报错，列表死循环，输出不规范等问题（add_translate）（测试完成）$
修复culculate_all_translated_time_tab没有最后一项的问题
去除conver_to_tab的@classmethod（会导致self.tag无法正常调用）
修正to_srt,小时位数计算只有一位需要补位的情况
考虑到嵌套有种种问题，取消嵌套
修改注释

#修复若干bug

1.0.0.33.6(1.8.0)
增加判断是否是标准格式

1.0.0.33.7(1.9.0)
增加另存为函数

1.0.0.33.8(1.10.0)
兼容直接以字符串形式的导入

1.0.0.33.9(1.11.0)
兼容直接以列表形式导入
并粗浅判断是否符合规范

1.0.0.33.10(1.12.0.210314)
增加其他id拓展（未将其添加到字典里面）
修复simple_lrc的注释文档的bug


类的默认实例化打开方式从w+变成r+
'''

'''
strict_mode:

    # 规范里面说了，分钟位和秒钟位必须有数字
    strict:
        1. 分秒毫秒按照 00:00.00排列，秒钟不得超过60
    
    normal:
        1. 分秒毫秒按照 00:00.00排列，毫秒允许三位以上或者1位，分钟允许三位以上或者一位
        
    lose:
        1. 分秒毫秒按照 00:00:/.00排列，，毫秒允许三位以上或者1位，分钟允许三位以上或者一位，允许:/.问题

'''
