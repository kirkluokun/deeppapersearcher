"""
Semantic Scholar API 检索测试脚本
参考文档: https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/post_graph_get_papers
"""

import requests
import json
import time
from typing import List, Dict, Optional


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
        limit: int = 30,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        fields_of_study: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        搜索论文（使用 GET /paper/search）
        
        Args:
            query: 搜索查询字符串
            limit: 返回结果数量限制（默认30）
            fields: 要返回的字段列表（默认包含基本字段）
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
                print("遇到速率限制，等待 5 秒后重试...")
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
            print(f"API 请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
                if e.response.status_code == 429:
                    print("\n提示: 您已达到速率限制。建议:")
                    print("1. 等待一段时间后重试")
                    print("2. 申请 API 密钥以获得更高的速率限制: https://www.semanticscholar.org/product/api")
            raise
    
    def get_papers_by_ids(
        self,
        paper_ids: List[str],
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        根据论文 ID 批量获取论文信息（使用 POST /paper/batch）
        
        Args:
            paper_ids: 论文 ID 列表
            fields: 要返回的字段列表
            
        Returns:
            论文列表
        """
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
        
        url = f"{self.BASE_URL}/paper/batch"
        
        params = {
            "ids": paper_ids,
            "fields": ",".join(fields)
        }
        
        try:
            response = requests.post(
                url,
                json=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API 请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
            raise


def test_search():
    """测试搜索功能"""
    print("=" * 60)
    print("Semantic Scholar API 检索测试")
    print("=" * 60)
    
    # 初始化 API 客户端（不需要 API key 也可以使用，但有限制）
    api = SemanticScholarAPI()
    
    # 测试搜索
    query = "machine learning"
    print(f"\n搜索查询: {query}")
    print(f"限制结果: 30 篇")
    print(f"研究领域限制: 无（支持所有领域）")
    print("-" * 60)
    
    try:
        papers = api.search_papers(query, limit=30)
        
        print(f"\n找到 {len(papers)} 篇论文")
        
        # 统计摘要情况
        papers_with_abstract = [p for p in papers if p.get('abstract')]
        print(f"有摘要的论文: {len(papers_with_abstract)} 篇 ({len(papers_with_abstract)/len(papers)*100:.1f}%)")
        print(f"无摘要的论文: {len(papers) - len(papers_with_abstract)} 篇\n")
        
        # 显示前5篇论文的详细信息
        for i, paper in enumerate(papers[:5], 1):
            print(f"[{i}] {paper.get('title', 'N/A')}")
            print(f"    ID: {paper.get('paperId', 'N/A')}")
            print(f"    年份: {paper.get('year', 'N/A')}")
            print(f"    引用数: {paper.get('citationCount', 0)}")
            print(f"    参考文献数: {paper.get('referenceCount', 0)}")
            authors = paper.get('authors', [])
            if authors:
                author_names = ', '.join([a.get('name', '') for a in authors[:3]])
                if len(authors) > 3:
                    author_names += f" 等 ({len(authors)} 位作者)"
                print(f"    作者: {author_names}")
            if paper.get('venue'):
                print(f"    发表场所: {paper.get('venue')}")
            if paper.get('fieldsOfStudy'):
                print(f"    研究领域: {', '.join(paper.get('fieldsOfStudy', []))}")
            abstract = paper.get('abstract')
            if abstract:
                if len(abstract) > 200:
                    abstract_display = abstract[:200] + "..."
                else:
                    abstract_display = abstract
                print(f"    摘要: {abstract_display}")
            else:
                print(f"    摘要: (无摘要 - Semantic Scholar 数据源中未提供)")
                # 如果有开放访问PDF，显示提示
                if paper.get('openAccessPdf') and paper['openAccessPdf'].get('disclaimer'):
                    print(f"    提示: 可能因版权限制未提供摘要，请查看原论文")
            print(f"    网页URL: {paper.get('url', 'N/A')}")
            
            # 显示 PDF 下载地址
            pdf_info = paper.get('openAccessPdf', {})
            pdf_url = pdf_info.get('url', '')
            if pdf_url and pdf_url.strip():
                pdf_status = pdf_info.get('status', 'N/A')
                print(f"    PDF下载: {pdf_url}")
                print(f"    PDF状态: {pdf_status} ({pdf_info.get('license', 'N/A')})")
            else:
                print(f"    PDF下载: (无开放获取PDF)")
            print()
        
        # 保存完整结果到 JSON 文件
        output_file = "semantic_scholar_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存到: {output_file}")
        
        return papers
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    test_search()

