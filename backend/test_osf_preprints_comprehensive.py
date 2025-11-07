"""
OSF API Preprints 端点测试
保存测试结果到文件
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# OSF API 基础 URL
BASE_URL = "https://api.osf.io/v2"

def test_preprints_comprehensive(query: Optional[str] = None, limit: int = 10):
    """
    全面测试 OSF Preprints 端点
    
    Args:
        query: 搜索关键词（通过 filter 参数）
        limit: 返回结果数量限制
    """
    results = {
        "test_time": datetime.now().isoformat(),
        "query": query,
        "limit": limit,
        "tests": []
    }
    
    # 测试1: 基本请求（获取预印本列表）
    print("1. 测试基本请求...")
    test1 = {
        "name": "基本请求（获取预印本列表）",
        "url": f"{BASE_URL}/preprints/",
        "params": {"page[size]": limit},
        "status": None,
        "success": False,
        "data": None,
        "error": None
    }
    
    try:
        response = requests.get(test1["url"], params=test1["params"], timeout=30)
        test1["status"] = response.status_code
        
        if response.status_code == 200:
            data = response.json()
            preprints = data.get("data", [])
            meta = data.get("meta", {})
            
            test1["success"] = True
            test1["data"] = {
                "total_preprints": len(preprints),
                "meta": meta,
                "sample_preprints": []
            }
            
            # 保存前3个预印本的详细信息
            for preprint in preprints[:3]:
                attrs = preprint.get("attributes", {})
                links = preprint.get("links", {})
                rels = preprint.get("relationships", {})
                
                preprint_info = {
                    "id": preprint.get("id"),
                    "type": preprint.get("type"),
                    "title": attrs.get("title"),
                    "description": attrs.get("description", "")[:500],  # 限制长度
                    "tags": attrs.get("tags", []),
                    "date_created": attrs.get("date_created"),
                    "date_published": attrs.get("date_published"),
                    "is_published": attrs.get("is_published"),
                    "public": attrs.get("public"),
                    "subjects": attrs.get("subjects", []),
                    "links": {
                        "html": links.get("html"),
                        "preprint_doi": links.get("preprint_doi"),
                        "self": links.get("self")
                    },
                    "relationships": {
                        "contributors": rels.get("contributors", {}).get("links", {}).get("related", {}).get("href"),
                        "bibliographic_contributors": rels.get("bibliographic_contributors", {}).get("links", {}).get("related", {}).get("href"),
                        "primary_file": rels.get("primary_file", {}).get("links", {}).get("related", {}).get("href"),
                        "files": rels.get("files", {}).get("links", {}).get("related", {}).get("href")
                    }
                }
                test1["data"]["sample_preprints"].append(preprint_info)
        else:
            test1["error"] = response.text[:500]
            
    except Exception as e:
        test1["error"] = str(e)
    
    results["tests"].append(test1)
    
    # 测试2: 搜索功能（如果提供了查询）
    if query:
        print(f"2. 测试搜索功能（关键词: {query}）...")
        test2 = {
            "name": f"搜索功能（关键词: {query}）",
            "url": f"{BASE_URL}/preprints/",
            "params": {
                "page[size]": limit,
                "filter[title]": query
            },
            "status": None,
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            response = requests.get(test2["url"], params=test2["params"], timeout=30)
            test2["status"] = response.status_code
            
            if response.status_code == 200:
                data = response.json()
                preprints = data.get("data", [])
                meta = data.get("meta", {})
                
                test2["success"] = True
                test2["data"] = {
                    "total_found": len(preprints),
                    "meta": meta,
                    "results": []
                }
                
                for preprint in preprints[:5]:
                    attrs = preprint.get("attributes", {})
                    links = preprint.get("links", {})
                    
                    test2["data"]["results"].append({
                        "id": preprint.get("id"),
                        "title": attrs.get("title"),
                        "description": attrs.get("description", "")[:300],
                        "date_published": attrs.get("date_published"),
                        "html_link": links.get("html"),
                        "doi_link": links.get("preprint_doi")
                    })
            else:
                test2["error"] = response.text[:500]
                
        except Exception as e:
            test2["error"] = str(e)
        
        results["tests"].append(test2)
    
    # 测试3: 获取作者信息
    print("3. 测试获取作者信息...")
    if results["tests"][0]["success"] and results["tests"][0]["data"]["sample_preprints"]:
        preprint_id = results["tests"][0]["data"]["sample_preprints"][0]["id"]
        
        test3 = {
            "name": f"获取作者信息（预印本 ID: {preprint_id}）",
            "url": f"{BASE_URL}/preprints/{preprint_id}/contributors/",
            "params": {"embed": "users", "page[size]": 10},
            "status": None,
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            response = requests.get(test3["url"], params=test3["params"], timeout=30)
            test3["status"] = response.status_code
            
            if response.status_code == 200:
                data = response.json()
                contributors = data.get("data", [])
                included = data.get("included", [])
                
                test3["success"] = True
                test3["data"] = {
                    "total_contributors": len(contributors),
                    "embedded_users": len(included),
                    "contributors": []
                }
                
                # 提取作者信息
                for contrib in contributors[:5]:
                    attrs = contrib.get("attributes", {})
                    rels = contrib.get("relationships", {})
                    embeds = contrib.get("embeds", {})
                    
                    author_info = {
                        "bibliographic": attrs.get("bibliographic"),
                        "permission": attrs.get("permission"),
                        "index": attrs.get("index")
                    }
                    
                    # 尝试从 embeds 获取用户信息
                    if embeds.get("users"):
                        user_data = embeds["users"].get("data", {})
                        user_attrs = user_data.get("attributes", {})
                        author_info["name"] = user_attrs.get("full_name")
                        author_info["given_name"] = user_attrs.get("given_name")
                        author_info["family_name"] = user_attrs.get("family_name")
                    
                    test3["data"]["contributors"].append(author_info)
                    
        except Exception as e:
            test3["error"] = str(e)
        
        results["tests"].append(test3)
    
    # 测试4: 获取 PDF 文件信息
    print("4. 测试获取 PDF 文件信息...")
    if results["tests"][0]["success"] and results["tests"][0]["data"]["sample_preprints"]:
        preprint = results["tests"][0]["data"]["sample_preprints"][0]
        primary_file_link = preprint["relationships"].get("primary_file")
        
        if primary_file_link:
            test4 = {
                "name": f"获取 PDF 文件信息",
                "url": primary_file_link,
                "params": {},
                "status": None,
                "success": False,
                "data": None,
                "error": None
            }
            
            try:
                response = requests.get(test4["url"], timeout=30)
                test4["status"] = response.status_code
                
                if response.status_code == 200:
                    data = response.json()
                    file_data = data.get("data", {})
                    attrs = file_data.get("attributes", {})
                    links = file_data.get("links", {})
                    
                    test4["success"] = True
                    test4["data"] = {
                        "file_id": file_data.get("id"),
                        "file_name": attrs.get("name"),
                        "file_kind": attrs.get("kind"),
                        "file_size": attrs.get("size"),
                        "download_link": links.get("download"),
                        "html_link": links.get("html")
                    }
                else:
                    test4["error"] = response.text[:500]
                    
            except Exception as e:
                test4["error"] = str(e)
            
            results["tests"].append(test4)
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("OSF API Preprints 端点全面测试")
    print("=" * 60)
    
    # 执行测试
    results = test_preprints_comprehensive(query="machine learning", limit=10)
    
    # 保存结果到 JSON 文件
    output_file = "osf_preprints_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 测试完成，结果已保存到: {output_file}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    for test in results["tests"]:
        status_icon = "✓" if test["success"] else "✗"
        print(f"{status_icon} {test['name']}")
        if test["success"]:
            if "total_preprints" in test.get("data", {}):
                print(f"   找到 {test['data']['total_preprints']} 个预印本")
            elif "total_found" in test.get("data", {}):
                print(f"   找到 {test['data']['total_found']} 个结果")
            elif "total_contributors" in test.get("data", {}):
                print(f"   找到 {test['data']['total_contributors']} 个贡献者")
            elif "file_name" in test.get("data", {}):
                print(f"   文件: {test['data']['file_name']}")
        else:
            print(f"   错误: {test.get('error', 'Unknown error')}")

