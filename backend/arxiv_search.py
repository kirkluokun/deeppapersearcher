"""
arXiv 论文检索模块
使用 arxiv Python 库搜索论文，支持所有主要学科分类
支持 OAI-PMH 协议进行批量数据访问（可选）
"""

import arxiv
from typing import List, Dict, Optional
from config import (
    ARXIV_CATEGORY, 
    MAX_SEARCH_RESULTS_PER_ENGINE, 
    is_valid_arxiv_category,
    OAI_PMH_BASE_URL,
    OAI_PMH_METADATA_PREFIX,
    ARXIV_SEARCH_MODE,
    map_category_to_oai_set
)
import logging

logger = logging.getLogger(__name__)


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


def search_papers_oai_pmh(
    keywords: str, 
    limit: int = None, 
    category: str = None
) -> List[Dict]:
    """
    使用 OAI-PMH 协议搜索 arXiv 论文
    
    Args:
        keywords: 搜索关键词（将在本地进行过滤）
        limit: 返回的最大数量（如果为 None，使用默认值 MAX_SEARCH_RESULTS_PER_ENGINE）
        category: 分类代码（如 "cs", "physics", "math"），可选，默认为 "cs"
        
    Returns:
        论文列表，每个论文包含 title, abstract, arxiv_id, url 等信息
        
    Raises:
        ValueError: 如果分类代码无效
        Exception: 如果搜索失败
    """
    try:
        from sickle import Sickle
        
        # 确定返回数量限制
        max_results = limit if limit is not None else MAX_SEARCH_RESULTS_PER_ENGINE
        
        # 如果没有指定分类，使用默认分类（向后兼容）
        if category is None:
            category = ARXIV_CATEGORY
        
        # 验证分类是否有效
        if not is_valid_arxiv_category(category):
            raise ValueError(f"无效的 arXiv 分类: {category}")
        
        # 映射分类到 OAI-PMH Set
        oai_set = map_category_to_oai_set(category)
        logger.info(f"使用 OAI-PMH 搜索，Set: {oai_set}, 关键词: {keywords}")
        
        # 创建 OAI-PMH 客户端
        sickle = Sickle(OAI_PMH_BASE_URL)
        
        # 获取记录（使用 resumptionToken 自动分页）
        records = sickle.ListRecords(
            metadataPrefix=OAI_PMH_METADATA_PREFIX,
            set=oai_set
        )
        
        papers = []
        keywords_lower = keywords.lower().split()  # 将关键词转换为小写并分割
        
        # 遍历记录，进行关键词过滤
        for record in records:
            # 如果已经获取足够的结果，停止
            if len(papers) >= max_results:
                break
            
            try:
                metadata = record.metadata
                
                # 提取元数据字段
                arxiv_id_raw = metadata.get('id', [''])[0] if isinstance(metadata.get('id'), list) else str(metadata.get('id', ''))
                title = metadata.get('title', [''])[0] if isinstance(metadata.get('title'), list) else str(metadata.get('title', ''))
                abstract = metadata.get('abstract', [''])[0] if isinstance(metadata.get('abstract'), list) else str(metadata.get('abstract', ''))
                
                # 提取作者信息
                authors = []
                # 尝试从 authors 字段提取
                authors_data = metadata.get('authors', [])
                if authors_data:
                    if isinstance(authors_data, list):
                        for author in authors_data:
                            if isinstance(author, dict):
                                # 格式可能是 {'keyname': '...', 'forenames': '...'}
                                keyname = author.get('keyname', '')
                                forenames = author.get('forenames', '')
                                if keyname or forenames:
                                    authors.append(f"{forenames} {keyname}".strip())
                            elif isinstance(author, str):
                                authors.append(author)
                
                # 如果 authors 字段为空，尝试从 keyname 和 forenames 字段提取
                if not authors:
                    keynames = metadata.get('keyname', [])
                    forenames_list = metadata.get('forenames', [])
                    if isinstance(keynames, list) and isinstance(forenames_list, list):
                        for i in range(min(len(keynames), len(forenames_list))):
                            author_name = f"{forenames_list[i]} {keynames[i]}".strip()
                            if author_name:
                                authors.append(author_name)
                
                # 提取日期信息
                created = metadata.get('created', [''])[0] if isinstance(metadata.get('created'), list) else str(metadata.get('created', ''))
                
                # 提取分类信息
                categories_raw = metadata.get('categories', [''])[0] if isinstance(metadata.get('categories'), list) else str(metadata.get('categories', ''))
                categories = categories_raw.split() if categories_raw else []
                
                # 关键词过滤：检查标题或摘要中是否包含关键词
                title_lower = title.lower()
                abstract_lower = abstract.lower()
                
                # 检查是否所有关键词都在标题或摘要中
                matches = all(
                    keyword in title_lower or keyword in abstract_lower
                    for keyword in keywords_lower
                )
                
                if not matches:
                    continue
                
                # 格式化 arXiv ID（去除版本号，如果有）
                arxiv_id = arxiv_id_raw.split('/')[-1] if '/' in arxiv_id_raw else arxiv_id_raw
                arxiv_id = arxiv_id.split('v')[0]  # 去除版本号
                
                # 构建 URL
                url = f"https://arxiv.org/abs/{arxiv_id}"
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                paper_info = {
                    "title": title,
                    "abstract": abstract,
                    "arxiv_id": arxiv_id,
                    "url": url,
                    "pdf_url": pdf_url,
                    "authors": authors,
                    "published": created[:10] if created else None,  # 只取日期部分
                    "source": "arxiv"  # 标记来源
                }
                papers.append(paper_info)
                
            except Exception as e:
                # 跳过无法解析的记录，继续处理下一条
                logger.warning(f"跳过无法解析的记录: {str(e)}")
                continue
        
        logger.info(f"OAI-PMH 搜索完成，找到 {len(papers)} 篇论文")
        return papers
        
    except ImportError:
        raise Exception("sickle 库未安装，请运行: pip install sickle")
    except ValueError:
        # 重新抛出 ValueError（分类验证错误）
        raise
    except Exception as e:
        raise Exception(f"OAI-PMH 搜索失败: {str(e)}")


def search_papers(keywords: str, limit: int = None, category: str = None) -> List[Dict]:
    """
    搜索 arXiv 论文
    根据配置选择使用 OAI-PMH 协议或传统 API
    
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
    # 根据配置选择搜索模式
    if ARXIV_SEARCH_MODE == "oai-pmh":
        return search_papers_oai_pmh(keywords, limit, category)
    else:
        # 使用传统 API（默认）
        return search_papers_traditional(keywords, limit, category)


def search_papers_traditional(keywords: str, limit: int = None, category: str = None) -> List[Dict]:
    """
    使用传统 arxiv API 搜索论文（原有实现）
    
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
