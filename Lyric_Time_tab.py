import re
from typing import Optional
from typing import Final
from typing import Match, Pattern
from typing import Self

# 时间标签转换常量
CONVERSION_TIME_60: int = 60
CONVERSION_TIME_1000: int = 1000
CONVERSION_TIME_100: int = 100


class Lyric_Time_tab:
    """
    中文注释： \n
    LRC 歌词格式的 时间标签类

    English Comments: \n
    LRC Lyrics Format Time Tab Class
    """

    # 尖括号正则表达式
    ANGLE_BRACKETS_REGREX: str = r'\<|\>'
    # 方括号正则表达式
    SQUARE_BRACKETS_REGREX: str = r'\[|\]'

    '''
    判断时间标签是否合法
    拥有严格，普通，宽松，非常宽松四种模式
    strict: 严格模式，只接受[00:00.00]、<00:00.00>格式
    normal: 普通模式，接受[00:00[:.]{2-3}]、<00:00[:.]{2-3}>格式
    loose: 宽松模式，在normal基础上 允许 分钟秒钟毫秒任意位数，至少一位，但是不允许括号缺失， 毫秒数可缺失 [ \d* : \d* [:.] \d* ]
    very_loose: 非常宽松模式，允许括号缺失 [? \d* : \d* [:.] \d* ]?
    
    # 规范里面说了，分钟位和秒钟位必须有数字
    '''
    # 每句歌词的时间标签的正则表达式 []
    # 严格模式时间标签的正则表达式
    TIME_TAB_EACH_LINE_STRICT_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)'
                                                                       r'(?P<minutes>\d{2})'
                                                                       r'(?P<minutes_seconds_seperator>:)'
                                                                       r'(?P<seconds>\d{2})'
                                                                       r'(?P<seconds_milliseconds_seperator>\.)'
                                                                       r'(?P<milliseconds>\d{2})'
                                                                       r'(?P<right_bracket>])')
    # 普通模式时间标签的正则表达式
    TIME_TAB_EACH_LINE_NORMAL_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)'
                                                                       r'(?P<minutes>\d{2})'
                                                                       r'(?P<minutes_seconds_seperator>:)'
                                                                       r'(?P<seconds>\d{2})'
                                                                       r'(?P<seconds_milliseconds_seperator>[:.])'
                                                                       r'(?P<milliseconds>\d{2,3})'
                                                                       r'(?P<right_bracket>])')

    # 宽松模式时间标签的正则表达式
    TIME_TAB_EACH_LINE_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)'
                                                                      r'(?P<minutes>\d*)'
                                                                      r'(?P<minutes_seconds_seperator>:)'
                                                                      r'(?P<seconds>\d*)'
                                                                      r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                      r'(?P<milliseconds>\d*)?'
                                                                      r'(?P<right_bracket>])')
    # 非常宽松模式时间标签的正则表达式
    TIME_TAB_EACH_LINE_VERY_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)?'
                                                                           r'(?P<minutes>\d*)'
                                                                           r'(?P<minutes_seconds_seperator>:)'
                                                                           r'(?P<seconds>\d*)'
                                                                           r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                           r'(?P<milliseconds>\d*)?'
                                                                           r'(?P<right_bracket>])?')

    # 正则表达式列表
    TIME_TAB_EACH_LINE_REGREX_LIST: list = [TIME_TAB_EACH_LINE_STRICT_REGREX,
                                            TIME_TAB_EACH_LINE_NORMAL_REGREX,
                                            TIME_TAB_EACH_LINE_LOOSE_REGREX,
                                            TIME_TAB_EACH_LINE_VERY_LOOSE_REGREX]

    # 歌词每个字的时间标签的正则表达式 <>
    # 严格模式时间标签的正则表达式
    TIME_TAB_EACH_WORD_STRICT_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                       r'(?P<minutes>\d{2})'
                                                                       r'(?P<minutes_seconds_seperator>:)'
                                                                       r'(?P<seconds>\d{2})'
                                                                       r'(?P<seconds_milliseconds_seperator>\.)'
                                                                       r'(?P<milliseconds>\d{2})'
                                                                       r'(?P<right_bracket>>)')
    # 普通模式时间标签的正则表达式
    TIME_TAB_EACH_WORD_NORMAL_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                       r'(?P<minutes>\d{2})'
                                                                       r'(?P<minutes_seconds_seperator>:)'
                                                                       r'(?P<seconds>\d{2})'
                                                                       r'(?P<seconds_milliseconds_seperator>[:.])'
                                                                       r'(?P<milliseconds>\d{2,3})'
                                                                       r'(?P<right_bracket>>)')
    # 宽松模式时间标签的正则表达式
    TIME_TAB_EACH_WORD_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                      r'(?P<minutes>\d*)'
                                                                      r'(?P<minutes_seconds_seperator>:)'
                                                                      r'(?P<seconds>\d*)'
                                                                      r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                      r'(?P<milliseconds>\d*)?'
                                                                      r'(?P<right_bracket>>)')
    # 非常宽松模式时间标签的正则表达式
    TIME_TAB_EACH_WORD_VERY_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)?'
                                                                           r'(?P<minutes>\d*)'
                                                                           r'(?P<minutes_seconds_seperator>:)'
                                                                           r'(?P<seconds>\d*)'
                                                                           r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                           r'(?P<milliseconds>\d*)?'
                                                                           r'(?P<right_bracket>>)?')

    # 正则表达式列表
    TIME_TAB_EACH_WORD_REGREX_LIST: list = [TIME_TAB_EACH_WORD_STRICT_REGREX,
                                            TIME_TAB_EACH_WORD_NORMAL_REGREX,
                                            TIME_TAB_EACH_WORD_LOOSE_REGREX,
                                            TIME_TAB_EACH_WORD_VERY_LOOSE_REGREX]

    """
    接受一个时间标签字符串，分离出时间标签的各个部分
    """

    def __init__(self, tab: Optional[str], mode: str = 'normal'):
        # 时间标签原始字符串
        self.original_time_tab: str = tab
        # 修改或者规范后的时间标签字符串
        self.time_tab: Optional[str] = None

        # 时间标签类型 [] or <>
        self.brackets: Optional[list[str, str]] = None
        # 时间戳
        self.time_stamp: Optional[float] = None

        # 原始匹配结果
        self.match_result: Optional[Match[str]] = None
        # 时间标签列表
        self.time_list: Optional[list] = None

        # 时间标签分钟
        self.minutes_str: Optional[str] = None
        # 时间标签秒
        self.seconds_str: Optional[str] = None
        # 时间标签毫秒（不足三位补零）（默认按照三位储存，输出则是默认两位）
        self.milliseconds_str: Optional[str] = None

        # 分钟秒钟分割符
        self.minutes_seconds_seperator: Optional[str] = None
        # 秒钟毫秒分割符
        self.seconds_milliseconds_seperator: Optional[str] = None

        # 时间标签毫秒位数
        self.len_of_millisecond = None

        # 预分离时间标签
        if tab is not None:
            self.__pre_separating(tab, mode)
        else:
            # print("Time tab None input, notice!")
            pass

        # 最后初始化 self.time_tab， 为 self.original_time_tab
        self.time_tab = self.original_time_tab

    # 返回时间标签时间戳
    def __int__(self):
        return self.time_stamp

    # 返回时间标签字符串
    def __str__(self):
        return self.time_tab

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

    # 加减乘除运算，返回时间标签时间戳
    def __add__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp += other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp += other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for +: \'TimeTab\' and \'{}\''.format(type(other)))

    def __sub__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp -= other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp -= other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for -: \'TimeTab\' and \'{}\''.format(type(other)))

    def __mul__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp *= other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp *= other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for *: \'TimeTab\' and \'{}\''.format(type(other)))

    def __truediv__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp /= other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp /= other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for /: \'TimeTab\' and \'{}\''.format(type(other)))

    def __floordiv__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp //= other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp //= other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for //: \'TimeTab\' and \'{}\''.format(type(other)))

    def __mod__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp %= other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp %= other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for %: \'TimeTab\' and \'{}\''.format(type(other)))

    def __pow__(self, other):
        # 判断类型是否为 时间标签
        if isinstance(other, self.__class__):
            self.time_stamp **= other.time_stamp
            return self
        # 判断类型是否为 int 或者 float
        elif isinstance(other, int) or isinstance(other, float):
            self.time_stamp **= other * CONVERSION_TIME_1000
            return self
        else:
            raise TypeError('unsupported operand type(s) for **: \'TimeTab\' and \'{}\''.format(type(other)))

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __rmod__(self, other):
        return self.__mod__(other)

    def __rpow__(self, other):
        return self.__pow__(other)

    """
    预分离标签，判断是否合法，分离出时间标签的各个部分，储存到类的属性中，供其他方法调用
    私有方法
    """

    def __pre_separating(self, tab: str, mode: str = 'normal') -> None:
        """
        中文注释：
        预分离标签，判断是否合法，分离出时间标签的各个部分，储存到类的属性中，供其他方法调用
        私有方法

        English comment:
        Pre-separate the label, judge whether it is legal, separate the various parts of the time label,
        and store them in the properties of the class for other methods to call
        Private method

        :param tab: 时间标签字符串
        :param mode: 模式
        :return: None
        """

        # 匹配时间标签
        # 判断是否合法，并且判断类型
        valid_with_type: list[bool, Optional[Pattern[str]]] = Lyric_Time_tab.is_valid_with_type(tab, mode)

        # 如果合法
        if valid_with_type[0]:
            # 利用返回的 判断出的 正则表达式 分离时间标签
            self.match_result = valid_with_type[1].match(tab)
            self.time_list = self.match_result.groups()

            # 添加到类的属性中
            self.brackets = self.match_result.group("left_bracket") + self.match_result.group("right_bracket")
            self.minutes_str = self.match_result.group("minutes")
            # 如果有分钟位，分钟位不足两位，左边补零
            self.minutes_str = self.minutes_str.rjust(2, '0')
            self.minutes_seconds_seperator = self.match_result.group("minutes_seconds_seperator")

            self.seconds_str = self.match_result.group("seconds")
            # 如果有秒位，秒位不足两位，左边补零
            self.seconds_str = self.seconds_str.rjust(2, '0')

            self.seconds_milliseconds_seperator = self.match_result.group("seconds_milliseconds_seperator")
            # 如果有毫秒位，毫秒位不足三位，右边补零
            self.milliseconds_str = self.match_result.group("milliseconds")

            # 如果有毫秒位，毫秒位不足三位，右边补零
            if self.milliseconds_str is not None:
                self.len_of_millisecond = len(self.milliseconds_str)
                self.milliseconds_str = self.milliseconds_str.ljust(3, '0')
            else:
                # 原先就是None，不用管
                pass

            # 自动计算时间戳
            # 要考虑没有(None)的情况
            # None 会被转换成 0
            minutes_int: int
            seconds_int: int
            milliseconds_int: int

            if self.minutes_str is not None:
                minutes_int = int(self.minutes_str)
            else:
                minutes_int = 0

            if self.seconds_str is not None:
                seconds_int = int(self.seconds_str)
            else:
                seconds_int = 0

            if self.milliseconds_str is not None:
                milliseconds_int = int(self.milliseconds_str)
            else:
                milliseconds_int = 0

            # 调用函数，计算时间戳
            self.time_stamp = Lyric_Time_tab.calculate_time_stamp(minutes_int, seconds_int, milliseconds_int)

            # print(self.time_stamp)

        # 如果不合法
        else:
            # 报错
            raise ValueError(f"The time original_tab {tab} is not valid under {mode} mode")

    """
    判断时间标签是否合法，并且判断类型
    """

    @classmethod
    def is_valid_with_type(cls, tab: str, mode: str = 'normal') -> list[bool, Optional[Pattern[str]]]:
        """
        中文： \n
        判断时间标签是否合法，并且判断类型 \n
        拥有严格，普通，宽松，非常宽松四种模式 \n
            strict: 严格模式，只接受[00:00.00]、<00:00.00>格式 \n
            normal: 普通模式，接受[00:00[:.]{2-3}]、<00:00[:.]{2-3}>格式 \n
            loose: 宽松模式，在normal基础上 允许 分钟秒钟毫秒任意位数，但是不允许括号缺失， 毫秒数可缺失 \n
            very_loose: 非常宽松模式，允许括号缺失 \n

        可以是 每行的也可以是每个字的 [] <> \n
            如果是每行的，返回[True, 对应的模式下的 方括号正则表达式常量] \n
            如果是每个字的，返回[True, 对应的模式下的 尖括号正则表达式常量] \n
            如果不是任何一种，返回[False, None]
        \n\n

        English: \n
        Determine whether the time label is legal and determine the type \n
        Has strict, normal, loose, very loose four modes \n
            strict: strict mode, only accept [00:00.00], <00:00.00> format \n
            normal: normal mode, accept [00:00[:.]{2-3}], <00:00[:.]{2-3}> format \n
            loose: loose mode, on the basis of normal,
                allow minutes_str, seconds_str, milliseconds_str any number of digits,
            but do not allow brackets missing, milliseconds_str can be missing \n
            very_loose: very loose mode, allow brackets missing \n

        Can be every line or every word [] <> \n
            If it is every line, return [True, square brackets regular expression constant] \n
            If it is every word, return [True, angle brackets regular expression constant] \n
            If it is not any one, return [False, None] \n

        :param tab: 时间标签 Time Tab
        :param mode: 模式 Mode
        :return: [是否合法 Whether valid,
                  括号正则表达式常量 Bracket Regular Expression Constant]
        """

        # 严格模式
        if mode == 'strict':
            # 每行的
            if re.match(cls.TIME_TAB_EACH_LINE_STRICT_REGREX, tab):
                return [True, Lyric_Time_tab.TIME_TAB_EACH_LINE_STRICT_REGREX]
            # 每个字的
            elif re.match(cls.TIME_TAB_EACH_WORD_STRICT_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_WORD_STRICT_REGREX]
            else:
                return [False, None]

        # 普通模式
        elif mode == 'normal':
            # 每行的
            if re.match(cls.TIME_TAB_EACH_LINE_NORMAL_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_LINE_NORMAL_REGREX]
            # 每个字的
            elif re.match(cls.TIME_TAB_EACH_WORD_NORMAL_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_WORD_NORMAL_REGREX]
            else:
                return [False, None]

        # 宽松模式
        elif mode == 'loose':
            # 每行的
            if re.match(cls.TIME_TAB_EACH_LINE_LOOSE_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_LINE_LOOSE_REGREX]
            # 每个字的
            elif re.match(cls.TIME_TAB_EACH_WORD_LOOSE_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_WORD_LOOSE_REGREX]
            else:
                return [False, None]

        # 非常宽松模式
        elif mode == 'very_loose':
            # 每行的
            if re.match(cls.TIME_TAB_EACH_LINE_VERY_LOOSE_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_LINE_VERY_LOOSE_REGREX]
            # 每个字的
            elif re.match(cls.TIME_TAB_EACH_WORD_VERY_LOOSE_REGREX, tab):
                return [True, cls.TIME_TAB_EACH_WORD_VERY_LOOSE_REGREX]
            else:
                return [False, None]

        # 模式错误
        else:
            # 引发异常, 模式错误
            # input is "mode变量的值", must be strict, normal, loose or very_loose
            raise ValueError(f'input is "{mode}", must be strict, normal, loose or very_loose')

    """
    计算时间戳，分、秒、毫秒，小时（可选）
    返回毫秒位单位的时间戳(3位)
    """

    @staticmethod
    def calculate_time_stamp(minute: int, second: int, millisecond: float, hour: int = 0) -> float:
        """
        中文：\n
        计算时间戳，分、秒、毫秒，小时（可选）\n
        返回毫秒位单位的时间戳(3位)

        English: \n
        Calculate the time stamp, minute, second, millisecond, hour (optional) \n
        Return the time stamp in milliseconds_str (3 digits)

        :param minute: 分 Minute
        :param second: 秒 Second
        :param millisecond: 毫秒 Millisecond
        :param hour: 小时 Hour
        :return: 毫秒位单位的时间戳(3位) The time stamp in milliseconds_str (3 digits)
        """

        # 括号不影响，不会转为元组
        return (hour * CONVERSION_TIME_60 * CONVERSION_TIME_60 * CONVERSION_TIME_1000 +
                minute * CONVERSION_TIME_60 * CONVERSION_TIME_1000 +
                second * CONVERSION_TIME_1000 +
                millisecond)

    """
    规范时间戳，按需求转为len_of_millisecond位的时间戳
    """

    @staticmethod
    def format_time_stamp_static(time_stamp: int, len_of_millisecond: int = 2, keep_decimal: bool = False) -> int:
        """
        中文：\n
        默认是三位， \n
        转为len_of_millisecond位的时间戳 \n
        比如，2位的时间戳，就是除以10

        English: \n
        Default is three digits, \n
        Convert to a time stamp of len_of_millisecond digits \n
        For example, a 2-digit time stamp is divided by 10

        :param time_stamp: 时间戳 The time stamp
        :param len_of_millisecond: 毫秒位的位数 The number of milliseconds_str
        :param keep_decimal: 是否保留小数位 Whether to keep decimal places
        """

        time_stamp: int | float

        # 计算时间戳
        if len_of_millisecond == 3:
            time_stamp = time_stamp
        else:
            time_stamp = time_stamp / (10 ** (3 - len_of_millisecond))

        # 是否保留小数位
        if keep_decimal:
            return time_stamp
        else:
            return int(time_stamp)

    """
    规范时间戳，按需求转为len_of_millisecond位的时间戳
    """

    def format_time_stamp(self, len_of_millisecond: int = 2, keep_decimal: bool = False) -> int:
        """
        中文：\n
        用静态方法 规范类为时间戳

        English: \n
        Use static method to standardize class as time stamp

        :param len_of_millisecond: 毫秒位的位数 The number of milliseconds_str
        :param keep_decimal: 是否保留小数位 Whether to keep decimal places
        """
        return Lyric_Time_tab.format_time_stamp_static(self.time_stamp, len_of_millisecond, keep_decimal)

    """
    将时间戳转为时间标签
    """

    @staticmethod
    def convert_time_stamp_to_time_tab_static(time_stamp: int | float,
                                              len_of_millisecond_inputted: int = 3,
                                              len_of_millisecond_output: int = 2,
                                              brackets: tuple[str, str] = ("[", "]"),
                                              seperator: tuple[str, str] = (":", ".")) -> str:
        """
        中文：\n
        将时间戳转为时间标签

        English: \n
        It is a staticmethod. It converts the time stamp of time tag in to a tag.

        :param time_stamp: 时间戳 The time stamp
        :param len_of_millisecond_inputted: 输入的时间戳的毫秒位的位数 The number of milliseconds_str of the input time stamp
        :param len_of_millisecond_output: 输出的时间戳的毫秒位的位数 The number of milliseconds_str of the output time stamp
        :param brackets: 括号 The brackets
        :param seperator: 分隔符 The seperator
        :return: 时间标签 The time tag
        """
        minutes_int: int
        seconds_int: int
        millisecond_int: int | float

        minutes_str: str
        seconds_str: str
        millisecond_str: str

        time_tab_output: str

        # 计算分秒毫秒，输入的时间戳是len_of_millisecond位相关的
        minutes_int = time_stamp // (10 ** len_of_millisecond_inputted) // 60
        seconds_int = time_stamp // (10 ** len_of_millisecond_inputted) % 60
        millisecond_int = time_stamp * (10 ** (3 - len_of_millisecond_inputted)) % 1000

        # 转为字符串
        # 分
        minutes_str = str(minutes_int)
        # 补位
        # 不足则左边补0
        minutes_str = minutes_str.rjust(2, "0")

        # 秒
        seconds_str = str(seconds_int)
        # 补位
        # 不足则左边补0
        seconds_str = seconds_str.rjust(2, "0")

        # 毫秒
        # 如果有小数位，抹去小数位
        millisecond_int = int(millisecond_int)
        # 转为字符串
        millisecond_str = str(millisecond_int)
        # 输出的毫秒位长度
        # 不足则右边补0
        millisecond_str = millisecond_str.ljust(len_of_millisecond_output, "0")
        # 截取
        millisecond_str = millisecond_str[:len_of_millisecond_output]

        # 加上 左右括号 和 分隔符
        # 格式化字符串
        time_tab_output = f"{brackets[0]}" \
                          f"{minutes_str}" \
                          f"{seperator[0]}" \
                          f"{seconds_str}" \
                          f"{seperator[1]}" \
                          f"{millisecond_str}" \
                          f"{brackets[1]}"

        # 返回最终结果
        return time_tab_output

    def convert_to_time_tab(self,
                            len_of_millisecond_inputted: int = 3,
                            len_of_millisecond_output: int = 2,
                            brackets: tuple[str, str] = ("[", "]"),
                            seperator: tuple[str, str] = (":", ".")) -> str:
        """
        中文：\n
        将时间戳转为时间标签，对实例本身进行操作

        English: \n
        It converts the time stamp of time tag in to a tag. It operates on the instance itself.

        :param len_of_millisecond_inputted: 输入的时间戳的毫秒位的位数 The number of milliseconds_str of the input time stamp
            默认在实例化类的时候已经转换成了3位毫秒位的时间戳 Default is 3 digits in property time_stamp of class Lyric_Time_tab
        :param len_of_millisecond_output: 输出的时间戳的毫秒位的位数 The number of milliseconds_str of the output time stamp
        :param brackets: 括号 The brackets
        :param seperator: 分隔符 The seperator
        :return: 时间标签 The time tag
        """
        # 如果time stamp是None，返回空字符串，表明没有时间标签
        if self.time_stamp is None:
            return ""
        else:
            return Lyric_Time_tab.convert_time_stamp_to_time_tab_static(self.time_stamp,
                                                                        len_of_millisecond_inputted,
                                                                        len_of_millisecond_output,
                                                                        brackets,
                                                                        seperator)

    # 返回自身
    def shift_time(self,
                   minutes: int,
                   seconds: int,
                   milliseconds: int,
                   len_of_millisecond: int = 3
                   ) -> Self:
        """
        中文：\n
        将时间标签向前或向后移动

        English: \n
        Move the time tag forward or backward

        :param minutes: 分钟数 The number of minutes_str
        :param seconds: 秒数 The number of seconds_str
        :param milliseconds: 毫秒数 The number of milliseconds_str
        :param len_of_millisecond: 毫秒位的位数 The number of milliseconds_str
        """

        # 转毫秒位为3位（规范化）
        milliseconds = int(milliseconds * (10 ** (3 - len_of_millisecond)))

        # 修改属性
        self.minutes_str += minutes
        self.seconds_str += seconds
        self.milliseconds_str += milliseconds

        # 修改时间列表
        self.time_list[1] += minutes
        self.time_list[3] += seconds
        self.time_list[5] += milliseconds

        # 计算时间戳
        time_stamp_shift: float = Lyric_Time_tab.calculate_time_stamp(minutes, seconds, milliseconds)

        # 移动时间戳
        self.time_stamp += time_stamp_shift

        # 修改时间标签
        self.time_tab = self.convert_to_time_tab()

        return self

    # 返回自身
    def format_time_tab_self(self,
                             brackets: Optional[tuple[str, str]],
                             seperator: Optional[tuple[str, str]]
                             ) -> Self:
        """
        中文：\n
        格式化时间标签对象本身 \n
        把秒 限制在0-59之间 \n
        把毫秒 限制在0-999之间 \n
        并且补全括号，分隔符 \n
        如果brackets和seperator为None，则不补全括号，分隔符
        返回规范化后的自身

        English: \n
        Format the time tag object itself\n
        Limit the seconds_str between 0 and 59 \n
        Limit the milliseconds_str between 0 and 999 \n
        And complete the brackets and seperator \n
        If brackets and seperator are None, do not complete the brackets and seperator
        Return the normalized self


        :return: self
        """

        # ==================== 时分秒毫秒单位溢出处理 ==================== #

        # 预处理 类型转换
        # 转为float
        minutes: int = int(self.minutes_str)
        seconds: int = int(self.seconds_str)
        milliseconds: float = float(self.milliseconds_str)

        # 毫秒
        # 如果大于等于1000
        if milliseconds >= 1000:
            # 计算多余的秒数
            seconds_extra: int = int(milliseconds // 1000)
            # 计算剩余的毫秒数
            milliseconds = milliseconds % 1000
            # 秒数加上多余的秒数
            seconds += seconds_extra

        # 如果小于0
        elif milliseconds < 0:
            # 注意这里 用的是负数相加，milliseconds是负数，所以退位减一是负一
            # 计算多余的秒数
            seconds_extra: int = -1 + int(milliseconds // 1000)
            # 计算剩余的毫秒数
            milliseconds = 1000 + milliseconds % 1000
            # 秒数加上多余的秒数
            seconds += seconds_extra

        # 秒
        # 如果大于等于60
        if seconds >= 60:
            # 计算多余的分钟数
            minutes_extra: int = int(seconds // 60)
            # 计算剩余的秒数
            seconds = seconds % 60
            # 分钟数加上多余的分钟数
            minutes += minutes_extra

        # 如果小于0
        elif seconds < 0:
            # 注意这里 用的是负数相加，seconds是负数，所以退位减一是负一
            # 计算多余的分钟数
            minutes_extra: int = -1 + int(seconds // 60)
            # 计算剩余的秒数
            seconds = 60 + seconds % 60
            # 分钟数加上多余的分钟数
            minutes += minutes_extra

        # 赋值回去
        self.minutes_str = str(minutes)
        self.seconds_str = str(seconds)
        self.milliseconds_str = str(milliseconds)

        # ==================== 括号分隔符补全 ==================== #

        # 如果brackets和seperator为None，则不补全括号，分隔符
        if brackets is not None:
            self.brackets = brackets

            # 也赋值到时间列表内
            self.time_list[0] = self.brackets[0]
            self.time_list[6] = self.brackets[1]

        if seperator is not None:
            self.minutes_seconds_seperator = seperator[0]
            self.seconds_milliseconds_seperator = seperator[1]

            # 也赋值到时间列表内
            self.time_list[2] = self.minutes_seconds_seperator
            self.time_list[4] = self.seconds_milliseconds_seperator

        # ==================== 修改时间列表内的分秒毫秒 ==================== #
        self.time_list[1] = minutes
        self.time_list[3] = seconds
        self.time_list[5] = milliseconds

        return self

    def isspace(self) -> bool:
        return self.original_time_tab.isspace()


"""
中文：\n
测试内容

English: \n
Test content
"""
if __name__ == '__main__':
    # 打印正则表达式列表
    for i in Lyric_Time_tab.TIME_TAB_EACH_LINE_REGREX_LIST:
        print(i)

    print(Lyric_Time_tab.TIME_TAB_EACH_LINE_NORMAL_REGREX.pattern)

    print(Lyric_Time_tab.calculate_time_stamp(10, 1, 100))

    # 测试时间标签 += 运算符
    time_tab = Lyric_Time_tab("[00:00.00]")
    time_tab += 1
    print(time_tab.convert_to_time_tab())
