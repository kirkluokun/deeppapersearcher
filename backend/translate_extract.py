"""
翻译和关键词提取模块
使用 Gemini 2.0 Flash 将摘要翻译成中文并提取关键词
支持使用 Gemini 2.5 Flash 精炼摘要，使其通俗易懂
"""

from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config import GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_REFINE_MODEL, GEMINI_REFINE_TEMPERATURE
import logging

logger = logging.getLogger(__name__)

# 初始化 LLM（用于翻译和关键词提取）
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=GEMINI_TEMPERATURE,
    convert_system_message_to_human=True
)

# 初始化精炼 LLM（用于摘要精炼）
refine_llm = ChatGoogleGenerativeAI(
    model=GEMINI_REFINE_MODEL,
    temperature=GEMINI_REFINE_TEMPERATURE,
    convert_system_message_to_human=True
)

# 精炼结果缓存（使用字典存储，key 为 arxiv_id + abstract 的哈希）
_refine_cache = {}


def translate_and_extract_keywords(paper: Dict, user_question: str = "") -> Dict[str, str]:
    """
    将论文摘要翻译成中文并提取中文关键词，同时评估是否能解决用户问题
    
    Args:
        paper: 论文字典，包含 title 和 abstract
        user_question: 用户的问题，用于评估相关性
        
    Returns:
        包含 title_zh, abstract_zh, keywords, relevance_summary 的字典
    """
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    
    # 确保 title 和 abstract 是字符串类型
    if not isinstance(title, str):
        title = str(title) if title else ""
    if not isinstance(abstract, str):
        abstract = str(abstract) if abstract else ""
    
    # 如果没有摘要（Semantic Scholar 可能没有），仍然提取关键词和评估相关性
    if not abstract or abstract == "(Semantic Scholar 数据源中未提供摘要)":
        # 仅基于标题进行评估
        title_escaped = title.replace('{', '{{').replace('}', '}}')
        question_escaped = user_question.replace('{', '{{').replace('}', '}}')
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("user",
             "请完成以下任务：\n\n"
             "1. 从论文标题中提取3-5个中文关键词，用中文逗号分隔\n"
             "2. 评估这篇论文是否能解决用户的问题，给出一个极简的概述（1-2句话）\n\n"
             "用户问题: {user_question}\n\n"
             "论文标题: {title}\n\n"
             "注意：这篇论文没有提供摘要。\n\n"
             "请按照以下格式返回（JSON格式）：\n"
             "{{\n"
             "  \"keywords\": \"关键词1，关键词2，关键词3\",\n"
             "  \"relevance_summary\": \"能否解决用户问题的极简概述\"\n"
             "}}\n\n"
             "只返回JSON，不要包含其他文字。")
        ])
        
        try:
            chain = prompt_template | llm
            response = chain.invoke({
                "title": title_escaped,
                "user_question": question_escaped
            })
            
            response_text = response.content.strip()
            import json
            import re
            
            json_match = re.search(r'\{[^{}]*"keywords"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
            
            json_str = json_str.replace('```json', '').replace('```', '').strip()
            
            try:
                result = json.loads(json_str)
                return {
                    "title_zh": title,  # 无摘要时，标题翻译可能失败，使用原标题
                    "abstract_zh": "(Semantic Scholar 数据源中未提供摘要)",
                    "keywords": result.get("keywords", ""),
                    "relevance_summary": result.get("relevance_summary", "")
                }
            except json.JSONDecodeError:
                keywords_match = re.search(r'"keywords":\s*"([^"]+)"', response_text)
                relevance_match = re.search(r'"relevance_summary":\s*"([^"]+)"', response_text)
                
                return {
                    "title_zh": title,  # 无摘要时，标题翻译可能失败，使用原标题
                    "abstract_zh": "(Semantic Scholar 数据源中未提供摘要)",
                    "keywords": keywords_match.group(1) if keywords_match else "",
                    "relevance_summary": relevance_match.group(1) if relevance_match else ""
                }
        except Exception as e:
            print(f"处理无摘要论文失败: {str(e)}")
            return {
                "title_zh": title,  # 无摘要时，标题翻译可能失败，使用原标题
                "abstract_zh": "(Semantic Scholar 数据源中未提供摘要)",
                "keywords": "",
                "relevance_summary": ""
            }
    
    # 转义花括号
    title_escaped = title.replace('{', '{{').replace('}', '}}')
    abstract_escaped = abstract.replace('{', '{{').replace('}', '}}')
    question_escaped = user_question.replace('{', '{{').replace('}', '}}')
    
    # 构建 prompt（包含标题翻译）
    prompt_template = ChatPromptTemplate.from_messages([
        ("user",
         "请完成以下任务：\n\n"
         "1. 将论文标题翻译成中文（如果已经是中文，保持原样）\n"
         "2. 将以下论文摘要翻译成中文（如果已经是中文，保持原样）\n"
         "3. 从摘要中提取3-5个中文关键词，用中文逗号分隔\n"
         "4. 评估这篇论文是否能解决用户的问题，给出一个极简的概述（1-2句话）\n\n"
         "用户问题: {user_question}\n\n"
         "论文标题: {title}\n\n"
         "摘要:\n{abstract}\n\n"
         "请按照以下格式返回（JSON格式）：\n"
         "{{\n"
         "  \"title_zh\": \"翻译后的中文标题\",\n"
         "  \"abstract_zh\": \"翻译后的中文摘要\",\n"
         "  \"keywords\": \"关键词1，关键词2，关键词3\",\n"
         "  \"relevance_summary\": \"能否解决用户问题的极简概述\"\n"
         "}}\n\n"
         "只返回JSON，不要包含其他文字。")
    ])
    
    try:
        chain = prompt_template | llm
        response = chain.invoke({
            "title": title_escaped,
            "abstract": abstract_escaped,
            "user_question": question_escaped
        })
        
        response_text = response.content.strip()
        
        # 尝试解析 JSON
        import json
        import re
        
        # 提取 JSON 部分（可能包含 markdown 代码块）
        json_match = re.search(r'\{[^{}]*"abstract_zh"[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            # 如果没有找到 JSON，尝试直接解析
            json_str = response_text
        
        # 清理可能的 markdown 代码块标记
        json_str = json_str.replace('```json', '').replace('```', '').strip()
        
        try:
            result = json.loads(json_str)
            return {
                "title_zh": result.get("title_zh", title),  # 如果解析失败，使用原标题
                "abstract_zh": result.get("abstract_zh", abstract),  # 如果解析失败，使用原摘要
                "keywords": result.get("keywords", ""),
                "relevance_summary": result.get("relevance_summary", "")
            }
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，尝试手动提取
            title_zh_match = re.search(r'"title_zh":\s*"([^"]+)"', response_text)
            abstract_zh_match = re.search(r'"abstract_zh":\s*"([^"]+)"', response_text)
            keywords_match = re.search(r'"keywords":\s*"([^"]+)"', response_text)
            relevance_match = re.search(r'"relevance_summary":\s*"([^"]+)"', response_text)
            
            return {
                "title_zh": title_zh_match.group(1) if title_zh_match else title,
                "abstract_zh": abstract_zh_match.group(1) if abstract_zh_match else abstract,
                "keywords": keywords_match.group(1) if keywords_match else "",
                "relevance_summary": relevance_match.group(1) if relevance_match else ""
            }
        
    except Exception as e:
        print(f"翻译和关键词提取失败: {str(e)}")
        # 如果失败，返回原标题、原摘要和空关键词
        return {
            "title_zh": title,  # 如果翻译失败，使用原标题
            "abstract_zh": abstract,  # 如果翻译失败，使用原摘要
            "keywords": "",
            "relevance_summary": ""
        }


def process_papers(papers: List[Dict], user_question: str = "", progress_callback=None) -> List[Dict]:
    """
    批量处理论文，添加翻译和关键词
    使用并发处理提高速度，同时支持进度回调
    
    Args:
        papers: 论文列表
        user_question: 用户问题，用于评估相关性
        progress_callback: 进度回调函数，接收 (current, total, paper_title) 参数
        
    Returns:
        处理后的论文列表，每篇论文包含 abstract_zh, keywords, relevance_summary 字段
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import logging
    
    logger = logging.getLogger(__name__)
    
    # 创建索引映射，保持顺序（使用统一的论文 ID）
    paper_index_map = {}
    for i, paper in enumerate(papers):
        paper_id = paper.get('arxiv_id') or paper.get('paper_id', f'paper_{i}')
        paper_index_map[paper_id] = i
    results = [None] * len(papers)  # 预分配结果列表
    completed_count = 0
    total = len(papers)
    
    # 使用线程池并发处理（最多5个并发，避免API限制）
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务，并记录索引
        future_to_index = {}
        for i, paper in enumerate(papers):
            paper_id = paper.get('arxiv_id') or paper.get('paper_id', f'paper_{i}')
            index = paper_index_map[paper_id]
            future_to_index[executor.submit(translate_and_extract_keywords, paper, user_question)] = index
        
        # 收集结果并保持顺序
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            paper = papers[index]
            try:
                result = future.result()
                paper_with_translation = {
                    **paper,
                    "title_zh": result.get("title_zh", paper.get("title", "")),
                    "abstract_zh": result["abstract_zh"],
                    "keywords": result["keywords"],
                    "relevance_summary": result["relevance_summary"]
                }
                results[index] = paper_with_translation
                completed_count += 1
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(completed_count, total, paper.get('title', ''))
            except Exception as e:
                logger.warning(f"处理论文失败: {str(e)}")
                # 如果处理失败，使用原论文数据
                paper_with_translation = {
                    **paper,
                    "title_zh": paper.get("title", ""),
                    "abstract_zh": paper.get("abstract", "") or "(Semantic Scholar 数据源中未提供摘要)",
                    "keywords": "",
                    "relevance_summary": ""
                }
                results[index] = paper_with_translation
                completed_count += 1
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(completed_count, total, paper.get('title', ''))
    
    return results


def refine_abstract(arxiv_id: str, abstract: str, title: str = "") -> str:
    """
    精炼论文摘要，使其通俗易懂，帮助用户理解论文内容
    
    使用 Gemini 2.5 Flash 模型，根据 LLM 的理解来精炼摘要，
    要求：精炼、通俗易懂、解释清楚说了啥
    
    Args:
        arxiv_id: arXiv 论文 ID（用于缓存）
        abstract: 原始摘要（可以是中文或英文）
        title: 论文标题（可选，有助于理解上下文）
        
    Returns:
        精炼后的摘要（中文）
    """
    import hashlib
    
    # 生成缓存键（基于 arxiv_id 和 abstract）
    cache_key = hashlib.md5(f"{arxiv_id}:{abstract}".encode()).hexdigest()
    
    # 检查缓存
    if cache_key in _refine_cache:
        logger.info(f"使用缓存的精炼结果: {arxiv_id}")
        return _refine_cache[cache_key]
    
    # 确保输入是字符串
    if not isinstance(abstract, str):
        abstract = str(abstract) if abstract else ""
    if not isinstance(title, str):
        title = str(title) if title else ""
    
    if not abstract:
        return "（摘要为空）"
    
    # 转义花括号
    title_escaped = title.replace('{', '{{').replace('}', '}}')
    abstract_escaped = abstract.replace('{', '{{').replace('}', '}}')
    
    # 构建精炼 prompt
    # 要求：更加精炼、去除冗余、简洁明了
    prompt_template = ChatPromptTemplate.from_messages([
        ("user",
         "你是一位科学传播专家，擅长将复杂的学术论文摘要转化为简洁通俗的语言。\n\n"
         "请精炼以下论文摘要，要求：\n"
         "1. **更加精炼**：大幅压缩内容，去除所有冗余和重复信息，只保留最核心的内容\n"
         "2. **简洁明了**：用最少的文字表达清楚，避免啰嗦和冗长的描述\n"
         "3. **通俗易懂**：使用日常语言，避免专业术语（如果必须使用，请简单解释）\n"
         "4. **核心要点**：明确说明这篇论文研究了什么问题、用了什么方法、得到了什么结果（用最简洁的方式）\n\n"
         "论文标题: {title}\n\n"
         "原始摘要:\n{abstract}\n\n"
         "请直接返回精炼后的摘要，不要包含任何其他文字或格式标记。"
         "精炼后的摘要应该：\n"
         "- 用中文表达（如果原始摘要是英文，请翻译并精炼）\n"
         "- 比原文明显更短（通常压缩到原文的50%以下）\n"
         "- 去除所有冗余、重复、啰嗦的内容\n"
         "- 只保留最核心的信息\n"
         "- 让非专业读者也能快速理解论文的核心内容")
    ])
    
    try:
        chain = prompt_template | refine_llm
        response = chain.invoke({
            "title": title_escaped,
            "abstract": abstract_escaped
        })
        
        refined_abstract = response.content.strip()
        
        # 清理可能的格式标记
        refined_abstract = refined_abstract.replace('```', '').strip()
        
        # 如果结果为空，返回原摘要
        if not refined_abstract:
            logger.warning(f"精炼结果为空，使用原摘要: {arxiv_id}")
            refined_abstract = abstract
        
        # 存入缓存
        _refine_cache[cache_key] = refined_abstract
        logger.info(f"精炼摘要成功: {arxiv_id}")
        
        return refined_abstract
        
    except Exception as e:
        logger.error(f"精炼摘要失败: {str(e)}")
        # 如果精炼失败，返回原摘要
        return abstract

