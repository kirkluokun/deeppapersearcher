"""
LLM 筛选模块
使用 Gemini 2.0 Flash 根据用户问题筛选相关论文
"""

import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from config import GEMINI_MODEL, GEMINI_TEMPERATURE, MAX_FILTERED_RESULTS

# 加载环境变量（优先从项目根目录加载）
# 获取当前文件的目录，然后找到项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # backend 的父目录
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 如果根目录没有，尝试从 backend 目录加载
    load_dotenv()

# 初始化 LLM
# 注意：Gemini 不支持 SystemMessage，需要转换为 HumanMessage
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=GEMINI_TEMPERATURE,
    convert_system_message_to_human=True
)


def filter_papers(keywords: str, question: str, papers: List[Dict]) -> List[Dict]:
    """
    使用 LLM 根据用户问题筛选相关论文
    
    Args:
        keywords: 搜索关键词
        question: 用户想了解的问题
        papers: 论文列表
        
    Returns:
        筛选后的论文列表
    """
    if not papers:
        return []
    
    # 构建论文列表文本
    # 注意：需要转义花括号，避免与模板变量冲突
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        # 转义标题和摘要中的花括号
        title = paper.get('title', '').replace('{', '{{').replace('}', '}}')
        abstract = (paper.get('abstract') or '')[:500].replace('{', '{{').replace('}', '}}')
        # 统一获取论文 ID（arxiv_id 或 paper_id）
        paper_id = paper.get('arxiv_id') or paper.get('paper_id', '')
        source = paper.get('source', 'unknown')
        papers_text += f"\n[{i}] 论文 ID: {paper_id} (来源: {source})\n"
        papers_text += f"标题: {title}\n"
        papers_text += f"摘要: {abstract}...\n"
    
    # 使用模板变量而不是 f-string，避免格式化错误
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
         "你是一位学术研究助手。你的任务是根据用户的问题，从给定的论文列表中筛选出最相关的论文。\n"
         "请仔细阅读每篇论文的标题和摘要，判断它们是否与用户的问题相关。\n"
         "只返回最相关的论文的 ID（每行一个 ID），最多返回 {max_results} 篇，按相关度从高到低排序。\n"
         "返回格式：每行一个论文 ID（与论文列表中显示的 ID 完全一致）。\n"
         "不要包含任何其他文字或解释。\n"
         "如果所有论文都不相关，返回空行。"),
        ("user",
         "搜索关键词: {keywords}\n\n"
         "用户问题: {question}\n\n"
         "论文列表:\n{papers_text}\n\n"
         "请根据用户问题，返回最相关的论文的 ID（每行一个，最多 {max_results} 篇）:")
    ])
    
    try:
        # 调用 LLM
        chain = prompt_template | llm
        response = chain.invoke({
            "keywords": keywords,
            "question": question,
            "papers_text": papers_text,
            "max_results": MAX_FILTERED_RESULTS
        })
        
        # 解析返回的论文 ID
        selected_ids = []
        response_text = response.content.strip()
        
        for line in response_text.split("\n"):
            line = line.strip()
            # 提取论文 ID（可能是纯 ID 或包含 URL）
            if line:
                # 如果包含 URL，提取 ID
                if "arxiv.org" in line or "semanticscholar.org" in line:
                    paper_id = line.split("/")[-1].strip()
                else:
                    paper_id = line.strip()
                
                # 验证 ID 格式（arXiv 通常是 YYMM.NNNNN，Semantic Scholar 是哈希值）
                if paper_id and len(paper_id) > 5:
                    selected_ids.append(paper_id)
        
        # 根据筛选出的 ID 返回论文
        filtered_papers = []
        selected_ids_set = set(selected_ids)
        
        for paper in papers:
            # 统一获取论文 ID（arxiv_id 或 paper_id）
            paper_id = paper.get('arxiv_id') or paper.get('paper_id', '')
            if paper_id in selected_ids_set:
                filtered_papers.append(paper)
        
        # 限制最多返回 MAX_FILTERED_RESULTS 篇
        filtered_papers = filtered_papers[:MAX_FILTERED_RESULTS]
        
        # 如果 LLM 没有返回有效 ID，返回前 MAX_FILTERED_RESULTS 篇论文（按相关度）
        if not filtered_papers and papers:
            print(f"警告: LLM 未返回有效的论文 ID，返回前 {MAX_FILTERED_RESULTS} 篇论文")
            return papers[:MAX_FILTERED_RESULTS]
        
        return filtered_papers
        
    except Exception as e:
        print(f"LLM 筛选失败: {str(e)}")
        # 如果 LLM 调用失败，返回前 MAX_FILTERED_RESULTS 篇论文（按相关度）
        return papers[:MAX_FILTERED_RESULTS]
