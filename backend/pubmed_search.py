"""
PubMed 论文检索模块
使用 LangChain PubMedRetriever 搜索生物医学论文
"""

import os
import logging
from typing import List, Dict, Optional
from langchain_community.retrievers import PubMedRetriever
from dotenv import load_dotenv
from config import MAX_SEARCH_RESULTS_PER_ENGINE

# 配置日志
logger = logging.getLogger(__name__)

# 加载环境变量（优先从项目根目录加载）
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()


class PubMedAPI:
    """PubMed API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, email: str = "pubmed@example.com"):
        """
        初始化 PubMed API 客户端
        
        Args:
            api_key: NCBI API 密钥（可选，通过环境变量设置）
            email: 联系邮箱（NCBI 要求）
        """
        self.api_key = api_key or os.getenv('NCBI_API_KEY')
        self.email = email
        
        # 设置环境变量（如果提供了 API key）
        if self.api_key:
            os.environ['NCBI_API_KEY'] = self.api_key
    
    def search_papers(
        self,
        query: str,
        limit: int = None
    ) -> List[Dict]:
        """
        搜索 PubMed 论文
        
        Args:
            query: 搜索查询字符串
            limit: 返回结果数量限制（如果为 None，使用默认值 MAX_SEARCH_RESULTS_PER_ENGINE）
            
        Returns:
            论文列表
        """
        # 确定返回数量限制
        if limit is None:
            limit = MAX_SEARCH_RESULTS_PER_ENGINE
        
        try:
            # 创建 PubMedRetriever
            retriever = PubMedRetriever(
                top_k_results=limit,
                email=self.email
            )
            
            # 执行搜索
            logger.info(f"PubMed 搜索查询: {query}, limit: {limit}")
            documents = retriever.invoke(query)
            logger.info(f"PubMed API 返回 {len(documents)} 篇原始论文")
            
            return documents
            
        except Exception as e:
            logger.error(f"PubMed API 搜索失败: {str(e)}")
            raise Exception(f"PubMed 搜索失败: {str(e)}")


def search_papers(keywords: str, limit: int = None) -> List[Dict]:
    """
    搜索 PubMed 论文并格式化返回
    
    Args:
        keywords: 搜索关键词
        limit: 返回的最大数量（如果为 None，使用默认值 MAX_SEARCH_RESULTS_PER_ENGINE）
        
    Returns:
        论文列表，每个论文包含标准化的字段
    """
    try:
        logger.info(f"开始调用 PubMed API，关键词: {keywords}, limit: {limit}")
        api = PubMedAPI()
        raw_documents = api.search_papers(keywords, limit=limit)
        logger.info(f"PubMed API 返回 {len(raw_documents)} 篇原始论文")
        
        # 格式化论文数据，统一字段格式
        papers = []
        for doc in raw_documents:
            metadata = doc.metadata
            page_content = doc.page_content
            
            # 提取基本信息
            title = metadata.get('Title', '')
            uid = metadata.get('uid', '')
            published = metadata.get('Published', '')
            abstract = page_content.strip() if page_content else ''
            
            # PubMed URL 格式: https://pubmed.ncbi.nlm.nih.gov/{uid}/
            url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/" if uid else ''
            
            # PubMed 通常不提供 PDF 直接下载链接，但可以通过 DOI 或其他方式获取
            # 这里先设置为 None，后续可以通过其他 API 获取
            pdf_url = None
            
            # PubMed 的 metadata 中通常不包含作者信息（需要额外查询）
            # 这里先设置为空列表
            authors = []
            
            # 格式化论文信息
            paper_info = {
                "title": title,
                "abstract": abstract or '',  # 如果没有摘要，使用空字符串
                "paper_id": uid,  # PubMed 使用 uid
                "arxiv_id": uid,  # 为了兼容，也设置 arxiv_id
                "url": url,  # 网页链接
                "pdf_url": pdf_url,  # PDF 下载链接（通常为 None）
                "authors": authors,  # 作者列表（需要额外查询）
                "published": published if published and published != '--' else None,
                "source": "pubmed"  # 标记来源
            }
            papers.append(paper_info)
        
        logger.info(f"PubMed 格式化完成，返回 {len(papers)} 篇论文")
        return papers
        
    except Exception as e:
        logger.error(f"PubMed 搜索失败: {str(e)}")
        raise Exception(f"PubMed 搜索失败: {str(e)}")

