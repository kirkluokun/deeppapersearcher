"""
测试 PubMed 搜索模块
"""

import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pubmed_search import search_papers

if __name__ == "__main__":
    print("=" * 60)
    print("测试 PubMed 搜索模块")
    print("=" * 60)
    
    try:
        keywords = "AI agent"
        limit = 5
        print(f"\n搜索关键词: {keywords}")
        print(f"限制结果: {limit} 篇")
        print("-" * 60)
        
        papers = search_papers(keywords, limit=limit)
        
        print(f"\n找到 {len(papers)} 篇论文\n")
        
        for i, paper in enumerate(papers, 1):
            print(f"[{i}] {paper.get('title', 'N/A')}")
            print(f"    ID: {paper.get('paper_id', 'N/A')}")
            print(f"    来源: {paper.get('source', 'N/A')}")
            print(f"    发布时间: {paper.get('published', 'N/A')}")
            print(f"    URL: {paper.get('url', 'N/A')}")
            abstract = paper.get('abstract', '')
            if abstract:
                preview = abstract[:150] + "..." if len(abstract) > 150 else abstract
                print(f"    摘要预览: {preview}")
            else:
                print(f"    摘要: (无摘要)")
            print()
        
        print("✓ PubMed 搜索模块测试成功！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

