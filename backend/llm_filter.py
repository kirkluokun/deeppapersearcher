"""
LLM 筛选模块
使用 Gemini 2.0 Flash 根据用户问题筛选相关论文
"""

import os
import logging
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from config import GEMINI_MODEL, GEMINI_TEMPERATURE, MAX_FILTERED_RESULTS

# 配置日志
logger = logging.getLogger(__name__)

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
    
    # 统计各引擎的论文数量
    arxiv_count = sum(1 for p in papers if p.get('source') == 'arxiv')
    ss_count = sum(1 for p in papers if p.get('source') == 'semantic_scholar')
    pubmed_count = sum(1 for p in papers if p.get('source') == 'pubmed')
    logger.info(f"LLM 筛选开始，输入论文总数: {len(papers)} (arXiv: {arxiv_count}, Semantic Scholar: {ss_count}, PubMed: {pubmed_count})")
    
    # 构建论文列表文本
    # 注意：需要转义花括号，避免与模板变量冲突
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        # 转义标题和摘要中的花括号
        # 确保 title 和 abstract 是字符串类型
        title = paper.get('title', '')
        if not isinstance(title, str):
            title = str(title) if title else ''
        title = title.replace('{', '{{').replace('}', '}}')
        
        abstract = paper.get('abstract') or ''
        if not isinstance(abstract, str):
            abstract = str(abstract) if abstract else ''
        abstract = abstract[:500].replace('{', '{{').replace('}', '}}')
        
        # 统一获取论文 ID（arxiv_id 或 paper_id）
        paper_id = paper.get('arxiv_id') or paper.get('paper_id', '')
        source = paper.get('source', 'unknown')
        papers_text += f"\n[{i}] 论文 ID: {paper_id} (来源: {source})\n"
        papers_text += f"标题: {title}\n"
        papers_text += f"摘要: {abstract}...\n"
    
    # 使用模板变量而不是 f-string，避免格式化错误
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
         "你是一位学术研究助手。你的任务是根据用户的问题，判断论文列表中哪些论文与问题相关。\n"
         "请仔细阅读每篇论文的标题和摘要，判断它们是否与用户的问题相关。\n"
         "重要提示：论文列表包含来自不同来源的论文（arXiv、Semantic Scholar 和 PubMed），它们的 ID 格式不同：\n"
         "- arXiv 论文的 ID 格式类似：2507.01376v1、2403.15137v1 等\n"
         "- Semantic Scholar 论文的 ID 是长哈希值，类似：53c9f3c34d8481adaf24df3b25581ccf1bc53f5c\n"
         "- PubMed 论文的 ID 是纯数字，类似：41200362、41199284 等\n"
         "请确保返回所有相关论文的 ID，无论它们来自哪个来源。\n"
         "只返回相关论文的 ID（每行一个 ID），最多返回 {max_results} 篇。\n"
         "返回格式：每行一个论文 ID（与论文列表中显示的 ID 完全一致，包括格式）。\n"
         "不要包含任何其他文字或解释。\n"
         "如果所有论文都不相关，返回空行。"),
        ("user",
         "搜索关键词: {keywords}\n\n"
         "用户问题: {question}\n\n"
         "论文列表:\n{papers_text}\n\n"
         "请根据用户问题，返回所有相关论文的 ID（每行一个，最多 {max_results} 篇，包括来自不同来源的论文）:")
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
        logger.info(f"LLM 返回的原始响应（前500字符）: {response_text[:500]}")
        
        for line in response_text.split("\n"):
            line = line.strip()
            # 提取论文 ID（可能是纯 ID 或包含 URL）
            if line:
                # 如果包含 URL，提取 ID
                if "arxiv.org" in line or "semanticscholar.org" in line:
                    paper_id = line.split("/")[-1].strip()
                else:
                    paper_id = line.strip()
                
                # 验证 ID 格式
                # arXiv ID 格式：YYMM.NNNNNvN 或类似格式（通常包含点号和v）
                # Semantic Scholar ID：长哈希值（通常是40个字符的十六进制字符串）
                # PubMed ID：纯数字（通常是8位数字）
                if paper_id:
                    # 放宽验证条件，接受任何长度大于4的ID
                    # arXiv ID 通常类似：2507.01376v1（约12-15字符）
                    # Semantic Scholar ID 通常是40字符的哈希值
                    # PubMed ID 通常是8位数字（如 41200362）
                    if len(paper_id) >= 4:  # PubMed ID 可能是8位数字，降低最小长度要求
                        selected_ids.append(paper_id)
                    else:
                        logger.debug(f"跳过过短的 ID: {paper_id}")
        
        logger.info(f"LLM 返回的有效 ID 数量: {len(selected_ids)}")
        if len(selected_ids) > 0:
            logger.info(f"LLM 返回的前5个 ID: {selected_ids[:5]}")
        
        # 根据筛选出的 ID 返回论文（保持原始搜索结果的顺序）
        selected_ids_set = set(selected_ids)
        filtered_papers = []
        
        # 创建 ID 到论文的映射，用于调试
        paper_id_map = {}
        for paper in papers:
            paper_id = paper.get('arxiv_id') or paper.get('paper_id', '')
            paper_id_map[paper_id] = paper
        
        matched_ids = []
        for paper in papers:
            paper_id = paper.get('arxiv_id') or paper.get('paper_id', '')
            if paper_id in selected_ids_set:
                filtered_papers.append(paper)
                matched_ids.append(paper_id)
                # 达到上限后停止
                if len(filtered_papers) >= MAX_FILTERED_RESULTS:
                    break
        
        matched_arxiv_count = sum(1 for pid in matched_ids if pid in paper_id_map and paper_id_map[pid].get('source') == 'arxiv')
        matched_ss_count = sum(1 for pid in matched_ids if pid in paper_id_map and paper_id_map[pid].get('source') == 'semantic_scholar')
        matched_pubmed_count = sum(1 for pid in matched_ids if pid in paper_id_map and paper_id_map[pid].get('source') == 'pubmed')
        logger.info(f"成功匹配的论文数量: {len(filtered_papers)} (arXiv: {matched_arxiv_count}, Semantic Scholar: {matched_ss_count}, PubMed: {matched_pubmed_count})")
        
        # 如果筛选后只有一个来源的论文，尝试平衡两个来源
        # 检查输入中是否有多个来源
        input_sources = set(p.get('source', 'unknown') for p in papers)
        if len(input_sources) > 1 and len(filtered_papers) > 0:
            filtered_sources = set(p.get('source', 'unknown') for p in filtered_papers)
            if len(filtered_sources) == 1:
                logger.warning(f"警告: LLM 只返回了单一来源的论文 ({filtered_sources})，尝试添加其他来源的论文...")
                # 找到缺失的来源
                missing_source = (input_sources - filtered_sources).pop() if (input_sources - filtered_sources) else None
                if missing_source:
                    # 从未被选中的论文中，选择缺失来源的论文
                    selected_ids_set = set(selected_ids)
                    missing_papers = [
                        p for p in papers 
                        if p.get('source') == missing_source 
                        and (p.get('arxiv_id') or p.get('paper_id', '')) not in selected_ids_set
                    ]
                    # 添加一些缺失来源的论文（最多添加5篇，或达到MAX_FILTERED_RESULTS的一半）
                    max_add = min(5, MAX_FILTERED_RESULTS // 2, len(missing_papers))
                    if max_add > 0:
                        for paper in missing_papers[:max_add]:
                            if len(filtered_papers) < MAX_FILTERED_RESULTS:
                                filtered_papers.append(paper)
                                logger.info(f"添加 {missing_source} 论文以平衡来源: {paper.get('arxiv_id') or paper.get('paper_id', '')}")
                        logger.info(f"平衡后论文数量: {len(filtered_papers)} (arXiv: {sum(1 for p in filtered_papers if p.get('source') == 'arxiv')}, Semantic Scholar: {sum(1 for p in filtered_papers if p.get('source') == 'semantic_scholar')})")
        
        if len(selected_ids) > 0 and len(filtered_papers) == 0:
            logger.warning(f"警告: LLM 返回了 {len(selected_ids)} 个 ID，但无法匹配到任何论文")
            logger.warning(f"LLM 返回的所有 ID: {selected_ids[:10]}")
            logger.warning(f"前10个论文的实际 ID 和来源: {[(p.get('arxiv_id') or p.get('paper_id', ''), p.get('source', 'unknown')) for p in papers[:10]]}")
            
            # 尝试更宽松的匹配：检查ID是否包含在论文ID中（用于处理可能的格式差异）
            logger.info("尝试更宽松的ID匹配...")
            for paper in papers:
                paper_id = paper.get('arxiv_id') or paper.get('paper_id', '')
                for selected_id in selected_ids:
                    if selected_id in paper_id or paper_id in selected_id:
                        if paper not in filtered_papers:
                            filtered_papers.append(paper)
                            logger.info(f"通过宽松匹配找到论文: {paper_id} (来源: {paper.get('source', 'unknown')})")
                        if len(filtered_papers) >= MAX_FILTERED_RESULTS:
                            break
                if len(filtered_papers) >= MAX_FILTERED_RESULTS:
                    break
        
        # 如果 LLM 没有返回有效 ID，返回前 MAX_FILTERED_RESULTS 篇论文（保持原始顺序）
        if not filtered_papers and papers:
            logger.warning(f"警告: LLM 未返回有效的论文 ID，返回前 {MAX_FILTERED_RESULTS} 篇论文")
            return papers[:MAX_FILTERED_RESULTS]
        
        return filtered_papers
        
    except Exception as e:
        logger.error(f"LLM 筛选失败: {str(e)}", exc_info=True)
        # 如果 LLM 调用失败，返回前 MAX_FILTERED_RESULTS 篇论文（保持原始顺序）
        return papers[:MAX_FILTERED_RESULTS]
