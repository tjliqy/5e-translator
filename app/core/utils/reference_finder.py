import os
from typing import List
from .utils import strip_name
def find_reference(text: str, target_dir: str = "/data/DND5e_chm") -> (List[str]):
    """
    在指定文件夹中查找包含text的文本，输出上下2行
    :param text: The text to search for a reference.
    :return: The reference list found in the text.
    """
    result = []
    striped_name = strip_name(text).replace(' ','')
    if striped_name == '' or len(striped_name) < 3:
        return []
    # 检查目标文件夹是否存在
    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        return [f"错误：文件夹 {target_dir} 不存在或不是一个有效的目录"]
    
    # 遍历文件夹中的所有文件
    for root, _, files in os.walk(target_dir):
        for file in files:
            # 处理文本文件（可根据需要扩展文件类型）
            if file.endswith(('.txt')):
            # if file.endswith(('.txt', '.html', '.md', '.chm','.htm')):
                file_path = os.path.join(root, file)
                
                try:
                    # 尝试以不同编码读取文件
                    encodings = ['utf-8', 'gbk', 'latin-1']
                    content = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.readlines()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        continue  # 无法解码的文件跳过
                    
                    # 查找包含目标文本的行（支持跨多行短语匹配）
                    # i = 0
                    # while i < len(content):
                    for i, c in enumerate(content):
                        c = c.replace('\n','').replace(' ','').lower()
                        # found = False
                        # 尝试不同的行跨度组合（1行到max_line_span行）
                        # for span in range(1, max_line_span + 1):
                        #     end_line = i + span
                        #     if end_line > len(content):
                        #         continue
                            
                            # 拼接连续行文本（保留原始空格和标点）
                            # combined_text = ''.join(content[i:end_line]).replace('\n','').replace(' ','')
                            
                            # 检查目标文本是否存在于拼接后的文本中
                        if striped_name in c:
                                
                                # 添加文件路径和跨行行号信息
                            result.append(f"文件: {file_path}, 行号: {i}")
                            result.append(content[i])
                            # 添加上下文（匹配行的上下各1行）
                            # context_start = max(0, i - 1)
                            # context_end = min(len(content), i + 3)
                                
                            # for line_idx in range(context_start, context_end):
                            #     line_num = line_idx + 1
                            #     # 为匹配范围内的所有行添加箭头标记
                            #     prefix = "→" if i == line_idx else " "
                            #     result.append(f"{prefix}{line_num}: {content[line_idx].rstrip()}")
                                
                            #     # 添加分隔线
                            #     result.append("-" * 80)
                            #     break
                        
                except Exception as e:
                    result.append(f"处理文件 {file_path} 时出错: {str(e)}")
    
    if not result:
        return [f"未找到包含 '{striped_name}' 的内容"]
    
    return result


if __name__ == "__main__":
    print(find_reference("Void Bolt"))