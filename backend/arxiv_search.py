"""
arXiv 论文检索模块
使用 arxiv Python 库搜索论文，限制在 cs 分类
"""

import arxiv
from typing import List, Dict
from config import ARXIV_CATEGORY, MAX_SEARCH_RESULTS


def search_papers(keywords: str) -> List[Dict]:
    """
    搜索 arXiv 论文
    
    Args:
        keywords: 搜索关键词
        
    Returns:
        论文列表，每个论文包含 title, abstract, arxiv_id, url 等信息
    """
    try:
        # 构建查询，限制在 cs 分类
        # 注意：arXiv API 不支持 AND 关键字，使用空格分隔即可
        # 使用 all: 前缀在所有字段（标题、摘要等）中搜索
        query = f"cat:{ARXIV_CATEGORY} all:{keywords}"
        
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
            max_results=MAX_SEARCH_RESULTS,
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
        
    except Exception as e:
        raise Exception(f"arXiv 搜索失败: {str(e)}")
