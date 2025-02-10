import datetime
import re
from typing import Final, Pattern

t = datetime.time(minute=2, second=3, microsecond=4)

print(datetime.timedelta(seconds=400.2200) + datetime.timedelta(seconds=1))

TIME_TAB_EACH_WORD_NORMAL_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket><)'
                                                                   r'(?P<minutes>\d{2})'
                                                                   r'(?P<minutes_seconds_seperator>:)'
                                                                   r'(?P<seconds>\d{2})'
                                                                   r'(?P<seconds_milliseconds_seperator>[:.])'
                                                                   r'(?P<milliseconds>\d*)'
                                                                   r'(?P<right_bracket>>)')

# REGREX group name
# 自定义必须包含的组名
SELF_DEFINED_GROUP_NAME: Final[tuple[str, ...]] = ('left_bracket', 'minutes', 'minutes_seconds_seperator',
                                                   'seconds', 'seconds_milliseconds_seperator', 'milliseconds',
                                                   'right_bracket')

print(set(SELF_DEFINED_GROUP_NAME).issubset(set(TIME_TAB_EACH_WORD_NORMAL_REGREX.groupindex.keys())) )

# 格式化输出 timedelta %H:%M:%S.%f
print(datetime.timedelta(seconds=-400000.2200))


match_obj = TIME_TAB_EACH_WORD_NORMAL_REGREX.match("<00:00.>")

print(match_obj.group('milliseconds') == "")





