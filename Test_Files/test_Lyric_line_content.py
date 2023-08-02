# 导入unittest模块
import unittest
from PyLrc import Lyric_line_content


# 定义一个测试类，继承自unittest.TestCase
class TestCheckPronunciationListValidity(unittest.TestCase):

    test_str_class_object = Lyric_line_content.Lyric_line_content("")

    # 定义一个测试方法，以test_开头
    def test_valid_pronunciation_list(self):
        # 定义一个有效的读音列表
        valid_pronunciation_list = [[self.test_str_class_object, 2],
                                    [self.test_str_class_object, None],
                                    [self.test_str_class_object, 1],
                                    [self.test_str_class_object, 0]]
        # 调用被测试的函数，断言返回值为True
        self.assertTrue(
            Lyric_line_content.Lyric_line_content.check_pronunciation_list_validity(valid_pronunciation_list))

    # 定义另一个测试方法，以test_开头
    def test_invalid_pronunciation_list(self):
        # 定义一个无效的读音列表
        invalid_pronunciation_list = [[self.test_str_class_object, 5], [self.test_str_class_object, 0]]
        # 调用被测试的函数，断言返回值为False
        self.assertFalse(
            Lyric_line_content.Lyric_line_content.check_pronunciation_list_validity(invalid_pronunciation_list))

    # 定义另一个测试方法，以test_开头
    def test_invalid_pronunciation_list_None1(self):
        # 定义一个无效的读音列表
        invalid_pronunciation_list = [[None, 0], [self.test_str_class_object, 0]]
        # 调用被测试的函数，断言返回值为False
        self.assertFalse(
            Lyric_line_content.Lyric_line_content.check_pronunciation_list_validity(invalid_pronunciation_list))

    # 定义更多的测试方法，以test_开头，使用不同的输入和期望的输出


# 如果是直接运行这个文件，执行所有的测试用例
if __name__ == '__main__':
    unittest.main()
