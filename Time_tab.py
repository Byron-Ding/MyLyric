import re
from typing import Optional


# 时间标签转换常量
CONVERSION_TIME_60: int = 60
CONVERSION_TIME_1000: int = 1000
CONVERSION_TIME_100: int = 100


class Time_tab:
    """
    LRC时间标签类
    """

    # 尖括号正则表达式
    ANGLE_BRACKETS_REGREX: str = r'\<|\>'
    # 方括号正则表达式
    SQUARE_BRACKETS_REGREX: str = r'\[|\]'

    # 每句歌词的时间标签的正则表达式
    TIME_TAB_EACH_LINE_REGREX: str = r'(\[|\])?' \
                                     r'(\d{2})' \
                                     r'(:)' \
                                     r'(\d{2})' \
                                     r'(\.)' \
                                     r'(\d{2,3})' \
                                     r'(\[|\])?'
    # 每个字符的时间标签的正则表达式
    TIME_TAB_CHAR_REGREX: str = r'(\[|\])?' \
                                r'(\d{2})' \
                                r'(:)' \
                                r'(\d{2})' \
                                r'(\.)' \
                                r'(\d{2,3})' \
                                r'(\[|\])?'

    """
    接受一个时间标签字符串，分离出时间标签的各个部分
    """
    def __init__(self, tab: str):
        # 时间标签原始字符串
        self.tab: str = tab
        # 时间标签类型
        self.bracket: Optional[str] = None
        # 时间戳
        self.time_stamp: Optional[int] = None

        # 时间标签列表
        self.time_list: Optional[list] = None
        # 时间标签分钟
        self.minutes: Optional[str] = None
        # 时间标签秒
        self.seconds: Optional[str] = None
        # 时间标签毫秒（不足三位补零）（默认按照三位储存，输出则是默认两位）
        self.milliseconds: Optional[str] = None

        # 分钟秒钟分割符
        self.minutes_seconds_seperator: Optional[str] = None
        # 秒钟毫秒分割符
        self.seconds_milliseconds_seperator: Optional[str] = None

        # 时间标签毫秒位数
        self.len_of_millisecond = None

        # 预分离时间标签
        if tab is not None:
            self.__pre_separating(tab)

        pass

    # 返回时间标签时间戳
    def __int__(self):
        return self.time_stamp

    # 返回时间标签字符串
    def __str__(self):
        return self.tab

    # 返回时间标签列表
    def __repr__(self):
        return self.time_list

    # 返回时间标签是否 == 另一个时间标签
    def __eq__(self, other):
        return self.time_stamp == other.time_stamp

    # 返回时间标签是否 < 于另一个时间标签
    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    # 返回时间标签是否 <= 另一个时间标签
    def __le__(self, other):
        return self.time_stamp <= other.time_stamp

    # 返回时间标签是否 != 另一个时间标签
    def __ne__(self, other):
        return self.time_stamp != other.time_stamp

    # 返回时间标签是否 > 另一个时间标签
    def __gt__(self, other):
        return self.time_stamp > other.time_stamp

    # 返回时间标签是否 >= 另一个时间标签
    def __ge__(self, other):
        return self.time_stamp >= other.time_stamp

    # 加减乘除运算



    """
    预分离判断标签类型
    """

    def __pre_separating(self, tab: str):
        # 新建列表，浅拷贝
        if '<' in tab or '>' in tab:

            tag = r'\<|>'
            self.tag = '<>'

        else:

            tag = r'\[|]'
            self.tag = '[]'

        time_str = [i for i in re.split(tag, tab) if i][0]

        self.time_list = re.split(r':|\.', time_str)

        self.minutes = self.time_list[0]
        self.seconds = self.time_list[1]
        self.milliseconds = self.time_list[2]
        self.len_of_millisecond = len(self.milliseconds)

        self.time_stamp = self.minutes * CONVERSION_TIME_60 * CONVERSION_TIME_1000 \
                          + self.seconds * CONVERSION_TIME_1000 \
                          + self.milliseconds
        # self.bracket =

    """
    判断时间标签是否合法
    """
    @staticmethod
    def is_valid(tab: str) -> bool:
        # 判断时间标签是否合法
        if re.match(Time_tab.SQUARE_BRACKETS, tab) or re.match(Time_tab.ANGLE_BRACKETS, tab):
            return True
        else:
            return False



    def convert_to_time_stamp(self, time_tab_input=None, len_of_millisecond=2) -> int:
        if time_tab_input is None:
            # 列表切片，浅拷贝
            time_list = self.time_list[:]
        else:
            time_list = self.__pre_separating(time_tab_input)

        if len_of_millisecond == None:
            len_of_milliseconds = self.len_of_millisecond

        # 不使用属性是因为考虑到外部调用
        time_stamp = int(time_list[0]) * (10 ** len_of_millisecond) * 60 + \
                     int(time_list[1]) * (10 ** len_of_millisecond) + \
                     int(time_list[2])

        return time_stamp

    def convert_to_tab(self, time_stamp: int, len_of_millisecond: int = 2, with_bracket: bool = True) -> str:
        '''
        It is a classmethod. It converts the time stamp of time tag in to a tag.
        '''
        minutes: str
        seconds: str
        millisecond: str
        time: str

        if len_of_millisecond == None:
            len_of_millisecond = self.len_of_millisecond

        minutes = str(int(time_stamp // \
                          (10 ** len_of_millisecond) // \
                          60))

        seconds = str(int(time_stamp // \
                          (10 ** len_of_millisecond) % \
                          60))

        millisecond = str(int(time_stamp % \
                              (10 ** len_of_millisecond)))

        # 补位至两位
        if len(minutes) < 2:
            minutes = minutes.zfill(2)

            # print(minutes,seconds,millisecond)
        if len(seconds) == 1:
            seconds = '0' + seconds

            # print(minutes,seconds,millisecond)
        if len(millisecond) < len_of_millisecond:
            millisecond = millisecond.zfill(len_of_millisecond)

            # print(minutes,seconds,millisecond)

        # print(minutes,seconds,millisecond)

        time = minutes + ':' + seconds + '.' + millisecond

        if with_bracket:

            if self.tag == '[]':
                time = '[' + time + ']'

            elif self.tag == '<>':
                time = '<' + time + '>'

            elif self.tag == None:
                pass

        return time

    def shift_time(self,
                   minutes: int,
                   seconds: int,
                   milliseconds: int,
                   origin_time_tab=None,
                   len_of_millisecond: int = 2,
                   with_bracket=True) -> str:

        '''
        注释文档
        '''

        if origin_time_tab == None:
            time_stamp = self.convert_to_time_stamp()

        time_stamp = self.convert_to_time_stamp(time_tab_input=origin_time_tab)

        if len_of_millisecond == None:
            len_of_millisecond = self.len_of_millisecond

        added_time = minutes * 60 * (10 ** len_of_millisecond) + \
                     seconds * (10 ** len_of_millisecond) + \
                     milliseconds

        time_after_adding = time_stamp + added_time

        returned_tab = self.convert_to_tab(time_after_adding, len_of_millisecond, with_bracket)
        return returned_tab
