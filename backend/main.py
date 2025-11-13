"""
FastAPI 主服务
提供论文搜索和筛选的 API 接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from arxiv_search import search_papers as search_arxiv_papers, get_latest_papers_oai_pmh
from semantic_scholar_search import search_papers as search_semantic_scholar_papers
from pubmed_search import search_papers as search_pubmed_papers
from llm_filter import filter_papers
from translate_extract import translate_and_extract_keywords, refine_abstract
from config import MAX_SEARCH_RESULTS_PER_ENGINE, is_valid_arxiv_category, ARXIV_CATEGORIES
from history_storage import save_history, list_history
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="arXiv 论文检索系统")

# 配置 CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求模型
class SearchRequest(BaseModel):
    keywords: str
    question: str
    engines: List[str] = ["arxiv"]  # 默认只使用 arxiv，可选: ["arxiv", "semantic_scholar", "pubmed"]
    arxiv_category: str | None = None  # arXiv 分类（可选），如 "cs", "physics", "math" 等，默认为 None（使用默认分类 "cs"）


# 响应模型
class PaperResponse(BaseModel):
    title: str
    title_zh: Optional[str] = None  # 中文标题（可选）
    abstract: str
    abstract_zh: str  # 中文摘要
    keywords: str  # 关键词（中文）
    relevance_summary: str  # 相关性评估概述
    arxiv_id: str  # 论文 ID（arxiv_id 或 paper_id）
    url: str  # 网页链接
    pdf_url: str | None = None  # PDF 下载链接（可选）
    authors: List[str]
    published: str | None
    source: str  # 来源：arxiv、semantic_scholar 或 pubmed


class SearchResponse(BaseModel):
    papers: List[PaperResponse]
    total: int


@app.get("/")
async def root():
    """根路径"""
    return {"message": "arXiv 论文检索系统 API"}


def process_search(request: SearchRequest) -> SearchResponse:
    """处理搜索请求"""
    try:
        # 验证引擎选择
        valid_engines = ["arxiv", "semantic_scholar", "pubmed"]
        engines = [e for e in request.engines if e in valid_engines]
        if not engines:
            engines = ["arxiv"]  # 默认使用 arxiv
        
        # 验证 arXiv 分类（如果提供了分类参数）
        arxiv_category = request.arxiv_category
        if arxiv_category is not None:
            if not is_valid_arxiv_category(arxiv_category):
                valid_categories = ', '.join(sorted(ARXIV_CATEGORIES.keys()))
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的 arXiv 分类: {arxiv_category}。有效的分类包括: {valid_categories}"
                )
            logger.info(f"使用 arXiv 分类: {arxiv_category}")
        else:
            logger.info("使用默认 arXiv 分类: cs")
        
        logger.info(f"选择了 {len(engines)} 个引擎: {engines}，每个引擎最多返回 {MAX_SEARCH_RESULTS_PER_ENGINE} 篇论文")
        
        # 1. 搜索论文（多引擎，每个引擎都返回相同数量的论文）
        all_papers = []
        
        if "arxiv" in engines:
            try:
                logger.info(f"开始搜索 arXiv，关键词: {request.keywords}, 分类: {arxiv_category or 'cs (默认)'}")
                arxiv_papers = search_arxiv_papers(
                    request.keywords,
                    limit=MAX_SEARCH_RESULTS_PER_ENGINE,
                    category=arxiv_category
                )
                all_papers.extend(arxiv_papers)
                logger.info(f"arXiv 搜索完成，找到 {len(arxiv_papers)} 篇论文")
            except ValueError as e:
                # 分类验证错误
                logger.error(f"arXiv 分类验证失败: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"arXiv 搜索失败: {str(e)}", exc_info=True)
        
        # 如果同时使用多个引擎，在请求之间添加延迟，避免触发 Semantic Scholar 速率限制
        if "semantic_scholar" in engines and len(engines) > 1:
            delay_seconds = 2  # 延迟2秒，给 Semantic Scholar API 一些缓冲时间
            logger.info(f"等待 {delay_seconds} 秒后调用 Semantic Scholar API，避免速率限制...")
            time.sleep(delay_seconds)
        
        if "semantic_scholar" in engines:
            try:
                logger.info(f"开始搜索 Semantic Scholar，关键词: {request.keywords}")
                ss_papers = search_semantic_scholar_papers(request.keywords, limit=MAX_SEARCH_RESULTS_PER_ENGINE)
                logger.info(f"Semantic Scholar 搜索完成，找到 {len(ss_papers)} 篇论文")
                if len(ss_papers) > 0:
                    logger.info(f"Semantic Scholar 第一篇论文示例: {ss_papers[0].get('title', 'N/A')[:50]}...")
                all_papers.extend(ss_papers)
                logger.info(f"Semantic Scholar 找到 {len(ss_papers)} 篇论文，已添加到总列表")
            except Exception as e:
                logger.error(f"Semantic Scholar 搜索失败: {str(e)}", exc_info=True)
        
        # 如果同时使用多个引擎，在请求之间添加延迟，避免触发 API 速率限制
        if "pubmed" in engines and len(engines) > 1:
            delay_seconds = 1  # PubMed 通常不需要太长的延迟
            logger.info(f"等待 {delay_seconds} 秒后调用 PubMed API，避免速率限制...")
            time.sleep(delay_seconds)
        
        if "pubmed" in engines:
            try:
                logger.info(f"开始搜索 PubMed，关键词: {request.keywords}")
                pubmed_papers = search_pubmed_papers(request.keywords, limit=MAX_SEARCH_RESULTS_PER_ENGINE)
                logger.info(f"PubMed 搜索完成，找到 {len(pubmed_papers)} 篇论文")
                if len(pubmed_papers) > 0:
                    logger.info(f"PubMed 第一篇论文示例: {pubmed_papers[0].get('title', 'N/A')[:50]}...")
                all_papers.extend(pubmed_papers)
                logger.info(f"PubMed 找到 {len(pubmed_papers)} 篇论文，已添加到总列表")
            except Exception as e:
                logger.error(f"PubMed 搜索失败: {str(e)}", exc_info=True)
        
        # 统计各引擎的论文数量
        arxiv_count = sum(1 for p in all_papers if p.get('source') == 'arxiv')
        ss_count = sum(1 for p in all_papers if p.get('source') == 'semantic_scholar')
        pubmed_count = sum(1 for p in all_papers if p.get('source') == 'pubmed')
        logger.info(f"合并后总计: {len(all_papers)} 篇论文 (arXiv: {arxiv_count}, Semantic Scholar: {ss_count}, PubMed: {pubmed_count})")
        
        if not all_papers:
            logger.warning("所有引擎都未找到论文")
            return SearchResponse(papers=[], total=0)
        
        # 2. 使用 LLM 筛选论文
        logger.info(f"开始 LLM 筛选，从 {len(all_papers)} 篇论文中筛选")
        filtered_papers = filter_papers(
            keywords=request.keywords,
            question=request.question,
            papers=all_papers
        )
        filtered_arxiv_count = sum(1 for p in filtered_papers if p.get('source') == 'arxiv')
        filtered_ss_count = sum(1 for p in filtered_papers if p.get('source') == 'semantic_scholar')
        filtered_pubmed_count = sum(1 for p in filtered_papers if p.get('source') == 'pubmed')
        logger.info(f"LLM 筛选完成，筛选出 {len(filtered_papers)} 篇论文 (arXiv: {filtered_arxiv_count}, Semantic Scholar: {filtered_ss_count}, PubMed: {filtered_pubmed_count})")
        
        # 3. 翻译摘要并提取关键词（并发处理）
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        total = len(filtered_papers)
        processed_papers = [None] * total  # 预分配列表保持顺序
        
        def process_single_paper(index: int, paper: Dict):
            """处理单篇论文"""
            try:
                result = translate_and_extract_keywords(paper, request.question)
                paper_with_translation = {
                    **paper,
                    "title_zh": result.get("title_zh", paper.get("title", "")),
                    "abstract_zh": result["abstract_zh"],
                    "keywords": result["keywords"],
                    "relevance_summary": result["relevance_summary"]
                }
                return index, paper_with_translation
            except Exception as e:
                paper_id = paper.get('arxiv_id') or paper.get('paper_id', 'unknown')
                logger.warning(f"处理论文 {paper_id} 失败: {str(e)}")
                paper_with_translation = {
                    **paper,
                    "abstract_zh": paper.get("abstract", "") or "(Semantic Scholar 数据源中未提供摘要)",
                    "keywords": "",
                    "relevance_summary": ""
                }
                return index, paper_with_translation
        
        # 使用线程池并发处理（最多5个并发，避免API限制）
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(process_single_paper, i, paper): i
                for i, paper in enumerate(filtered_papers)
            }
            
            # 收集结果（使用 as_completed 确保所有任务完成）
            for future in as_completed(future_to_index):
                try:
                    index, paper_result = future.result()
                    processed_papers[index] = paper_result
                except Exception as e:
                    logger.error(f"任务执行失败: {str(e)}")
                    # 处理失败的任务
                    index = future_to_index[future]
                    paper = filtered_papers[index]
                    processed_papers[index] = {
                        **paper,
                        "title_zh": paper.get("title", ""),
                        "abstract_zh": paper.get("abstract", "") or "(Semantic Scholar 数据源中未提供摘要)",
                        "keywords": "",
                        "relevance_summary": ""
                    }
        
        # 4. 转换为响应格式
        paper_responses = []
        final_arxiv_count = 0
        final_ss_count = 0
        final_pubmed_count = 0
        for paper in processed_papers:
            # 处理可能缺失的字段
            abstract = paper.get("abstract", "")
            abstract_zh = paper.get("abstract_zh", "")
            
            # 确保字段类型正确
            if not isinstance(abstract, str):
                abstract = str(abstract) if abstract else ""
            if not isinstance(abstract_zh, str):
                abstract_zh = str(abstract_zh) if abstract_zh else ""
            
            # 如果没有摘要，使用提示文本
            if not abstract:
                abstract = "(Semantic Scholar 数据源中未提供摘要)"
            if not abstract_zh and abstract:
                abstract_zh = abstract
            
            # 处理 published 字段，确保是字符串或 None
            published = paper.get("published")
            if published is not None and not isinstance(published, str):
                published = str(published) if published else None
            
            paper_response = PaperResponse(
                title=paper.get("title", ""),
                title_zh=paper.get("title_zh"),
                abstract=abstract,
                abstract_zh=abstract_zh,
                keywords=paper.get("keywords", ""),
                relevance_summary=paper.get("relevance_summary", ""),
                arxiv_id=paper.get("arxiv_id") or paper.get("paper_id", ""),
                url=paper.get("url", ""),
                pdf_url=paper.get("pdf_url"),
                authors=paper.get("authors", []),
                published=published,
                source=paper.get("source", "unknown")
            )
            paper_responses.append(paper_response)
            if paper.get('source') == 'arxiv':
                final_arxiv_count += 1
            elif paper.get('source') == 'semantic_scholar':
                final_ss_count += 1
            elif paper.get('source') == 'pubmed':
                final_pubmed_count += 1
        
        logger.info(f"最终返回 {len(paper_responses)} 篇论文 (arXiv: {final_arxiv_count}, Semantic Scholar: {final_ss_count}, PubMed: {final_pubmed_count})")
        
        # 保存历史记录
        # 判断记录类型：如果只使用 arxiv 引擎且指定了分类，则为 arxiv_search，否则为 multi_engine
        record_type = 'multi_engine'
        if len(engines) == 1 and engines[0] == 'arxiv' and request.arxiv_category:
            record_type = 'arxiv_search'
        
        try:
            # 将 PaperResponse 转换为字典格式保存
            papers_data = [paper.dict() for paper in paper_responses]
            save_history(
                record_type=record_type,
                params={
                    "keywords": request.keywords,
                    "question": request.question,
                    "engines": engines,
                    "arxiv_category": request.arxiv_category,
                },
                result_summary={
                    "total": len(paper_responses),
                    "papers_count": len(paper_responses)
                },
                papers=papers_data
            )
        except Exception as e:
            logger.warning(f"保存历史记录失败: {str(e)}")
        
        return SearchResponse(papers=paper_responses, total=len(paper_responses))
        
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search", response_model=SearchResponse)
async def search_papers_api(request: SearchRequest):
    """
    搜索并筛选论文
    
    Args:
        request: 包含关键词和问题的请求
        
    Returns:
        论文列表和总数
    """
    return process_search(request)


# 最新论文请求模型
class LatestPapersRequest(BaseModel):
    category: str  # 分类代码（如 "cs", "physics", "math"）
    days: int = 7  # 获取最近多少天的论文（默认7天）
    offset: int = 0  # 分页偏移量（默认0）
    limit: int = 20  # 返回的最大数量（默认20）


@app.post("/api/arxiv/latest", response_model=SearchResponse)
async def get_latest_papers_api(request: LatestPapersRequest):
    """
    获取指定分类的最新论文
    
    Args:
        request: 包含分类、天数、偏移量和限制的请求
        
    Returns:
        论文列表（已翻译摘要）和总数
    """
    try:
        # 验证分类
        if not is_valid_arxiv_category(request.category):
            valid_categories = ', '.join(sorted(ARXIV_CATEGORIES.keys()))
            raise HTTPException(
                status_code=400,
                detail=f"无效的 arXiv 分类: {request.category}。有效的分类包括: {valid_categories}"
            )
        
        logger.info(f"获取最新论文，分类: {request.category}, 天数: {request.days}, offset: {request.offset}, limit: {request.limit}")
        
        # 1. 使用 OAI-PMH 获取最新论文
        papers = get_latest_papers_oai_pmh(
            category=request.category,
            days=request.days,
            offset=request.offset,
            limit=request.limit
        )
        
        if not papers:
            logger.info("未找到论文")
            return SearchResponse(papers=[], total=0)
        
        logger.info(f"获取到 {len(papers)} 篇论文，开始翻译摘要")
        
        # 2. 自动翻译摘要（并发处理，最多5个并发）
        total = len(papers)
        processed_papers = [None] * total
        
        def process_single_paper(index: int, paper: Dict):
            """处理单篇论文（翻译摘要）"""
            try:
                # 复用现有的翻译功能（不需要用户问题，只翻译摘要和标题）
                result = translate_and_extract_keywords(paper, user_question="")
                paper_with_translation = {
                    **paper,
                    "title_zh": result.get("title_zh", paper.get("title", "")),
                    "abstract_zh": result["abstract_zh"],
                    "keywords": result["keywords"],
                    "relevance_summary": ""  # 最新论文不需要相关性评估
                }
                return index, paper_with_translation
            except Exception as e:
                paper_id = paper.get('arxiv_id', 'unknown')
                logger.warning(f"处理论文 {paper_id} 失败: {str(e)}")
                paper_with_translation = {
                    **paper,
                    "title_zh": paper.get("title", ""),
                    "abstract_zh": paper.get("abstract", "") or "",
                    "keywords": "",
                    "relevance_summary": ""
                }
                return index, paper_with_translation
        
        # 使用线程池并发处理（最多5个并发）
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_index = {
                executor.submit(process_single_paper, i, paper): i
                for i, paper in enumerate(papers)
            }
            
            for future in as_completed(future_to_index):
                try:
                    index, paper_result = future.result()
                    processed_papers[index] = paper_result
                except Exception as e:
                    logger.error(f"任务执行失败: {str(e)}")
                    index = future_to_index[future]
                    paper = papers[index]
                    processed_papers[index] = {
                        **paper,
                        "title_zh": paper.get("title", ""),
                        "abstract_zh": paper.get("abstract", "") or "",
                        "keywords": "",
                        "relevance_summary": ""
                    }
        
        # 3. 转换为响应格式
        paper_responses = []
        for paper in processed_papers:
            abstract = paper.get("abstract", "")
            abstract_zh = paper.get("abstract_zh", "")
            
            if not isinstance(abstract, str):
                abstract = str(abstract) if abstract else ""
            if not isinstance(abstract_zh, str):
                abstract_zh = str(abstract_zh) if abstract_zh else ""
            
            if not abstract_zh and abstract:
                abstract_zh = abstract
            
            published = paper.get("published")
            if published is not None and not isinstance(published, str):
                published = str(published) if published else None
            
            paper_response = PaperResponse(
                title=paper.get("title", ""),
                title_zh=paper.get("title_zh"),
                abstract=abstract,
                abstract_zh=abstract_zh,
                keywords=paper.get("keywords", ""),
                relevance_summary=paper.get("relevance_summary", ""),
                arxiv_id=paper.get("arxiv_id") or paper.get("paper_id", ""),
                url=paper.get("url", ""),
                pdf_url=paper.get("pdf_url"),
                authors=paper.get("authors", []),
                published=published,
                source=paper.get("source", "arxiv")
            )
            paper_responses.append(paper_response)
        
        logger.info(f"返回 {len(paper_responses)} 篇论文")
        
        # 保存历史记录
        try:
            # 将 PaperResponse 转换为字典格式保存
            papers_data = [paper.dict() for paper in paper_responses]
            save_history(
                record_type='latest_papers',
                params={
                    "category": request.category,
                    "days": request.days,
                    "offset": request.offset,
                    "limit": request.limit,
                },
                result_summary={
                    "total": len(paper_responses),
                    "papers_count": len(paper_responses)
                },
                papers=papers_data
            )
        except Exception as e:
            logger.warning(f"保存历史记录失败: {str(e)}")
        
        return SearchResponse(papers=paper_responses, total=len(paper_responses))
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取最新论文失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 摘要精炼请求模型
class RefineAbstractRequest(BaseModel):
    arxiv_id: str  # arXiv 论文 ID
    abstract: str  # 原始摘要（可以是中文或英文）
    title: str = ""  # 论文标题（可选，有助于理解上下文）


# 摘要精炼响应模型
class RefineAbstractResponse(BaseModel):
    refined_abstract: str  # 精炼后的摘要


@app.post("/api/arxiv/refine-abstract", response_model=RefineAbstractResponse)
async def refine_abstract_api(request: RefineAbstractRequest):
    """
    精炼论文摘要，使其通俗易懂
    
    Args:
        request: 包含 arXiv ID、原始摘要和标题的请求
        
    Returns:
        精炼后的摘要
    """
    try:
        logger.info(f"精炼摘要请求: {request.arxiv_id}")
        
        # 调用精炼函数（包含缓存机制）
        refined_abstract = refine_abstract(
            arxiv_id=request.arxiv_id,
            abstract=request.abstract,
            title=request.title
        )
        
        logger.info(f"精炼摘要成功: {request.arxiv_id}")
        return RefineAbstractResponse(refined_abstract=refined_abstract)
        
    except Exception as e:
        logger.error(f"精炼摘要失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 历史记录请求模型
class SaveHistoryRequest(BaseModel):
    type: str  # 记录类型（multi_engine, arxiv_search, latest_papers）
    params: Dict  # 搜索参数
    result_summary: Dict  # 结果摘要


class ListHistoryRequest(BaseModel):
    type: Optional[str] = None  # 记录类型（可选，如果为 None 则查询所有类型）
    limit: int = 50  # 返回的最大数量（默认50）


@app.post("/api/history/save")
async def save_history_api(request: SaveHistoryRequest):
    """
    保存历史记录
    
    Args:
        request: 包含记录类型、参数和结果摘要的请求
        
    Returns:
        记录 ID
    """
    try:
        record_id = save_history(
            record_type=request.type,
            params=request.params,
            result_summary=request.result_summary
        )
        return {"id": record_id}
    except Exception as e:
        logger.error(f"保存历史记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/history/list")
async def list_history_api(request: ListHistoryRequest):
    """
    查询历史记录
    
    Args:
        request: 包含记录类型和限制数量的请求
        
    Returns:
        历史记录列表（包含完整的论文数据）
    """
    try:
        records = list_history(
            record_type=request.type,
            limit=request.limit
        )
        return {"records": records}
    except Exception as e:
        logger.error(f"查询历史记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/get/{record_id}")
async def get_history_record(record_id: str):
    """
    获取单个历史记录的详细信息（包含完整论文数据）
    
    Args:
        record_id: 历史记录 ID
        
    Returns:
        历史记录详情（包含完整论文数据）
    """
    try:
        # 查询所有类型的历史记录
        all_records = list_history(record_type=None, limit=1000)
        
        # 查找匹配的记录
        for record in all_records:
            if record.get("id") == record_id:
                return {"record": record}
        
        raise HTTPException(status_code=404, detail="历史记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
