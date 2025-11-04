import pytest
from unittest.mock import patch, MagicMock, call
from bs4 import BeautifulSoup
from pathlib import Path
from langchain_core.documents import Document


from app.core.transform.engine.parser import HtmlParser,NodeType, Attr

# 模拟NodeChecker类


class MockNodeChecker:
    def isPrimaryTitle(self, node):
        return False

    def isSecondaryTitle(self, node):
        return False

    def isContent(self, node):
        return False

    def isBR(self, node):
        return False

# 测试初始化方法
# def test_html_parser_initialization():
    # with patch('your_module.importlib.util.find_spec') as mock_find_spec:
    #     mock_find_spec.return_value = True  # 模拟lxml已安装
    #     parser = HtmlParser('test.html')
    #     assert parser.file_path == 'test.html'
    #     assert parser.open_encoding is None
    #     assert parser.bs_kwargs == {"features": "lxml"}
    #     assert len(parser.work_stack) == 0
    #     assert parser.current_checker == -1
    #     assert not parser.processed

# def test_html_parser_initialization_no_lxml():
#     with patch('your_module.importlib.util.find_spec') as mock_find_spec:
#         mock_find_spec.return_value = False  # 模拟lxml未安装
#         with pytest.raises(ImportError) as exc_info:
#             HtmlParser('test.html')
#         assert "lxml" in str(exc_info.value)

# 测试parse方法
# @patch('app.core.transform.engine.parser.HtmlParser.set_next_checker')
# @patch('app.core.transform.engine.parser.HtmlParser._HtmlParser__dfs')
# @patch('app.core.transform.engine.parser.HtmlParser._HtmlParser__process_result')
# def test_parse(mock_process_result, mock_dfs, mock_set_next):
#     mock_set_next.side_effect = [True, False]  # 第一次调用成功，第二次失败
#     mock_process_result.return_value = True
#     mock_soup = MagicMock()
#     mock_soup.body = MagicMock()

#     with patch('builtins.open', mock_open(read_data='<html><body></body></html>')) as mock_file, \
#          patch('your_module.BeautifulSoup', return_value=mock_soup) as mock_bs:

#         parser = HtmlParser('test.html')
#         result = parser.parse()

#         mock_bs.assert_called_once_with(mock_file.return_value, **{"features": "lxml"})
#         mock_dfs.assert_called_once_with(mock_soup.body)
#         mock_process_result.assert_called_once()
#         assert parser.processed == True
#         assert result == parser.work_stack

# 测试__process_result方法
# def test_process_result():
#     parser = HtmlParser('test.html')

#     # 测试空work_stack
#     assert parser._HtmlParser__process_result() == False

#     # 测试包含有效和无效节点的work_stack
#     valid_bean = MagicMock()
#     valid_bean.name = "Valid"
#     valid_bean.eng_name = "valid"

#     invalid_bean = MagicMock()
#     invalid_bean.name = ""
#     invalid_bean.eng_name = "invalid"

#     parser.work_stack = [valid_bean, invalid_bean]

#     with patch('builtins.print') as mock_print:
#         assert parser._HtmlParser__process_result() == True
#         mock_print.assert_called_once_with("Error：当前节点标签名: , 文本内容: ")

#     assert parser.dictionary == {"valid": {"Valid"}}

# 测试get_documents方法


def test_get_documents():
    parser = HtmlParser('test.html')

    doc1 = Document(page_content="content1")
    doc2 = Document(page_content="content2")

    bean1 = MagicMock()
    bean1.get_documents.return_value = [doc1]

    bean2 = MagicMock()
    bean2.get_documents.return_value = [doc2]

    parser.work_stack = [bean1, bean2]

    result = parser.get_documents()

    assert len(result) == 2
    assert result == [doc1, doc2]
    bean1.get_documents.assert_called_once()
    bean2.get_documents.assert_called_once()

# 测试set_next_checker方法


def test_set_next_checker():
    checker1 = MockNodeChecker()
    checker2 = MockNodeChecker()
    parser = HtmlParser('test.html', checker_list=[checker1, checker2])

    # 测试第一个checker
    assert parser.set_next_checker() == True
    assert parser.current_checker == 0
    assert parser.checker == checker1

    # 测试第二个checker
    assert parser.set_next_checker() == True
    assert parser.current_checker == 1
    assert parser.checker == checker2

    # 测试超出范围
    assert parser.set_next_checker() == False
    assert parser.current_checker == 2

# TODO:测试__parser方法
# 测试__html_to_lines方法


def test_html_to_lines(tmp_path):
    test_cases = [
        ('<html><body><h1>Normal</h1><p>Content</p></body></html>',
         ['Normal', 'Content'],
         [100, NodeType.LINE.value],
         1),
        ('<html><body><p>Main Title<p>Content</p></p></body></html>',
         ['Main Title', 'Content'],
         [NodeType.LINE.value, NodeType.LINE.value],
         1),
        ('<html><body><p>BR<br/>Content</p></body></html>',
         ['BR', 'Content'],
         [NodeType.LINE.value, NodeType.LINE.value],
         1),
        ('<html><body><p>Double\nBR<br/>Content</p></body></html>',
         ['DoubleBR', 'Content'],
         [NodeType.LINE.value, NodeType.LINE.value],
         1),
        ("""
<html><body><p>BR2
Content</p></body></html>
         """,
         ['BR2Content'],
         [NodeType.LINE.value],
         1),
        ('<html><body><h1>OutSpan<span>InSpan<span/>Content</h1></body></html>',
         ['OutSpanInSpanContent'],
         [100],
         1),
        ('<html><body><h1>Title1</h1><p>Content1</p><h1>Title2</h1><p>Content2</p></body></html>',
         ['Title1', 'Content1', 'Title2', 'Content2'],
         [100, NodeType.LINE.value, 100, NodeType.LINE.value],
         2),
    ]
    for html, expects, rates, bean_len in test_cases:
        html_file = tmp_path / "test.html"
        html_file.write_text(html)
        parser = HtmlParser(html_file)
        parser.parse()
        assert len(parser.lines) == len(expects), f"parser.lines 长度与 expects 不匹配，{html}"
        for w, e, r in zip(parser.lines, expects, rates):
            assert w.text == e, f"w.text 与 e 不匹配，{html}"
            assert w.rate == r, f"w.rate 与 r 不匹配，{html}"
        assert len(parser.work_stack) == bean_len, f"bean_len 错误{html}"
    # parser.checker = MagicMock()
    # node = MagicMock()

    # # 测试BR节点
    # parser.checker.isBR.return_value = True
    # res, text_type = parser._HtmlParser__html_to_lines(node)
    # assert res == ""
    # assert text_type == CONTENT

    # # 测试PrimaryTitle节点
    # parser.checker.isBR.return_value = False
    # parser.checker.isPrimaryTitle.return_value = True
    # parser.checker.isSecondaryTitle.return_value = False
    # parser.checker.isContent.return_value = True

    # mock_child1 = MagicMock()
    # mock_child1.name = None
    # mock_child1.__str__.return_value = "Child Text"

    # node.children = [mock_child1]

    # with patch.object(parser, '_HtmlParser__parser') as mock_parser:
    #     res, text_type = parser._HtmlParser__html_to_lines(node)
    #     mock_parser.assert_called_once_with("", ["Child Text"], TITLE_PRIMARY)
    #     assert res == ""
    #     assert text_type == CONTENT

    # # 测试Content节点
    # parser.checker.isPrimaryTitle.return_value = False
    # parser.checker.isSecondaryTitle.return_value = False
    # parser.checker.isContent.return_value = False

    # mock_child2 = MagicMock()
    # mock_child2.name = "span"
    # mock_child2.get_text.return_value = "Span Text"

    # node.children = [mock_child2]

    # with patch.object(parser, '_HtmlParser__dfs') as mock_dfs:
    #     mock_dfs.return_value = ("Span Text", CONTENT)
    #     res, text_type = parser._HtmlParser__html_to_lines(node)
    #     assert res == "Span Text"
    #     assert text_type == CONTENT

def test_html_to_table(tmp_path):
    html_file = tmp_path / "test.html"
    test_cases = [
        ("""
<html><body><table>
    <tr>
        <td>Data11</td>
        <td>Data12</td>
    </tr>
    <tr>
        <td>Data21</td>
        <td>Data22</td>
    </tr>
    <tr>
        <td>Data31</td>
        <td>Data32</td>
    </tr>
</table></body></html>
    """,
    [
        "Data11 Data12",
        "Data21 Data22",
        "Data31 Data32",
    ],1),
        ("""
<html><body><table>
    <tr>
        <td><strong>Header1</strong></td>
        <td><strong>Header2</strong></td>
    </tr>
    <tr>
        <td>Data11</td>
        <td>Data12</td>
    </tr>
    <tr>
        <td>Data21</td>
        <td>Data22</td>
    </tr>
</table></body></html>
        """,
        [
            "Header1:Data11 Header2:Data12",
            "Header1:Data21 Header2:Data22",
        ],1),
    ]
    for html, expects, stack_len in test_cases:
        
        html_file.write_text(html)
        parser = HtmlParser(html_file)
        parser.parse()
        assert len(parser.lines) == len(expects), f"parser.lines 长度与 expects 不匹配，{html}"
        for w, e in zip(parser.lines, expects):
            assert w.text == e, f"w.text 与 e 不匹配，{html}"
    
        assert len(parser.work_stack) == stack_len
