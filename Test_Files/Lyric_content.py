from MyLyric import Lyric_Time_tab


# 歌词类
class Lyric_content:

    def __init__(self, content: str):
        self.content: str = content

        # 是否为扩展歌词
        self.is_extend = False

        # 扩展歌词每个部分的时间列表
        self.extend_time: list[list[Lyric_Time_tab.Lyric_Time_tab, str]] = []

        # 预分离
        self.pre_separate(content)

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        return self.content[item]

    def __setitem__(self, key, value):
        self.content[key] = value

    def __delitem__(self, key):
        del self.content[key]

    def __iter__(self):
        return iter(self.content)

    def __reversed__(self):
        return reversed(self.content)

    def __contains__(self, item):
        return item in self.content

    def __add__(self, other):
        return Lyric_content(self.content + other)

    def __radd__(self, other):
        return Lyric_content(other + self.content)

    def __iadd__(self, other):
        return Lyric_content(self.content + other)

    def __mul__(self, other):
        return Lyric_content(self.content * other)

    def __rmul__(self, other):
        return Lyric_content(other * self.content)

    def __imul__(self, other):
        return Lyric_content(self.content * other)

    def __eq__(self, other):
        return self.content == other

    def __ne__(self, other):
        return self.content != other



    # 预分离处理
    def pre_separate(self, content: str):
        # [Time_tab 字词] 为一组
        ...


