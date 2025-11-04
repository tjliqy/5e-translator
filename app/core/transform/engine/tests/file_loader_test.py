# tests/core/transform/engine/test_file_loader.py
import os
import pytest
from unittest.mock import patch, MagicMock
from app.core.transform.engine.chm_file_loader import load_html_to_documents

@pytest.fixture
def mock_html_files(tmp_path):
    # 创建临时HTML文件目录结构
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    
    # 创建测试HTML文件
    file1 = html_dir / "test1.html"
    file1.write_text("<html><body>Test1</body></html>")
    
    sub_dir = html_dir / "subdir"
    sub_dir.mkdir()
    file2 = sub_dir / "test2.html"
    file2.write_text("<html><body>Test2</body></html>")
    
    # 创建一个非HTML文件
    non_html = html_dir / "text.txt"
    non_html.write_text("Not HTML content")
    
    return str(html_dir)

def test_load_html_files_success(mock_html_files):
    """测试成功加载HTML文件"""
    result = load_html_to_documents(mock_html_files)
    
    assert len(result) == 2  # 应该加载2个HTML文件
    assert any("Test1" in str(doc) for doc in result)
    assert any("Test2" in str(doc) for doc in result)

def test_load_html_files_empty_dir(tmp_path):
    """测试空目录情况"""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    result = load_html_to_documents(str(empty_dir))
    assert len(result) == 0  # 应该返回空列表

def test_load_html_files_no_html_files(tmp_path):
    """测试目录中没有HTML文件的情况"""
    no_html_dir = tmp_path / "no_html"
    no_html_dir.mkdir()
    
    # 创建非HTML文件
    (no_html_dir / "file1.txt").write_text("Text file")
    (no_html_dir / "file2.json").write_text("{}")
    
    result = load_html_to_documents(str(no_html_dir))
    assert len(result) == 0  # 应该返回空列表

def test_load_html_files_with_loader_error(mock_html_files):
    """测试HTML加载器出错的情况"""
    with patch('app.core.transform.engine.file_loader.CHMFileLoader') as mock_loader:
        mock_loader.side_effect = Exception("Loader error")
        
        with pytest.raises(Exception):
            load_html_to_documents(mock_html_files)

def test_load_html_files_permission_error(mock_html_files):
    """测试目录无权限访问的情况"""
    with patch('os.walk') as mock_walk:
        mock_walk.side_effect = PermissionError("No permission")
        
        with pytest.raises(PermissionError):
            load_html_to_documents(mock_html_files)