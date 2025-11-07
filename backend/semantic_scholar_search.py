"""
Semantic Scholar 论文检索模块
使用 Semantic Scholar API 搜索论文
"""

import requests
import time
from typing import List, Dict, Optional
from config import MAX_SEARCH_RESULTS


class SemanticScholarAPI:
    """Semantic Scholar API 客户端"""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 API 客户端
        
        Args:
            api_key: API 密钥（可选，有密钥可以提高速率限制）
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["x-api-key"] = api_key
    
    def search_papers(
        self,
        query: str,
        limit: int = MAX_SEARCH_RESULTS,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        fields_of_study: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        搜索论文（使用 GET /paper/search）
        
        Args:
            query: 搜索查询字符串
            limit: 返回结果数量限制
            fields: 要返回的字段列表
            year: 年份过滤（格式：YYYY 或 YYYY-YYYY）
            fields_of_study: 研究领域过滤（如 ["Computer Science"]）
            
        Returns:
            论文列表
        """
        # 默认字段
        if fields is None:
            fields = [
                "paperId",
                "title",
                "abstract",
                "year",
                "authors",
                "citationCount",
                "referenceCount",
                "url",
                "venue",
                "fieldsOfStudy",
                "openAccessPdf"  # PDF 下载地址
            ]
        
        # 构建查询参数（GET 请求使用 params）
        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields)
        }
        
        if year:
            params["year"] = year
        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)
        
        # 使用 GET /paper/search 端点
        url = f"{self.BASE_URL}/paper/search"
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            # 处理速率限制
            if response.status_code == 429:
                time.sleep(5)
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
            
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Semantic Scholar 搜索失败: {str(e)}")


def search_papers(keywords: str) -> List[Dict]:
    """
    搜索 Semantic Scholar 论文并格式化返回
    
    Args:
        keywords: 搜索关键词
        
    Returns:
        论文列表，每个论文包含标准化的字段
    """
    try:
        api = SemanticScholarAPI()
        raw_papers = api.search_papers(keywords, limit=MAX_SEARCH_RESULTS)
        
        # 格式化论文数据，统一字段格式
        papers = []
        for paper in raw_papers:
            # 提取作者名称列表
            authors = []
            if paper.get('authors'):
                authors = [author.get('name', '') for author in paper['authors'] if author.get('name')]
            
            # 提取 URL（网页链接）
            web_url = paper.get('url', '')
            
            # 提取 PDF URL
            pdf_url = ''
            pdf_info = paper.get('openAccessPdf', {})
            if pdf_info and pdf_info.get('url'):
                pdf_url = pdf_info['url'].strip()
            
            # 格式化论文信息
            paper_info = {
                "title": paper.get('title', ''),
                "abstract": paper.get('abstract') or '',  # 如果没有摘要，使用空字符串
                "paper_id": paper.get('paperId', ''),  # Semantic Scholar 使用 paperId
                "arxiv_id": paper.get('paperId', ''),  # 为了兼容，也设置 arxiv_id
                "url": web_url,  # 网页链接
                "pdf_url": pdf_url,  # PDF 下载链接
                "authors": authors,
                "published": str(paper.get('year', '')) if paper.get('year') else None,
                "venue": paper.get('venue', ''),
                "citation_count": paper.get('citationCount', 0),
                "reference_count": paper.get('referenceCount', 0),
                "fields_of_study": paper.get('fieldsOfStudy', []),
                "source": "semantic_scholar"  # 标记来源
            }
            papers.append(paper_info)
        
        return papers
        
    except Exception as e:
        raise Exception(f"Semantic Scholar 搜索失败: {str(e)}")

