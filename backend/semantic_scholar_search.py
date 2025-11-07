"""
Semantic Scholar 论文检索模块
使用 Semantic Scholar API 搜索论文
"""

import requests
import time
import logging
from typing import List, Dict, Optional
from config import MAX_SEARCH_RESULTS_PER_ENGINE

# 配置日志
logger = logging.getLogger(__name__)


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
        limit: int = None,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        fields_of_study: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        搜索论文（使用 GET /paper/search）
        
        Args:
            query: 搜索查询字符串
            limit: 返回结果数量限制（如果为 None，使用默认值 MAX_SEARCH_RESULTS_PER_ENGINE）
            fields: 要返回的字段列表
            year: 年份过滤（格式：YYYY 或 YYYY-YYYY）
            fields_of_study: 研究领域过滤（如 ["Computer Science"]）
            
        Returns:
            论文列表
        """
        # 确定返回数量限制
        if limit is None:
            limit = MAX_SEARCH_RESULTS_PER_ENGINE
        
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
        
        # 重试配置
        max_retries = 3
        retry_delay = 10  # 初始延迟10秒
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
                
                # 处理速率限制（429）
                if response.status_code == 429:
                    # 检查响应头中的 Retry-After
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except ValueError:
                            wait_time = retry_delay * (attempt + 1)
                    else:
                        wait_time = retry_delay * (attempt + 1)
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"遇到速率限制 (429)，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(
                            f"Semantic Scholar API 速率限制：已达到最大重试次数。"
                            f"建议：1) 等待一段时间后重试 2) 申请 API 密钥以获得更高的速率限制"
                        )
                
                # 检查其他错误状态
                response.raise_for_status()
                
                # 成功获取数据
                data = response.json()
                return data.get("data", [])
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    # HTTPError 也可能包含 429，继续重试
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except ValueError:
                            wait_time = retry_delay * (attempt + 1)
                    else:
                        wait_time = retry_delay * (attempt + 1)
                    
                    logger.warning(f"遇到速率限制 (429)，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Semantic Scholar API 错误 ({e.response.status_code}): {str(e)}")
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"请求失败，等待 {retry_delay} 秒后重试 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Semantic Scholar 搜索失败: {str(e)}")
        
        # 如果所有重试都失败
        raise Exception("Semantic Scholar 搜索失败：已达到最大重试次数")


def search_papers(keywords: str, limit: int = None) -> List[Dict]:
    """
    搜索 Semantic Scholar 论文并格式化返回
    
    Args:
        keywords: 搜索关键词
        limit: 返回的最大数量（如果为 None，使用默认值 MAX_SEARCH_RESULTS_PER_ENGINE）
        
    Returns:
        论文列表，每个论文包含标准化的字段
    """
    try:
        logger.info(f"开始调用 Semantic Scholar API，关键词: {keywords}, limit: {limit}")
        api = SemanticScholarAPI()
        raw_papers = api.search_papers(keywords, limit=limit)
        logger.info(f"Semantic Scholar API 返回 {len(raw_papers)} 篇原始论文")
        
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

