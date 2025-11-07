"""
FastAPI 主服务
提供论文搜索和筛选的 API 接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import logging
import json

from arxiv_search import search_papers
from llm_filter import filter_papers
from translate_extract import translate_and_extract_keywords

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


# 响应模型
class PaperResponse(BaseModel):
    title: str
    abstract: str
    abstract_zh: str  # 中文摘要
    keywords: str  # 关键词（中文）
    relevance_summary: str  # 相关性评估概述
    arxiv_id: str
    url: str
    authors: List[str]
    published: str | None


class SearchResponse(BaseModel):
    papers: List[PaperResponse]
    total: int


@app.get("/")
async def root():
    """根路径"""
    return {"message": "arXiv 论文检索系统 API"}


async def process_search_with_progress(request: SearchRequest):
    """处理搜索请求并推送进度"""
    try:
        # 发送初始状态
        initial_data = json.dumps({'type': 'status', 'message': '开始搜索 arXiv 论文...', 'progress': 0}, ensure_ascii=False)
        logger.info(f"发送初始状态: {initial_data}")
        yield f"data: {initial_data}\n\n"
        
        # 1. 搜索论文
        papers = search_papers(request.keywords)
        status_data = json.dumps({
            'type': 'status',
            'message': f'找到 {len(papers)} 篇论文，开始筛选...',
            'progress': 10
        }, ensure_ascii=False)
        logger.info(f"发送状态1: {status_data}")
        yield f"data: {status_data}\n\n"
        
        if not papers:
            complete_data = json.dumps({'type': 'complete', 'papers': [], 'total': 0}, ensure_ascii=False)
            yield f"data: {complete_data}\n\n"
            return
        
        # 2. 使用 LLM 筛选论文
        filtered_papers = filter_papers(
            keywords=request.keywords,
            question=request.question,
            papers=papers
        )
        status_data2 = json.dumps({
            'type': 'status',
            'message': f'筛选完成，剩余 {len(filtered_papers)} 篇，开始翻译和理解...',
            'progress': 30
        }, ensure_ascii=False)
        yield f"data: {status_data2}\n\n"
        
        # 3. 翻译摘要并提取关键词（并发处理，带进度）
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        total = len(filtered_papers)
        processed_papers = [None] * total  # 预分配列表保持顺序
        completed_count = 0
        
        def process_single_paper(index: int, paper: Dict):
            """处理单篇论文"""
            try:
                result = translate_and_extract_keywords(paper, request.question)
                paper_with_translation = {
                    **paper,
                    "abstract_zh": result["abstract_zh"],
                    "keywords": result["keywords"],
                    "relevance_summary": result["relevance_summary"]
                }
                return ('success', index, paper_with_translation, paper['title'])
            except Exception as e:
                logger.warning(f"处理论文 {paper.get('arxiv_id', 'unknown')} 失败: {str(e)}")
                paper_with_translation = {
                    **paper,
                    "abstract_zh": paper.get("abstract", ""),
                    "keywords": "",
                    "relevance_summary": ""
                }
                return ('success', index, paper_with_translation, paper['title'])
        
        # 使用线程池并发处理（最多5个并发，避免API限制）
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(process_single_paper, i, paper): i
                for i, paper in enumerate(filtered_papers)
            }
            
            # 收集结果并发送进度（使用 as_completed 确保所有任务完成）
            for future in as_completed(future_to_index):
                try:
                    event_type, index, paper_result, paper_title = future.result()
                    if event_type == 'success':
                        processed_papers[index] = paper_result
                        completed_count += 1
                        progress = 30 + int((completed_count / total) * 60)
                        progress_data = json.dumps({
                            'type': 'progress',
                            'current': completed_count,
                            'total': total,
                            'paper_title': paper_title[:50] if paper_title else '',
                            'progress': progress
                        }, ensure_ascii=False)
                        logger.info(f"发送进度: {completed_count}/{total}, progress={progress}")
                        yield f"data: {progress_data}\n\n"
                except Exception as e:
                    logger.error(f"任务执行失败: {str(e)}")
                    # 处理失败的任务
                    index = future_to_index[future]
                    paper = filtered_papers[index]
                    processed_papers[index] = {
                        **paper,
                        "abstract_zh": paper.get("abstract", ""),
                        "keywords": "",
                        "relevance_summary": ""
                    }
                    completed_count += 1
                    progress = 30 + int((completed_count / total) * 60)
                    error_progress_data = json.dumps({
                        'type': 'progress',
                        'current': completed_count,
                        'total': total,
                        'paper_title': paper.get('title', '')[:50] if paper.get('title') else '',
                        'progress': progress
                    }, ensure_ascii=False)
                    yield f"data: {error_progress_data}\n\n"
        
        # 4. 转换为响应格式
        paper_responses = [
            PaperResponse(
                title=paper["title"],
                abstract=paper["abstract"],
                abstract_zh=paper.get("abstract_zh", paper["abstract"]),
                keywords=paper.get("keywords", ""),
                relevance_summary=paper.get("relevance_summary", ""),
                arxiv_id=paper["arxiv_id"],
                url=paper["url"],
                authors=paper["authors"],
                published=paper["published"]
            )
            for paper in processed_papers
        ]
        
        # 发送完成
        complete_data = json.dumps({
            'type': 'complete',
            'papers': [p.model_dump() for p in paper_responses],
            'total': len(paper_responses)
        }, ensure_ascii=False)
        yield f"data: {complete_data}\n\n"
        
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        error_data = json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)
        yield f"data: {error_data}\n\n"


@app.post("/api/search")
async def search_papers_api(request: SearchRequest):
    """
    搜索并筛选论文（使用 SSE 推送进度）
    
    Args:
        request: 包含关键词和问题的请求
        
    Returns:
        SSE 流，包含进度和最终结果
    """
    return StreamingResponse(
        process_search_with_progress(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
