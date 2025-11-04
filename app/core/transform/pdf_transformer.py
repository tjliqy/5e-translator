import os
import fitz  # PyMuPDF库，用于更精确地提取文本和字体信息
import re
import numpy as np
# from sentence_transformers import SentenceTransformer, util
import jieba
from typing import List, Tuple, Dict
def transform_pdf(pdf_file: str):
    """将PDF文件按段落分段，根据字体大小识别标题

    Args:
        pdf_file (str): PDF文件路径
    Returns:
        list[dict]: 包含标题和内容的段落列表，每个元素为{'title': str, 'content': str}
    """
    # 检查文件是否存在
    if not os.path.exists(pdf_file):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_file}")
    
    # 检查文件是否为PDF格式
    if not pdf_file.lower().endswith('.pdf'):
        raise ValueError(f"文件不是PDF格式: {pdf_file}")
    
    try:
        # 打开PDF文件
        doc = fitz.open(pdf_file)
        
        # 存储所有段落的列表，每个段落包含标题和内容
        paragraphs = []
        
        # 当前正在处理的段落
        current_paragraph = {
            'title': '',
            'content': []
        }
        all_blocks = []
        # 遍历每一页
        for page_num in range(len(doc)):
            # 获取当前页
            page = doc[page_num]
            
            # 提取页面中的所有文本块（包含字体信息）
            blocks = page.get_text("dict")["blocks"]
            all_blocks.extend(blocks)
            
        # 用于存储当前页的所有字体大小
        font_sizes = []
        
        # 第一次遍历：收集所有字体大小，用于确定标题阈值
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span.get("size") and span.get("text").strip():
                            font_sizes.append(span["size"])
        
        # 如果没有找到字体大小，使用默认阈值
        if not font_sizes:
            title_font_threshold = 14  # 默认标题字体大小阈值
        else:
            # 计算字体大小的中位数作为标题判断的参考
            font_sizes.sort()
            mid_index = len(font_sizes) // 2
            title_font_threshold = font_sizes[mid_index] * 1.2  # 比平均字体大20%的作为标题
        # print(title_font_threshold)
        # 第二次遍历：根据字体大小识别标题和正文
        pre_title = ""
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span.get("text", "").strip()
                        if not text or text.isspace():
                            continue
                        
                        # 获取字体大小
                        font_size = span.get("size", 0)
                        
                        # 判断是否为标题（字体较大）
                        if font_size >= title_font_threshold:
                            # 如果当前已有正在处理的段落且内容不为空，保存当前段落
                            if current_paragraph['title'] or current_paragraph['content']:
                                if not current_paragraph['title']:
                                    current_paragraph['title'] = pre_title
                                paragraphs.append(current_paragraph)
                            pre_title = text
                            # 开始新的段落，设置标题
                            current_paragraph = {
                                'title': text,
                                'content': []
                            }
                        elif text != '':
                            # 正文内容，添加到当前段落
                            current_paragraph['content'].append(text)
        
        # 添加最后一个段落（如果有）
        if current_paragraph['title'] or current_paragraph['content']:
            paragraphs.append(current_paragraph)
        
        # 关闭文档
        doc.close()
        
        return paragraphs
    
    except Exception as e:
        raise RuntimeError(f"处理PDF文件时出错: {str(e)}")
    
    

def transform_pdf_to_sentences(pdf_file: str) -> (List[str]):
    """将PDF文件按段落分段，根据字体大小识别标题

    Args:
        pdf_file (str): PDF文件路径
    Returns:
        list[dict]: 包含标题和内容的段落列表，每个元素为{'title': str, 'content': str}
    """
    res = []
    paragraphs = transform_pdf(pdf_file)
    for paragraph in paragraphs:
        res.append(paragraph['title'] + ' '.join(paragraph['content']))
    return res

class SentenceMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化句子匹配器
        :param model_name: 预训练的跨语言模型名称
        """
        # 加载多语言句子嵌入模型
        # self.model = SentenceTransformer(model_name)
        
        # 中文分句的标点符号
        self.chinese_punctuation = r"。！？；…"
        self.chinese_sentence_pattern = re.compile(f'([^{self.chinese_punctuation}]*[{self.chinese_punctuation}])')
    
    def split_chinese_sentences(self, text: str) -> (List[str]):
        """
        将中文文本分割为句子
        :param text: 未分句的中文文本
        :return: 分句后的中文句子列表
        """
        sentences = self.chinese_sentence_pattern.findall(text)
        # 处理可能遗漏的最后一个句子
        last_sentence = re.sub(f'[{self.chinese_punctuation}]$', '', text)
        if last_sentence and not any(last_sentence in s for s in sentences):
            sentences.append(last_sentence.strip() + '。')
        
        # 清洗句子，去除空字符串和多余空格
        return [s.strip() for s in sentences if s.strip()]
    
    def process_chinese_text(self, chinese_text: str) -> (List[str]):
        """
        处理中文文本，包括分句和预处理
        :param chinese_text: 原始中文文本
        :return: 处理后的中文句子列表
        """
        return self.split_chinese_sentences(chinese_text)
    
    def match_sentences(self, english_sentences: List[str], chinese_sentences: List[str], 
                       threshold: float = 0.5) -> (List[Dict]):
        """
        匹配英文句子和中文句子
        :param english_sentences: 已分句的英文句子列表
        :param chinese_sentences: 已分句的中文句子列表
        :param threshold: 相似度阈值，低于此值则认为无匹配
        :return: 匹配结果列表，包含英文句子、匹配的中文句子、相似度和是否为新增内容
        """
        # 生成嵌入向量
        english_embeddings = self.model.encode(english_sentences, convert_to_tensor=True)
        chinese_embeddings = self.model.encode(chinese_sentences, convert_to_tensor=True)
        
        # 计算相似度矩阵
        cosine_scores = util.cos_sim(english_embeddings, chinese_embeddings)
        
        results = []
        matched_chinese_indices = set()
        
        # 为每个英文句子找到最匹配的中文句子
        for i, english_sentence in enumerate(english_sentences):
            # 找到最相似的中文句子
            scores = cosine_scores[i].cpu().numpy()
            max_score_idx = np.argmax(scores)
            max_score = scores[max_score_idx]
            
            # 检查是否超过阈值且中文句子未被匹配
            if max_score >= threshold and max_score_idx not in matched_chinese_indices:
                matched_chinese_indices.add(max_score_idx)
                chinese_sentence = chinese_sentences[max_score_idx]
                is_new = False
            else:
                chinese_sentence = ""
                is_new = True
            
            results.append({
                "english": english_sentence,
                "chinese": chinese_sentence,
                "similarity": float(max_score),
                "is_new": is_new
            })
        
        return results
    
    def save_matches_to_file(self, matches: List[Dict], output_file: str):
        """
        将匹配结果保存到文件
        :param matches: 匹配结果列表
        :param output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("英文句子 | 中文译文 | 相似度 | 是否为新增内容\n")
            f.write("-" * 80 + "\n")
            
            for match in matches:
                f.write(f"{match['english']} | {match['chinese']} | {match['similarity']:.4f} | {match['is_new']}\n\n")

# 使用示例
if __name__ == "__main__":
    # 初始化匹配器
    matcher = SentenceMatcher()
    
    # 示例：已分句的英文句子（修订版）
    english_sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence is transforming the world.",
        "This is a new paragraph added in the revised version.",
        "Natural language processing allows computers to understand text.",
        "Machine learning algorithms can predict future trends."
    ]
    
    # 示例：未分句的中文译文（初版）
    chinese_text = """敏捷的棕色狐狸跳过了懒惰的狗。人工智能正在改变世界。自然语言处理使计算机能够理解文本。机器学习算法可以预测未来趋势。这是一段额外的中文内容，用于测试匹配效果。"""
    
    # 处理中文文本（分句）
    chinese_sentences = matcher.process_chinese_text(chinese_text)
    print("中文分句结果:")
    for i, sent in enumerate(chinese_sentences, 1):
        print(f"{i}. {sent}")
    
    # 匹配句子
    matches = matcher.match_sentences(english_sentences, chinese_sentences, threshold=0.4)
    
    # 打印匹配结果
    print("\n匹配结果:")
    for i, match in enumerate(matches, 1):
        print(f"句子 {i}:")
        print(f"英文: {match['english']}")
        print(f"中文: {match['chinese']}")
        print(f"相似度: {match['similarity']:.4f}")
        print(f"是否为新增内容: {'是' if match['is_new'] else '否'}\n")
    
    # 保存结果到文件
    matcher.save_matches_to_file(matches, "sentence_matches.txt")
    print("匹配结果已保存到 sentence_matches.txt")
    
# if __name__ == "__main__":
#     paragraphs = transform_pdf("/data/5e-translator/data/idrotf.pdf")
#     print(len(paragraphs))
#     for p in paragraphs:
#         if p['title'] == "":
#             print(p)
