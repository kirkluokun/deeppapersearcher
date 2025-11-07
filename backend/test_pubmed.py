"""
测试 PubMed API
检查 PubMedRetriever 的使用方式和是否需要 API key
"""

import os
from dotenv import load_dotenv

# 加载环境变量
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

try:
    from langchain_community.retrievers import PubMedRetriever
    print("✓ 成功导入 PubMedRetriever")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请安装: pip install langchain-community")
    exit(1)

# 检查 API key
api_key = os.getenv('NCBI_API_KEY')
print(f"\nNCBI_API_KEY: {'已设置' if api_key else '未设置'}")

# 测试 PubMedRetriever
print("\n" + "=" * 60)
print("测试 PubMedRetriever")
print("=" * 60)

try:
    # 创建 retriever（可以传入 API key）
    if api_key:
        print(f"\n使用 API key 创建 retriever...")
        retriever = PubMedRetriever(top_k_results=10, email="test@example.com")
        # 注意：PubMedRetriever 可能不支持直接传入 API key
        # 但可以通过环境变量设置
        os.environ['NCBI_API_KEY'] = api_key
    else:
        print(f"\n不使用 API key 创建 retriever...")
        retriever = PubMedRetriever(top_k_results=10)
    
    # 测试搜索
    query = "AI agent"
    print(f"\n搜索查询: {query}")
    print(f"限制结果: 10 篇")
    print("-" * 60)
    
    results = retriever.invoke(query)
    
    print(f"\n找到 {len(results)} 篇论文\n")
    
    # 显示结果
    for i, doc in enumerate(results, 1):
        print(f"[{i}] {doc.metadata.get('Title', 'N/A')}")
        print(f"    UID: {doc.metadata.get('uid', 'N/A')}")
        print(f"    发布时间: {doc.metadata.get('Published', 'N/A')}")
        
        # 显示内容摘要（如果有）
        content = doc.page_content
        if content:
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"    摘要预览: {preview}")
        else:
            print(f"    摘要: (无摘要)")
        
        print()
    
    # 检查返回的数据结构
    if results:
        print("\n" + "=" * 60)
        print("数据结构分析")
        print("=" * 60)
        first_doc = results[0]
        print(f"\nDocument 类型: {type(first_doc)}")
        print(f"page_content 长度: {len(first_doc.page_content)}")
        print(f"metadata 键: {list(first_doc.metadata.keys())}")
        print(f"\n完整 metadata 示例:")
        for key, value in first_doc.metadata.items():
            print(f"  {key}: {value}")
    
    print("\n✓ PubMed API 测试成功！")
    
except Exception as e:
    print(f"\n✗ PubMed API 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()

