import copy
import datetime
import math
import re
import warnings
from typing import Callable, Union, Any, Optional, List, Tuple
from typing import Final
from typing import Match, Pattern
from typing import Self

from bidict import bidict

from collections import UserString, UserList

from functools import wraps

from DataTypeInterface import Comparable, Calculable, C, BinaryCalculable
from DataTypeInterface import var_type_guard, int_leq_0_guard


class LyricTimeTab(UserString, Comparable, Calculable, BinaryCalculable, ):
    """
    中文注释： 
    LRC 歌词格式的 时间标签类

    拥有严格，普通，宽松，非常宽松四种模式
    strict: 严格模式，只接受[00:00.00]、<00:00.00>格式
    normal: 普通模式，接受[00:00[:.]{2-3}]、<00:00[:.]{2-3}>格式
    loose: 宽松模式，在normal基础上 允许 分钟秒钟毫秒任意位数，但是不允许括号缺失， 毫秒数可缺失 [ \\d* : \\d* [:.] \\d* ]
    very_loose: 非常宽松模式，允许括号缺失 [? \\d* : \\d* [:.] \\d* ]?

    self_defined: 自定义模式，自定义正则表达式
    但是必须包含
    <left_bracket>
    <minutes> <minutes_seconds_seperator>
    <seconds> <seconds_milliseconds_seperator>
    <milliseconds>
    <right_bracket>

    注意，只有在current_time_tab更新的时候才会重新初始化，其他属性不会更新

    English Comments: 
    LRC lyric format time label class

    There are four modes: strict, normal, loose, and very loose
    strict: strict mode, only accept [00:00.00], <00:00.00> format
    normal: normal mode, accept [00:00[:.]{2-3}], <00:00[:.]{2-3}> format
    loose: loose mode, on the basis of normal, allow minutes, seconds, milliseconds any number of digits,
    but brackets are not allowed to be missing, milliseconds can be missing [ \\d* : \\d* [:.] \\d* ]
    very_loose: very loose mode, allow brackets to be missing [? \\d* : \\d* [:.] \\d* ]?

    self_defined: self-defined mode, custom regular expression
    But must contain
    <left_bracket>
    <minutes> <minutes_seconds_seperator>
    <seconds> <seconds_milliseconds_seperator>
    <milliseconds>
    <right_bracket>

    Note that only when current_time_tab is updated will it be reinitialized, other attributes will not be updated
    """
    # 时间标签转换常量
    CONVERSION_TIME_60: int = 60
    CONVERSION_TIME_1000: int = 1000
    CONVERSION_TIME_100: int = 100

    # 尖括号正则表达式
    ANGLE_BRACKETS_REGREX: str = r'\<|\>'
    # 方括号正则表达式
    SQUARE_BRACKETS_REGREX: str = r'\[|\]'

    '''
    判断时间标签是否合法
    拥有严格，普通，宽松，非常宽松四种模式
    strict: 严格模式，只接受[00:00.00]、<00:00.00>格式
    normal: 普通模式，接受[00:00[:.]{2-3}]、<00:00[:.]{2-3}>格式
    loose: 宽松模式，在normal基础上 允许 分钟秒钟毫秒任意位数，但是不允许括号缺失， 毫秒数可缺失 [ \\d* : \\d* [:.] \\d* ]
    very_loose: 非常宽松模式，允许括号缺失 [? \\d* : \\d* [:.] \\d* ]?
    
    self_defined: 自定义模式，自定义正则表达式
    但是必须包含
    <left_bracket>
    <minutes> <minutes_seconds_seperator>
    <seconds> <seconds_milliseconds_seperator>
    <milliseconds>
    <right_bracket>
    
    # 规范里面说了，分钟位和秒钟位必须有数字
    '''
    MODE_TYPE: Final[tuple[str, ...]] = ('strict', 'normal', 'loose', 'very_loose', 'self_defined')

    # REGREX group name
    # 自定义必须包含的组名
    SELF_DEFINED_GROUP_NAME: Final[set[str]] = {'left_bracket', 'minutes', 'minutes_seconds_seperator',
                                                'seconds', 'seconds_milliseconds_seperator', 'milliseconds',
                                                'right_bracket'}

    # 歌词每个字的时间标签的正则表达式 <> []
    # 严格模式时间标签的正则表达式
    TIME_TAB_STRICT_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                             r'(?P<minutes>\d{2})'
                                                             r'(?P<minutes_seconds_seperator>:)'
                                                             r'(?P<seconds>\d{2})'
                                                             r'(?P<seconds_milliseconds_seperator>\.)'
                                                             r'(?P<milliseconds>\d{2})'
                                                             r'(?P<right_bracket>[]>])')
    # 普通模式时间标签的正则表达式
    TIME_TAB_NORMAL_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                             r'(?P<minutes>\d{2})'
                                                             r'(?P<minutes_seconds_seperator>:)'
                                                             r'(?P<seconds>\d{2})'
                                                             r'(?P<seconds_milliseconds_seperator>[:.])'
                                                             r'(?P<milliseconds>\d{2,3})'
                                                             r'(?P<right_bracket>[]>])')
    # 宽松模式时间标签的正则表达式
    TIME_TAB_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                            r'(?P<minutes>\d+)'
                                                            r'(?P<minutes_seconds_seperator>:)'
                                                            r'(?P<seconds>\d+)'
                                                            r'(?P<seconds_milliseconds_seperator>[:.]?)'
                                                            r'(?P<milliseconds>\d*)'
                                                            r'(?P<right_bracket>[]>])')
    # 非常宽松模式时间标签的正则表达式
    TIME_TAB_VERY_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<]?)'
                                                                 r'(?P<minutes>\d*?)'
                                                                 r'(?P<minutes_seconds_seperator>:?)'
                                                                 r'(?P<seconds>\d*?)'
                                                                 r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                 r'(?P<milliseconds>\d+)'
                                                                 r'(?P<right_bracket>[]>]?)')

    # 正则表达式列表
    TIME_TAB_MODE_REGREX_PAIR: bidict[str, Pattern[str]] = bidict({
        MODE_TYPE[0]: TIME_TAB_STRICT_REGREX,
        MODE_TYPE[1]: TIME_TAB_NORMAL_REGREX,
        MODE_TYPE[2]: TIME_TAB_LOOSE_REGREX,
        MODE_TYPE[3]: TIME_TAB_VERY_LOOSE_REGREX
    })

    # 歌词每个字的时间标签的正则表达式 []
    # 严格模式时间标签的正则表达式
    TIME_TAB_STRICT_REGREX_SQUARE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)'
                                                                             r'(?P<minutes>\d{2})'
                                                                             r'(?P<minutes_seconds_seperator>:)'
                                                                             r'(?P<seconds>\d{2})'
                                                                             r'(?P<seconds_milliseconds_seperator>\.)'
                                                                             r'(?P<milliseconds>\d{2})'
                                                                             r'(?P<right_bracket>])')
    # 普通模式时间标签的正则表达式
    TIME_TAB_NORMAL_REGREX_SQUARE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)'
                                                                             r'(?P<minutes>\d{2})'
                                                                             r'(?P<minutes_seconds_seperator>:)'
                                                                             r'(?P<seconds>\d{2})'
                                                                             r'(?P<seconds_milliseconds_seperator>[:.])'
                                                                             r'(?P<milliseconds>\d{2,3})'
                                                                             r'(?P<right_bracket>])')
    # 宽松模式时间标签的正则表达式
    TIME_TAB_LOOSE_REGREX_SQUARE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[)'
                                                                            r'(?P<minutes>\d+)'
                                                                            r'(?P<minutes_seconds_seperator>:)'
                                                                            r'(?P<seconds>\d+)'
                                                                            r'(?P<seconds_milliseconds_seperator>[:.]?)'
                                                                            r'(?P<milliseconds>\d*)'
                                                                            r'(?P<right_bracket>])')
    # 非常宽松模式时间标签的正则表达式
    TIME_TAB_VERY_LOOSE_REGREX_SQUARE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>\[?)'
                                                                                 r'(?P<minutes>\d*?)'
                                                                                 r'(?P<minutes_seconds_seperator>:?)'
                                                                                 r'(?P<seconds>\d*?)'
                                                                                 r'(?P<seconds_milliseconds_seperator>'
                                                                                 r'[:.])?'
                                                                                 r'(?P<milliseconds>\d+)'
                                                                                 r'(?P<right_bracket>]?)')

    # 正则表达式列表
    TIME_TAB_MODE_REGREX_PAIR_SQUARE_BRACKETS: bidict[str, Pattern[str]] = bidict({
        MODE_TYPE[0]: TIME_TAB_STRICT_REGREX_SQUARE_BRACKETS,
        MODE_TYPE[1]: TIME_TAB_NORMAL_REGREX_SQUARE_BRACKETS,
        MODE_TYPE[2]: TIME_TAB_LOOSE_REGREX_SQUARE_BRACKETS,
        MODE_TYPE[3]: TIME_TAB_VERY_LOOSE_REGREX_SQUARE_BRACKETS
    })

    # 歌词每个字的时间标签的正则表达式 <>
    TIME_TAB_STRICT_REGREX_ANGLE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                            r'(?P<minutes>\d{2})'
                                                                            r'(?P<minutes_seconds_seperator>:)'
                                                                            r'(?P<seconds>\d{2})'
                                                                            r'(?P<seconds_milliseconds_seperator>\.)'
                                                                            r'(?P<milliseconds>\d{2})'
                                                                            r'(?P<right_bracket>>)')
    # 普通模式时间标签的正则表达式
    TIME_TAB_NORMAL_REGREX_ANGLE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                            r'(?P<minutes>\d{2})'
                                                                            r'(?P<minutes_seconds_seperator>:)'
                                                                            r'(?P<seconds>\d{2})'
                                                                            r'(?P<seconds_milliseconds_seperator>[:.])'
                                                                            r'(?P<milliseconds>\d{2,3})'
                                                                            r'(?P<right_bracket>>)')
    # 宽松模式时间标签的正则表达式
    TIME_TAB_LOOSE_REGREX_ANGLE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                           r'(?P<minutes>\d+)'
                                                                           r'(?P<minutes_seconds_seperator>:)'
                                                                           r'(?P<seconds>\d+)'
                                                                           r'(?P<seconds_milliseconds_seperator>[:.]?)'
                                                                           r'(?P<milliseconds>\d*)'
                                                                           r'(?P<right_bracket>>)')
    # 非常宽松模式时间标签的正则表达式
    TIME_TAB_VERY_LOOSE_REGREX_ANGLE_BRACKETS: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><?)'
                                                                                r'(?P<minutes>\d*?)'
                                                                                r'(?P<minutes_seconds_seperator>:?)'
                                                                                r'(?P<seconds>\d*?)'
                                                                                r'(?P<seconds_milliseconds_seperator>'
                                                                                r'[:.]?)'
                                                                                r'(?P<milliseconds>\d+)'
                                                                                r'(?P<right_bracket>>?)')

    # 正则表达式列表
    TIME_TAB_MODE_REGREX_PAIR_ANGLE_BRACKETS: bidict[str, Pattern[str]] = bidict({
        MODE_TYPE[0]: TIME_TAB_STRICT_REGREX_ANGLE_BRACKETS,
        MODE_TYPE[1]: TIME_TAB_NORMAL_REGREX_ANGLE_BRACKETS,
        MODE_TYPE[2]: TIME_TAB_LOOSE_REGREX_ANGLE_BRACKETS,
        MODE_TYPE[3]: TIME_TAB_VERY_LOOSE_REGREX_ANGLE_BRACKETS
    })


    # Final[bidict[str, str]]
    # noinspection PyTypeChecker
    VALID_BRACKET_PAIRS: Final[bidict] = bidict({'[': ']', '<': '>'})

    STANDARD_MINUTES_LEN: Final[int] = 2
    STANDARD_SECONDS_LEN: Final[int] = 2
    STANDARD_MILLISECONDS_LEN: Final[int] = 2

    STANDARD_MINUTES_SECONDS_SEPERATOR: Final[str] = ":"
    STANDARD_SECONDS_MILLISECONDS_SEPERATOR: Final[str] = "."

    """
    接受一个时间标签字符串，分离出时间标签的各个部分
    """

    def __init__(self, tab: Optional[str | UserString],
                 mode: Union[tuple[str, Optional[Pattern[str]]], list[str, Optional[Pattern[str]]]] = (
                 'normal', None)) -> None:
        """
        中文注释：
        接受一个时间标签字符串，分离出时间标签的各个部分

        English Comments:
        Accept a time label string and separate the various parts of the time label
        """

        # ================== 类的属性 ==================
        # 时间标签原始字符串，作为拷贝，
        self._original_time_tab: Optional[str] = tab
        # 时间标签字符串
        self._current_time_tab: Optional[str] = tab
        super().__init__(self._current_time_tab)

        # 模式 + 自定义正则表达式
        self._mode: tuple[str, Optional[Pattern[str]]] = mode

        self._match_result: Optional[Match[str]] = None

        # 时间标签类型 [] or <> or None
        self._brackets: Optional[list[str]] = None
        # 时间戳
        self._time_stamp: Optional[datetime.timedelta] = None

        # 分钟秒钟分割符
        self._minutes_seconds_seperator: Optional[str] = None
        # 秒钟毫秒分割符
        self._seconds_milliseconds_seperator: Optional[str] = None

        # inf 是自适应
        # 其他则是补0到指定位数
        # 时间标签分钟位数
        self._min_len_of_minutes: Optional[int | math.inf] = None  # 标准: 2
        # 时间标签秒位数
        self._min_len_of_seconds: Optional[int] = None  # 标准: 2
        # 时间标签毫秒位数
        self._len_of_millisecond: Optional[int] = None  # 标准: 2
        # 默认N位补全并超出部分截断
        self._cut_off_millisecond: bool = True  # 标准: True

        # ================== 类型检查 🛂🛡️ ==================
        # ------------------ tab ------------------
        # str 则是字符串相关都可以，包括 UserString
        # None 严格为 None
        var_type_guard(tab, (str, UserString, None))

        # ------------------ mode ------------------
        # mode 必须是 str + self_defined_regex
        # 必须是 strict, normal, loose, very_loose, self_defined
        var_type_guard(mode, (tuple,))
        # 必须是 strict, normal, loose, very_loose 或者 self_defined
        self.__mode_guard()

        # ================== 初始化 预处理 ==================
        # 预分离时间标签
        # None: 初始化
        # str: 时间标签字符串
        self._initialize_time_tab()

    # 返回时间标签时间戳
    def __int__(self):
        return self.get_millisecond_time_stamp()

    # str is same as the self.current_time_tab
    # Inherited from UserString

    # hash is not inherited from UserString
    # if __eq__ is defined, hash is disabled default
    # Use int to hash, time same then object same
    def __hash__(self):
        return hash(self.time_stamp)

    # 返回时间标签列表
    def __repr__(self):
        return self.current_time_tab

    def is_empty(self) -> bool:
        """
        中文：
        判断是否为空

        English:
        Determine if it is empty

        :return: 是否为空 Whether it is empty
        """
        return self._current_time_tab is None

    """
    预分离标签，判断是否合法，分离出时间标签的各个部分，储存到类的属性中，供其他方法调用
    私有方法
    """

    def _initialize_time_tab(self) -> None:
        """
        中文注释：
        预分离标签，判断是否合法，分离出时间标签的各个部分，储存到类的属性中，供其他方法调用
        私有方法

        English comment:
        Pre-separate the label, judge whether it is legal, separate the various parts of the time label,
        and store them in the properties of the class for other methods to call
        Private method

        :return: None
        """
        # None 则初始化，不会触及初始标签
        # if: 初始标签为 None
        if self.current_time_tab is None:
            # 匹配结果（粗处理）
            self._match_result = None

            # 描述符
            self._min_len_of_minutes = None
            self._min_len_of_seconds = None
            self._len_of_millisecond = None

            # 括号
            self._brackets = None

            # 分割符
            self._minutes_seconds_seperator = None
            self._seconds_milliseconds_seperator = None

            # 时间
            self._time_stamp = None

            return

        # else: 其他情况
        # 前面已经检查过了，直接匹配
        # 分离时间标签
        if self.mode == self.MODE_TYPE[4]:
            self._match_result = self.mode[1].match(self.current_time_tab)

        # 匹配结果（粗处理）
        self._match_result = self.TIME_TAB_MODE_REGREX_PAIR[self.mode[0]].match(self.current_time_tab)

        # ================== 判断是否合法 ==================
        if self._match_result is None:
            raise ValueError('Time tab is not valid: ' + self.current_time_tab + " under mode: " + self.mode[0])

        # ================== 分离时间/分隔符/括号 ==================
        # 添加到类的属性中
        # 描述符
        self._min_len_of_minutes = len(self._match_result.group('minutes'))
        self._min_len_of_seconds = len(self._match_result.group('seconds'))
        self._len_of_millisecond = len(self._match_result.group('milliseconds'))

        # 括号
        self._brackets = (self._match_result.group('left_bracket'), self._match_result.group('right_bracket'))

        # 分隔符
        self._minutes_seconds_seperator = self._match_result.group('minutes_seconds_seperator')
        self._seconds_milliseconds_seperator = self._match_result.group('seconds_milliseconds_seperator')

        # ================== 时间戳 ==================
        # ------------------ 转整数 ------------------
        # 自动计算时间戳
        # 要考虑没有("")的情况
        # "" 会被转换成 0
        minutes_int: int
        seconds_int: int
        milliseconds_int: int
        # 防止有 微秒 的情况
        microseconds_int: float

        # 时间
        minutes_int = int(self.match_result.group('minutes')) \
            if self.match_result.group('minutes') != "" else 0
        seconds_int = int(self.match_result.group('seconds')) \
            if self.match_result.group('seconds') != "" else 0

        # 毫秒特殊处理，小数点左边
        # 先标准化为3位（补全则补全0）（4位是因为需要微妙）
        milliseconds_str: str = self.match_result.group('milliseconds').rjust(4, "0")
        # 毫秒
        milliseconds_int = int(milliseconds_str[0:3])
        # 防止微秒
        microseconds_int = int(milliseconds_str[3:]) / (10 ** (len(milliseconds_str) - 3))

        # ------------------ 计算时间戳 ------------------
        # 调用函数，计算时间戳
        # 使用python 自带的 datetime.timedelta
        self._time_stamp = datetime.timedelta(minutes=minutes_int,
                                              seconds=seconds_int,
                                              milliseconds=milliseconds_int,
                                              microseconds=microseconds_int)

    def __mode_guard(self) -> None:
        # 先检查mode 是否是 self_defined
        # 不是则 self_defined_regex 必须是 None
        # 否则报 Warning
        # 是则 self_defined_regex 必须是 Pattern[str]
        if self.mode[0] != self.MODE_TYPE[4]:
            if self.mode[1] is not None:
                # warning
                warnings.warn('Mode is not "self_defined", self_defined_regex must be None')
            else:
                pass
        elif self.mode[0] in set(self.MODE_TYPE).remove(r'self_defined'):
            if isinstance(self.mode[0], Pattern):
                # check whether the group name is correct
                # 检查组名是否正确
                if self.SELF_DEFINED_GROUP_NAME.issubset(tuple(self.mode[1].groupindex.keys())):
                    pass
                else:
                    raise ValueError('The group name of self_defined_regex is not correct; \
                                     should contain ' + str(self.SELF_DEFINED_GROUP_NAME))
            else:
                raise TypeError('Mode is "self_defined", self_defined_regex must be Pattern[str]')
        else:
            raise ValueError('Mode must be in ' + str(self.MODE_TYPE))


    def get_millisecond_time_stamp(self) -> float:
        """
        中文：
        计算时间戳，分、秒、毫秒，小时（可选）
        返回毫秒位单位的时间戳(3位)

        English: 
        Calculate the time stamp, minute, second, millisecond, hour (optional) 
        Return the time stamp in milliseconds_str (3 digits)

        :return: 毫秒位单位的时间戳(3位) The time stamp in milliseconds_str (3 digits)
        """
        if self._time_stamp is None:
            raise ValueError("Not Initialized Time Stamp")

        # 括号不影响，不会转为元组
        return (int(self._time_stamp.total_seconds()) * self.CONVERSION_TIME_1000 +
                int(self._time_stamp.microseconds // self.CONVERSION_TIME_1000)
                )

    # ======================== 更新 tab，需要重新初始化 ========================
    @property
    def current_time_tab(self) -> str:
        """
        中文：
        返回时间标签字符串
        【修改会重新初始化】
        
        English: 
        Return the time label string
        [Changing will reinitialize]
        """
        return self._current_time_tab

    @current_time_tab.setter
    def current_time_tab(self, value: str | UserString) -> None:
        # ================== Type Guard 🛡️ ==================
        # str 则是字符串相关都可以，包括 UserString
        var_type_guard(value, (str, UserString))
        self._current_time_tab = value
        # 也会重置data
        self._initialize_time_tab()

    @property
    def mode(self) -> tuple[str, Optional[Pattern[str]]]:
        """
        中文：
        返回当前的匹配模式
        【修改会重新初始化】
        
        English: 
        Return the current matching mode
        [Changing will reinitialize]
        """
        return self._mode

    # 允许换一种匹配模式
    @mode.setter
    def mode(self, value: tuple[str, Optional[Pattern[str]]]):
        # ================== Type Guard 🛡️ ==================
        # mode 必须是 str + self_defined_regex
        var_type_guard(value, (tuple,))
        # 必须是 strict, normal, loose, very_loose 或者 self_defined
        self.__mode_guard()

        self._mode = value
        self._initialize_time_tab()

    # ======================== 不更新 tab，特殊值 ========================
    @property
    def original_time_tab(self) -> str:
        """
        中文：
        返回原始时间标签字符串
        
        English:
        Return the original time label string
        """
        return self._original_time_tab

    # 匹配结果不可更改
    @property
    def match_result(self) -> Match[str]:
        """
        中文
        返回匹配结果
        
        English:
        Return the match result
        """
        return self._match_result

    # ======================== 不更新 tab，因为最后是分隔符+时间+括号拼接 ========================
    # tab更新才需要重新初始化
    @property
    def brackets(self) -> list[str]:
        """
        中文：
        返回括号

        English:
        Return the brackets
        """
        return self._brackets

    @brackets.setter
    def brackets(self, value: tuple[str, str] | List[str] | UserList[str]) -> None:
        var_type_guard(value, (list, tuple, UserList))
        self._brackets = value

    @property
    def minutes_seconds_seperator(self) -> str:
        """
        中文：
        返回分钟秒钟分隔符

        English:
        Return the minute second separator
        """
        return self._minutes_seconds_seperator

    @minutes_seconds_seperator.setter
    def minutes_seconds_seperator(self, value: str) -> None:
        var_type_guard(value, (str,))
        self._minutes_seconds_seperator = value

    @property
    def seconds_milliseconds_seperator(self) -> str:
        """
        中文：
        返回秒钟毫秒分隔符

        English:
        Return the second millisecond
        """
        return self._seconds_milliseconds_seperator

    @seconds_milliseconds_seperator.setter
    def seconds_milliseconds_seperator(self, value: str) -> None:
        var_type_guard(value, (str,))
        self._seconds_milliseconds_seperator = value

    @property
    def time_stamp(self) -> datetime.timedelta:
        """
        中文：
        返回时间戳

        English:
        Return the time stamp
        """
        return self._time_stamp

    @time_stamp.setter
    def time_stamp(self, value: datetime.timedelta) -> None:
        var_type_guard(value, (datetime.timedelta,))
        self._time_stamp = value

    # ======================== len 时间标签位数，set也不更新tab ========================
    @property
    def min_len_of_minutes(self) -> int:
        """
        中文：
        返回分钟位数

        English:
        Return the number of minutes
        """
        return self._min_len_of_minutes

    @min_len_of_minutes.setter
    def min_len_of_minutes(self, value: int) -> None:
        # 范围检查
        int_leq_0_guard(value)
        self._min_len_of_minutes = value

    @property
    def min_len_of_seconds(self) -> int:
        """
        中文：
        返回秒钟位数

        English:
        Return the number of seconds
        """
        return self._min_len_of_seconds

    @min_len_of_seconds.setter
    def min_len_of_seconds(self, value: int) -> None:
        # 范围检查
        int_leq_0_guard(value)
        self._min_len_of_seconds = value

    @property
    def min_len_of_millisecond(self) -> int:
        """
        中文：
        返回毫秒位数

        English:
        Return the number of milliseconds
        """
        return self._len_of_millisecond

    @min_len_of_millisecond.setter
    def min_len_of_millisecond(self, value: int) -> None:
        # 范围检查
        int_leq_0_guard(value)
        self._len_of_millisecond = value

    @property
    def cut_off_millisecond(self) -> bool:
        """
        中文：
        返回是否截断毫秒位

        English:
        Return whether to cut off the milliseconds
        """
        return self._cut_off_millisecond

    @cut_off_millisecond.setter
    def cut_off_millisecond(self, value: bool) -> None:
        var_type_guard(value, (bool,))
        self._cut_off_millisecond = value

    # ======================== 其他方法 ========================

    """
    规范时间戳，按需求转为len_of_millisecond位的时间戳
    """


    def get_standard_time_stamp(self) -> int:
        """
        中文：
        返回规范的时间戳，以秒为单位

        English: 
        Return the standard time stamp in seconds

        :return: 规范的时间戳 The standard time stamp
        """
        return int(self.time_stamp.total_seconds())

    @staticmethod
    def match_under_mode(time_tab: str, mode: list[str, Optional[Pattern[str]]]) -> Optional[Match[str]]:
        """
        中文：
        判断时间标签是否合法

        English:
        Determine if the time label is valid

        :param time_tab: 时间标签 The time label
        :param mode: 模式 The mode
        :return: 是否合法 Whether it is valid
        """
        #   ================== 类型检查 🛂🛡️ ==================

        # ------------------ time_tab ------------------
        # str 则是字符串相关都可以，包括 UserString
        var_type_guard(time_tab, (str, UserString))

        # ------------------ mode ------------------
        # mode 必须是 str + self_defined_regex
        var_type_guard(mode, (list,))

        # 解包
        mode_type: str
        self_defined_regex: Optional[Pattern[str]]
        mode_type, self_defined_regex = mode

        # 必须是 strict, normal, loose, very_loose 或者 self_defined
        if mode_type in set(LyricTimeTab.MODE_TYPE).remove(r'self_defined'):
            if self_defined_regex is not None:
                # warning
                warnings.warn('Mode is not "self_defined", self_defined_regex must be None')
            else:
                pass
        else:
            if isinstance(self_defined_regex, Pattern):
                # check whether the group name is correct
                # 检查组名是否正确
                if LyricTimeTab.SELF_DEFINED_GROUP_NAME.issubset(tuple(self_defined_regex.groupindex.keys())):
                    pass
                else:
                    raise ValueError('The group name of self_defined_regex is not correct; \
                                     should contain ' + str(LyricTimeTab.SELF_DEFINED_GROUP_NAME))
            else:
                raise TypeError('Mode is "self_defined", self_defined_regex must be Pattern[str]')

        # ================== 判断是否合法 ==================
        # 正则
        if mode_type == LyricTimeTab.MODE_TYPE[4]:
            match_regex = self_defined_regex
        else:
            match_regex = LyricTimeTab.TIME_TAB_MODE_REGREX_PAIR[mode_type]

        # 匹配
        match_result: Optional[Match[str]] = match_regex.match(time_tab)

        # ================== 返回 ==================
        return match_result


    @staticmethod
    def is_valid_under_mode(time_tab: str, mode: list[str, Optional[Pattern[str]]]) -> bool:
        return LyricTimeTab.match_under_mode(time_tab, mode) is not None

    class __OperatorIntFloadGuard(object):
        def __init__(self, operator_name: str):
            self.operator_name = operator_name

        def __call__(self,
                     operator: Callable[["LyricTimeTab",
                                         Union[int, float, "LyricTimeTab", datetime.timedelta]
                                         ],
                                        "LyricTimeTab"]
                     ) -> Callable[[Any, Any], "LyricTimeTab"]:
            @wraps(operator)
            def decorated_operator(obj_instance: "LyricTimeTab", other):
                """
                中文：
                装饰器，用于检查加减乘除的类型是否正确 + 拷贝

                English: 
                Decorator, used to check whether the types of operations
                such as addition, subtraction, multiplication, and division are correct + copy

                :param obj_instance: 类的实例 The instance of the class
                :param other: 其他 The other
                :return: 返回实例 The instance
                """
                # 调用的时候一定要加入self的参数，self在这里不会被自动传入
                # 实例化类
                if isinstance(other, LyricTimeTab):
                    other: LyricTimeTab
                    # 复制之后再加，不改变原来的值
                    returned_instance: "LyricTimeTab" = copy.deepcopy(obj_instance)
                    returned_instance = operator(returned_instance, other.time_stamp)
                    # 不重新初始化，初始化只针对 current_time_tab

                    return returned_instance

                # 可以和 int 或者 float 加减乘除
                elif isinstance(other, (int, float)):
                    # 复制之后再加，不改变原来的值
                    returned_instance: "LyricTimeTab" = copy.deepcopy(obj_instance)
                    returned_instance = operator(returned_instance, datetime.timedelta(seconds=other))
                    # 不重新初始化，初始化只针对 current_time_tab

                    return returned_instance

                elif isinstance(other, datetime.timedelta):
                    # 复制之后再加，不改变原来的值
                    returned_instance: "LyricTimeTab" = copy.deepcopy(obj_instance)
                    returned_instance = operator(returned_instance, other)
                    # 不重新初始化，初始化只针对 current_time_tab

                    return returned_instance

                else:
                    raise TypeError("LyricTimeTab is not valid for" + self.operator_name +
                                    " with type " + str(type(other)) + ": " + str(other))

            return decorated_operator

    @__OperatorIntFloadGuard(operator_name="+")
    def __add__(self, other: Any) -> Any:
        self.time_stamp += other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="-")
    def __sub__(self, other: Any) -> Any:
        self.time_stamp -= other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="*")
    def __mul__(self, other: Any) -> Any:
        self.time_stamp *= other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="/")
    def __truediv__(self, other: Any) -> Any:
        self.time_stamp /= other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="//")
    def __floordiv__(self, other: Any) -> Any:
        self.time_stamp //= other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="%")
    def __mod__(self, other: Any) -> Any:
        self.time_stamp %= other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="**")
    def __pow__(self, other: Any) -> Any:
        self.time_stamp **= other

        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="<<")
    def __and__(self, other: Any) -> Any:
        self.time_stamp &= other
        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name=">>")
    def __or__(self, other: Any) -> Any:
        self.time_stamp |= other
        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="^")
    def __xor__(self, other: Any) -> Any:
        self.time_stamp ^= other
        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="<<")
    def __lshift__(self, other: Any) -> Any:
        self.time_stamp <<= other
        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name=">>")
    def __rshift__(self, other: Any) -> Any:
        self.time_stamp >>= other
        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    @__OperatorIntFloadGuard(operator_name="~")
    def __invert__(self) -> Any:
        self.time_stamp = datetime.timedelta(seconds=~int(self.time_stamp.total_seconds()))
        # 在装饰器里面已经重新初始化 + 拷贝了
        return self

    def __float__(self) -> Any:
        return self.time_stamp.total_seconds()

    def __eq__(self, other: Any) -> bool:
        # 实例化类
        if isinstance(other, LyricTimeTab):
            return self.time_stamp == other.time_stamp
        # int 或者 float
        elif isinstance(other, (int, float)):
            return self.time_stamp.total_seconds() == other
        # 非实例化类
        elif other == LyricTimeTab:
            return self.time_stamp == other.time_stamp
        else:
            raise TypeError("LyricTimeTab is not comparable with type " + str(type(other)) + " " + str(other))

    def __lt__(self: C, other: C) -> bool:
        # 实例化类
        if isinstance(other, LyricTimeTab):
            return self.time_stamp < other.time_stamp
        # int 或者 float
        elif isinstance(other, (int, float)):
            return self.time_stamp.total_seconds() < other
        # 非实例化类 也不可比较
        else:
            raise TypeError("LyricTimeTab is not comparable with type " + str(type(other)) + " " + str(other))

    @classmethod
    def convert_time_tab_to_time_tab_classmethod(cls,
                                                 time_stamp: datetime.timedelta,
                                                 min_len_of_minutes: Optional[Union[int, "math.inf"]] = 2,
                                                 min_len_of_seconds: Optional[int] = 2,
                                                 min_len_of_millisecond: Optional[Union[int, "math.inf"]] = 2,
                                                 cut_off_millisecond: bool = True,
                                                 brackets: List[str] | Tuple[str, str] = ("[", "]"),
                                                 seperator: List[str] | Tuple[str, str] = (":", ".")
                                                 ) -> str:
        """
        中文：
        将时间戳转为时间标签

        English: 
        It is a staticmethod. It converts the time stamp of time tag in to a tag.

        :param time_stamp: 时间戳 The time stamp
        :param min_len_of_minutes: 最小的分钟位数 The minimum number of minutes_str
        :param min_len_of_seconds: 最小的秒钟位数 The minimum number of seconds_str
        :param min_len_of_millisecond: 最小的毫秒位数 The minimum number of milliseconds_str
        :param cut_off_millisecond: 是否截断毫秒位 Whether to cut off the millisecond
        :param brackets: 括号 The brackets
        :param seperator: 分隔符 The seperator
        :return: 时间标签 The time tag
        """
        minutes_int: int
        seconds_int: int
        microsecond_int: int

        minutes_str: str
        seconds_str: str
        millisecond_str: str

        time_tab_output: str

        # 计算分秒毫秒，输入的时间戳是len_of_millisecond位相关的
        # // 返回int, 不用管类型提醒，第一行int可以不用加
        minutes_int = int(time_stamp.total_seconds() // cls.CONVERSION_TIME_60)
        seconds_int = int(time_stamp.total_seconds() % cls.CONVERSION_TIME_60)
        microsecond_int = time_stamp.microseconds
        millisecond_int = microsecond_int  # 因为左边是小数点，所以直接赋值

        # else:
        # 分 秒 毫秒
        minutes_str = str(minutes_int)
        seconds_str = str(seconds_int)
        millisecond_str = str(millisecond_int)
        # 不足则左边补0
        # 不为 inf
        if min_len_of_minutes != math.inf:
            minutes_str = minutes_str.rjust(min_len_of_minutes, "0")
        seconds_str = seconds_str.rjust(min_len_of_seconds, "0")
        # 右边补0
        # 不为 inf
        if min_len_of_millisecond != math.inf:
            millisecond_str = millisecond_str.ljust(min_len_of_millisecond, "0")
        # 截取
        if cut_off_millisecond:
            millisecond_str = millisecond_str[:min_len_of_millisecond]

        # 拼接
        time_tab_output = f"{brackets[0]}" \
                          f"{minutes_str}" \
                          f"{seperator[0]}{seconds_str}" \
                          f"{seperator[1]}{millisecond_str}"   \
                          f"{brackets[1]}"

        # 返回最终结果
        return time_tab_output


    def convert_to_time_tab(self,
                             min_len_of_minutes: Optional[Union[int, "math.inf"]] = 2,
                             min_len_of_seconds: Optional[int] = 2,
                             min_len_of_millisecond: Optional[Union[int, "math.inf"]] = 2,
                             cut_off_millisecond: bool = True,
                             brackets: List[str] | Tuple[str, str] = ("[", "]"),
                             seperator: List[str] | Tuple[str, str] = (":", ".")) -> str:
        """
        中文：
        将时间戳转为时间标签，对实例本身进行操作

        English:
        Convert the time stamp to a time tag and operate on the instance itself

        :return: 时间标签 The time tag
        """
        # 如果time stamp是None，返回空字符串，表明没有时间标签
        if self.time_stamp is None:
            raise ValueError("Not Initialized Time Stamp")
        else:
            return self.convert_time_tab_to_time_tab_classmethod(self.time_stamp,
                                                                 min_len_of_minutes,
                                                                 min_len_of_seconds,
                                                                 min_len_of_millisecond,
                                                                 cut_off_millisecond,
                                                                 brackets,
                                                                 seperator,
                                                                 )


    def convert_to_time_tab_base_on_inner_param(self) -> str:
        """
        中文：
        将时间戳转为时间标签，对实例本身进行操作

        English: 
        Convert the time stamp to a time tag and operate on the instance itself

        :return: 时间标签 The time tag
        """
        # 如果time stamp是None，返回空字符串，表明没有时间标签
        if self.time_stamp is None:
            raise ValueError("Not Initialized Time Stamp")
        else:
            return self.convert_time_tab_to_time_tab_classmethod(self.time_stamp,
                                                                 self.min_len_of_minutes,
                                                                 self.min_len_of_seconds,
                                                                 self.min_len_of_millisecond,
                                                                 self.cut_off_millisecond,
                                                                 self.brackets,
                                                                 (self.minutes_seconds_seperator,
                                                                  self.seconds_milliseconds_seperator)
                                                                 )
    def convert_to_time_tab_standard(self,
                                     brackets: Optional[tuple[str, str]]
                                     ) -> str:
        """
        中文：
        将时间戳转为标准时间标签

        English:
        Convert the time stamp to a standard time tag

        :param brackets: 括号 The brackets
        :return: 时间标签 The time tag
        """
        # 如果time stamp是None，返回空字符串，表明没有时间标签
        if self.time_stamp is None:
            raise ValueError("Not Initialized Time Stamp")
        else:
            return self.convert_time_tab_to_time_tab_classmethod(self.time_stamp,
                                                                 self.min_len_of_minutes,
                                                                 self.min_len_of_seconds,
                                                                 self.min_len_of_millisecond,
                                                                 self.cut_off_millisecond,
                                                                 brackets,
                                                                 (self.minutes_seconds_seperator,
                                                                  self.seconds_milliseconds_seperator)
                                                                 )


    # 返回自身
    def shift_time(self,
                   minutes: int,
                   seconds: int,
                   milliseconds: int
                   ) -> Self:
        """
        中文：
        将时间标签向前或向后移动

        English: 
        Move the time tag forward or backward

        :param minutes: 分钟数 The number of minutes_str
        :param seconds: 秒数 The number of seconds_str
        :param milliseconds: 毫秒数 The number of milliseconds_str
        """

        # 创建时间戳
        time_stamp: datetime.timedelta = datetime.timedelta(minutes=minutes,
                                                            seconds=seconds,
                                                            milliseconds=milliseconds)

        # 赋值
        self.time_stamp += time_stamp

        return self

    @classmethod
    def paring_brackets(cls,
                        brackets: tuple[str, str] | list[str],
                        pair_left_brackets: Optional[bool] = True,
                        ) -> tuple[str, str]:
        """
        中文：
        补全括号，默认是按照左括号配对 

        English: 
        Complete the brackets, default is paired according to the left bracket

        :param brackets: 括号 The brackets
        :param pair_left_brackets: 是否按照左括号配对 Whether to pair according to the left bracket
        :return: 补全后的括号 The completed brackets
        """
        # ================== 括号 ==================
        # 按照左括号配对
        if pair_left_brackets:
            # 左括号不在[[, <]中的任何一个，则默认为[
            if brackets[0] not in cls.VALID_BRACKET_PAIRS.keys():
                output_brackets = ('[', ']')
            # 补全括号
            else:
                output_brackets = (brackets[0], cls.VALID_BRACKET_PAIRS[brackets[0]])
        # 按照右括号配对
        else:
            # 右括号不在[[, <]中的任何一个，则默认为]
            if brackets[1] not in cls.VALID_BRACKET_PAIRS.values():
                output_brackets = ('[', ']')
            # 补全括号
            else:
                output_brackets = (cls.VALID_BRACKET_PAIRS.inverse[brackets[1]], brackets[1])

        return output_brackets

    # 返回自身
    def convert_to_standardized_time_tab(self,
                                         brackets: Optional[tuple[str, str]] = None,
                                         pair_left_brackets: Optional[bool] = True,
                                         ) -> str:
        """
        中文：
        格式化时间标签对象本身 
        把秒 限制在0-59之间 
        把毫秒 限制在0-999之间 
        并且补全括号，分隔符 
        如果brackets为None，括号默认是 按照左括号配对(pair_left_brackets) 
        否则按照右括号配对 
        左括号不在[[, <]中的任何一个，则默认为 [
        返回规范化后的自身

        English: 
        Format the time tag object itself
        Limit the seconds_str between 0 and 59 
        Limit the milliseconds_str between 0 and 999 
        And complete the brackets and seperator 
        If brackets is None, the brackets are paired according to the left bracket(pair_left_brackets) 
        Otherwise, pair according to the right bracket 
        If the left bracket is not in [[, <], it defaults to [ 
        Return the standardized self


        :return: self
        """
        # ================== 括号 ==================
        # 括号不给，使用默认
        if brackets is None:
            brackets = self.paring_brackets(self.brackets, pair_left_brackets)
        # 括号给了
        else:
            # 其实是 brackets = brackets
            pass

        # 直接输出TimeTab
        formatted_time_tab: str \
            = self.convert_time_tab_to_time_tab_classmethod(time_stamp=self.time_stamp,
                                                            min_len_of_minutes=self.STANDARD_MINUTES_LEN,
                                                            min_len_of_seconds=self.STANDARD_SECONDS_LEN,
                                                            min_len_of_millisecond=self.STANDARD_MILLISECONDS_LEN,
                                                            cut_off_millisecond=True, brackets=brackets,
                                                            seperator=(self.STANDARD_MINUTES_SECONDS_SEPERATOR,
                                                                       self.STANDARD_SECONDS_MILLISECONDS_SEPERATOR))

        return formatted_time_tab

    # 返回自身
    def standardize_self(self) -> Self:
        """
        中文：
        规范化自身，返回自身

        English: 
        Standardize the instance itself and return itself
        """
        # setter 会自动调用初始化函数
        self.current_time_tab = self.convert_to_standardized_time_tab()

        return self


"""
中文：
测试内容

English: 
Test content
"""
if __name__ == '__main__':
    # 打印正则表达式列表

    # 测试时间标签 += 运算符
    time_tab = LyricTimeTab("[00:00.00]", ('normal', "None"))
    # Check the next inheritance class in the inheritance chain
    print(time_tab.__class__.__mro__)
    print(time_tab.data)

    time_tab = time_tab + 1
    print(time_tab.convert_to_time_tab_base_on_inner_param())
    time_tab -= 1



    time_tab_1 = LyricTimeTab("00:00.0000>", ('very_loose', "None"))
    print(int(time_tab), int(time_tab_1))
    print(time_tab == time_tab_1)

    print({LyricTimeTab("<00:00.0000>", ('very_loose', None)), time_tab}
          == {LyricTimeTab("<00:00.0000>", ('very_loose', None)), time_tab_1}
          )