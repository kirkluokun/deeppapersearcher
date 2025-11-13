"""
arXiv 论文检索模块
使用 arxiv Python 库搜索论文，支持所有主要学科分类
"""

import arxiv
from typing import List, Dict, Optional
from config import ARXIV_CATEGORY, MAX_SEARCH_RESULTS_PER_ENGINE, is_valid_arxiv_category


def build_arxiv_query(keywords: str, category: str = None) -> str:
    """
    构建 arXiv 查询字符串
    
    Args:
        keywords: 搜索关键词
        category: 分类代码（如 "cs", "physics", "math"），如果为 None 则使用默认分类
        
    Returns:
        arXiv 查询字符串
    """
    # 如果没有指定分类，使用默认分类（向后兼容）
    if category is None:
        category = ARXIV_CATEGORY
    
    # 验证分类是否有效
    if not is_valid_arxiv_category(category):
        raise ValueError(f"无效的 arXiv 分类: {category}")
    
    # 构建查询，限制在指定分类
    # 注意：arXiv API 不支持 AND 关键字，使用空格分隔即可
    # 使用 all: 前缀在所有字段（标题、摘要等）中搜索
    query = f"cat:{category} all:{keywords}"
    return query


def search_papers(keywords: str, limit: int = None, category: str = None) -> List[Dict]:
    """
    搜索 arXiv 论文
    
    Args:
        keywords: 搜索关键词
        limit: 返回的最大数量（如果为 None，使用默认值 MAX_SEARCH_RESULTS_PER_ENGINE）
        category: 分类代码（如 "cs", "physics", "math"），可选，默认为 "cs"（向后兼容）
        
    Returns:
        论文列表，每个论文包含 title, abstract, arxiv_id, url 等信息
        
    Raises:
        ValueError: 如果分类代码无效
        Exception: 如果搜索失败
    """
    try:
        # 确定返回数量限制
        max_results = limit if limit is not None else MAX_SEARCH_RESULTS_PER_ENGINE
        
        # 构建查询字符串
        query = build_arxiv_query(keywords, category)
        
        # 创建自定义 Client，使用 HTTPS URL 避免 301 重定向错误
        # 修复：将 query_url_format 改为 HTTPS
        client = arxiv.Client(
            page_size=100,
            delay_seconds=3.0,
            num_retries=3
        )
        # 修改 Client 的 query_url_format 为 HTTPS
        client.query_url_format = 'https://export.arxiv.org/api/query?{}'
        
        # 创建搜索对象
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        # 使用自定义 Client 执行搜索
        for result in client.results(search):
            arxiv_id = result.entry_id.split("/")[-1]  # 提取 arXiv ID
            # arXiv PDF URL 格式: https://arxiv.org/pdf/{arxiv_id}.pdf
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            paper_info = {
                "title": result.title,
                "abstract": result.summary,
                "arxiv_id": arxiv_id,
                "url": result.entry_id,  # arXiv 网页 URL
                "pdf_url": pdf_url,  # arXiv PDF 下载链接
                "authors": [author.name for author in result.authors],
                "published": result.published.strftime("%Y-%m-%d") if result.published else None,
                "source": "arxiv"  # 标记来源
            }
            papers.append(paper_info)
        
        return papers
        
    except ValueError:
        # 重新抛出 ValueError（分类验证错误）
        raise
    except Exception as e:
        raise Exception(f"arXiv 搜索失败: {str(e)}")
