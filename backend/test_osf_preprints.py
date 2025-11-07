"""
测试 OSF API Preprints 端点
检查能否检索预印本论文
"""

import requests
import json
from typing import Dict, List, Optional

# OSF API 基础 URL
BASE_URL = "https://api.osf.io/v2"

def test_preprints_search(query: Optional[str] = None, limit: int = 10):
    """
    测试 OSF Preprints 端点
    
    Args:
        query: 搜索关键词（通过 filter 参数）
        limit: 返回结果数量限制
    """
    print("=" * 60)
    print("测试 OSF API Preprints 端点")
    print("=" * 60)
    
    # 测试1: 基本请求（获取预印本列表）
    print("\n1. 测试基本请求（获取预印本列表）")
    print("-" * 60)
    url = f"{BASE_URL}/preprints/"
    params = {
        "page[size]": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            preprints = data.get("data", [])
            meta = data.get("meta", {})
            
            print(f"✓ 成功获取数据")
            print(f"返回的预印本数量: {len(preprints)}")
            print(f"总数: {meta.get('total', 'N/A')}")
            print(f"每页数量: {meta.get('per_page', 'N/A')}")
            
            if preprints:
                print(f"\n前3个预印本示例:")
                for i, preprint in enumerate(preprints[:3], 1):
                    attrs = preprint.get("attributes", {})
                    print(f"\n[{i}] {attrs.get('title', 'N/A')}")
                    print(f"    ID: {preprint.get('id', 'N/A')}")
                    print(f"    类型: {preprint.get('type', 'N/A')}")
                    print(f"    日期创建: {attrs.get('date_created', 'N/A')}")
                    print(f"    日期发布: {attrs.get('date_published', 'N/A')}")
                    print(f"    摘要预览: {attrs.get('description', 'N/A')[:100]}...")
                    print(f"    标签: {attrs.get('tags', [])}")
                    
                    # 检查链接
                    links = preprint.get("links", {})
                    if links:
                        print(f"    网页链接: {links.get('html', 'N/A')}")
                        print(f"    PDF链接: {links.get('preprint_doi', 'N/A')}")
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 使用 filter 参数搜索
    if query:
        print(f"\n\n2. 测试搜索功能（关键词: {query}）")
        print("-" * 60)
        url = f"{BASE_URL}/preprints/"
        params = {
            "page[size]": limit,
            "filter[title]": query  # 尝试按标题过滤
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                preprints = data.get("data", [])
                meta = data.get("meta", {})
                
                print(f"✓ 搜索成功")
                print(f"找到的预印本数量: {len(preprints)}")
                print(f"总数: {meta.get('total', 'N/A')}")
                
                if preprints:
                    print(f"\n搜索结果示例:")
                    for i, preprint in enumerate(preprints[:3], 1):
                        attrs = preprint.get("attributes", {})
                        print(f"\n[{i}] {attrs.get('title', 'N/A')}")
                        print(f"    ID: {preprint.get('id', 'N/A')}")
                        print(f"    摘要: {attrs.get('description', 'N/A')[:150]}...")
                else:
                    print("未找到匹配的预印本")
            else:
                print(f"✗ 搜索失败: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                
        except Exception as e:
            print(f"✗ 搜索异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 测试3: 检查可用的过滤字段
    print(f"\n\n3. 检查 API 文档中提到的过滤功能")
    print("-" * 60)
    print("根据 OSF API 文档，支持的过滤方式:")
    print("- filter[title]: 按标题过滤")
    print("- filter[tags]: 按标签过滤")
    print("- filter[date_created]: 按创建日期过滤")
    print("- filter[date_published]: 按发布日期过滤")
    print("- 等等...")
    
    # 测试4: 尝试不同的过滤方式
    print(f"\n\n4. 测试多种过滤方式")
    print("-" * 60)
    
    test_filters = [
        {"filter[title]": "machine learning"},
        {"filter[tags]": "ai"},
    ]
    
    for filter_params in test_filters:
        print(f"\n测试过滤: {filter_params}")
        url = f"{BASE_URL}/preprints/"
        params = {
            "page[size]": 5,
            **filter_params
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                preprints = data.get("data", [])
                print(f"  找到 {len(preprints)} 个结果")
                if preprints:
                    attrs = preprints[0].get("attributes", {})
                    print(f"  示例: {attrs.get('title', 'N/A')[:60]}...")
            else:
                print(f"  状态码: {response.status_code}")
        except Exception as e:
            print(f"  错误: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    # 测试基本功能
    test_preprints_search()
    
    # 测试搜索功能
    print("\n\n" + "=" * 60)
    test_preprints_search(query="AI", limit=5)

