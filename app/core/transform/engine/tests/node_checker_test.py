# test_node_checker.py
import pytest
from bs4 import BeautifulSoup
from app.core.transform.engine.node_checker import NodeChecker, NodeType

@pytest.fixture
def node_checker():
    return NodeChecker()

def test_rate_h1(node_checker):
    """测试<h1>标签场景"""
    html = "<h1>Title</h1>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.h1
    assert node_checker.rate(node) == 100

def test_rate_font_with_color(node_checker):
    """测试<font color='#800000'>标签场景"""
    html = "<font color='#800000'>Title</font>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.font
    assert node_checker.rate(node) == 97

def test_rate_p_with_strong(node_checker):
    """测试<p><strong>标签场景"""
    html = "<p><strong>Title</strong></p>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.p
    assert node_checker.rate(node) == 96

    html = "<p><strong>Title</strong>content</p>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.p
    assert node_checker.rate(node) == NodeType.LINE.value

def test_rate_line_node(node_checker):
    """测试行节点场景"""
    html = "<p></p>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.p

    assert node_checker.rate(node) == NodeType.LINE.value

def test_rate_content_node(node_checker):
    """测试普通内容节点场景"""
    html = "<span>Content</span>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.span
    assert node_checker.rate(node) == NodeType.CONTENT.value

def test_rate_priority_order(node_checker):
    """测试条件优先级顺序"""
    # 同时满足多个条件时应该返回最高优先级（h1）
    html = "<h1 color='#800000'><strong>Title</strong></h1>"
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.h1
    assert node_checker.rate(node) == 100  # h1优先级最高