from typing import Optional, Self
from Lyric_Time_tab import Lyric_Time_tab
from Lyric_line_content import Lyric_line_content


class Lyric_line:

    def __init__(self,
                 time_tab_list: Optional[list[Lyric_Time_tab]],
                 lyric_content_list: list[Lyric_line_content]):

        # 歌词标签，用于适应多行合并的歌词
        # 自动排序
        self.time_tabs: Optional[list[Lyric_Time_tab]] = sorted(time_tab_list)

        self.lyric_contents: list[Lyric_line_content] = lyric_content_list

    def __str__(self):
        # 两个列表，一个是时间标签，一个是歌词内容
        # 各自拼接
        time_tabs_str = ""
        for time_tab in self.time_tabs:
            time_tabs_str += str(time_tab)

        lyric_contents_str = ""
        for lyric_content in self.lyric_contents:
            lyric_contents_str += str(lyric_content)

        return time_tabs_str + lyric_contents_str

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.time_tabs)

    def __getitem__(self, item):
        # 直接合并歌词列表
        lyric_contents_str = ""
        for lyric_content in self.lyric_contents:
            lyric_contents_str += str(lyric_content)

        # 加个时间头输出
        return str(self.time_tabs[item]) + lyric_contents_str

    def __setitem__(self, key, value: Lyric_Time_tab):
        self.time_tabs[key] = value

    def __delitem__(self, key):
        del self.time_tabs[key]

    def __iter__(self):
        # 返回每个时间标签+歌词内容
        for time_tab in self.time_tabs:
            lyric_contents_str = ""
            for lyric_content in self.lyric_contents:
                lyric_contents_str += str(lyric_content)

            yield time_tab + lyric_contents_str

    def __reversed__(self):
        # 返回每个时间标签+歌词内容

        for time_tab in reversed(self.time_tabs):
            lyric_contents_str = ""
            for lyric_content in self.lyric_contents:
                lyric_contents_str += str(lyric_content)

            yield time_tab + lyric_contents_str

    def __contains__(self, item: Lyric_Time_tab):
        return item in self.time_tabs

    # 大小比较，以第一个时间标签为准
    def __lt__(self, other):
        return self.time_tabs[0] < other.time_tabs[0]

    def __le__(self, other):
        return self.time_tabs[0] <= other.time_tabs[0]

    def __eq__(self, other):
        return self.time_tabs[0] == other.time_tabs[0]

    def __ne__(self, other):
        return self.time_tabs[0] != other.time_tabs[0]

    def __gt__(self, other):
        return self.time_tabs[0] > other.time_tabs[0]

    def __ge__(self, other):
        return self.time_tabs[0] >= other.time_tabs[0]

    # 不支持加减乘除，防止混乱

    # 解构，返回每个时间标签和歌词内容 的列表
    def decompress_time_tab(self) -> list[Self]:
        output_list: list[Self] = []

        # 返回每个时间标签+歌词内容 的 Lyric_line 列表
        for time_tab in self.time_tabs:
            # 用每个时间标签 和 所有的歌词内容，新建一个 Lyric_line 对象
            new_lyric_line_object: Self = Lyric_line([time_tab], self.lyric_contents)

            # 添加到列表
            output_list.append(new_lyric_line_object)

        return output_list

    # 格式化输出
    def format_output(self,
                      len_of_millisecond_output: int = 2,
                      seperator_each_line: tuple[str, str] = (":", "."),
                      seperator_inline: tuple[str, str] = (":", ".")
                      ) -> str:

        # 用于输出字符串
        output_str: str = ""

        time_tab_str: str
        lyric_content_str: str

        # 遍历时间标签
        for time_tab in self.time_tabs:
            # 用于输出字符串
            time_tab_str = time_tab.convert_to_time_tab(len_of_millisecond_output=len_of_millisecond_output,
                                                        seperator=seperator_each_line)
            output_str += time_tab_str

        for lyric_content in self.lyric_contents:
            # 用于输出字符串
            lyric_content_str = lyric_content.format_content(len_of_millisecond_output=len_of_millisecond_output,
                                                             seperator=seperator_inline)
            output_str += lyric_content_str

        return output_str

    # 判断是否是同一句歌词
    def whether_same_lyric(self,
                           other: Self
                           ) -> bool:
        # 不管时间标签
        # 只看歌词内容
        return self.lyric_contents == other.lyric_contents


if __name__ == '__main__':
    # 测试
    # 新定义几个时间标签
    time_tab1 = Lyric_Time_tab("[00:00.00]")
    time_tab2 = Lyric_Time_tab("[00:01.00]")
    time_tab3 = Lyric_Time_tab("[00:02.00]")
    time_tab4 = Lyric_Time_tab("[00:03.00]")
    time_tab5 = Lyric_Time_tab("[00:04.00]")

    # 新定义几个歌词内容
    lyric_content1 = Lyric_line_content("歌词1")

    # 打乱顺序，组成乱序列表，用于测试
    time_tabs = [time_tab1, time_tab3, time_tab2, time_tab5, time_tab4]

    # 输入时间标签和歌词内容
    lyric_line = Lyric_line(time_tabs, [lyric_content1])

    # 输出
    print(str(lyric_line))
    print(repr(lyric_line))
    print(len(lyric_line))
    print(lyric_line.decompress_time_tab())
