"""
测试 Google Scholar 搜索工具
使用 LangChain 的 GoogleScholarQueryRun
"""
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_google_scholar():
    """测试 Google Scholar 搜索"""
    try:
        # 检查 API Key
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            logger.warning("未找到 SERP_API_KEY 环境变量")
            logger.info("请设置 SERP_API_KEY 环境变量（从 https://serpapi.com/ 获取）")
            logger.info("可以在 .env 文件中添加: SERP_API_KEY=your_api_key")
            return None
        
        logger.info("✓ 找到 SERP_API_KEY")
        
        # 导入 LangChain Google Scholar 工具
        try:
            from langchain_community.tools.google_scholar import GoogleScholarQueryRun
            from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper
            logger.info("✓ 成功导入 LangChain Google Scholar 工具")
        except ImportError as e:
            logger.error(f"✗ 导入失败: {str(e)}")
            logger.info("请安装依赖: pip install google-search-results langchain-community")
            return None
        
        # 设置环境变量
        os.environ["SERP_API_KEY"] = serp_api_key
        
        # 创建工具
        logger.info("创建 Google Scholar 工具...")
        tool = GoogleScholarQueryRun(api_wrapper=GoogleScholarAPIWrapper())
        
        # 测试查询
        test_query = "LLM Models"
        logger.info(f"执行搜索查询: {test_query}")
        
        result = tool.run(test_query)
        
        logger.info(f"✓ 搜索成功！")
        logger.info(f"返回结果长度: {len(result)} 字符")
        
        # 打印结果预览
        logger.info("\n" + "="*80)
        logger.info("结果预览（前 500 字符）:")
        logger.info("="*80)
        preview = result[:500] if len(result) > 500 else result
        logger.info(preview)
        if len(result) > 500:
            logger.info("...")
        logger.info("="*80)
        
        # 保存完整结果到文件
        output_file = "test/google_scholar_test_results.json"
        os.makedirs("test", exist_ok=True)
        
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "query": test_query,
            "api_key_set": bool(serp_api_key),
            "result_length": len(result),
            "result": result,
            "preview": preview
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ 结果已保存到: {output_file}")
        
        # 尝试解析结果（如果可能）
        try:
            # Google Scholar 返回的是字符串格式，尝试解析
            lines = result.split('\n')
            papers = []
            current_paper = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Title:'):
                    if current_paper:
                        papers.append(current_paper)
                    current_paper = {'title': line.replace('Title:', '').strip()}
                elif line.startswith('Authors:'):
                    current_paper['authors'] = line.replace('Authors:', '').strip()
                elif line.startswith('Summary:'):
                    current_paper['summary'] = line.replace('Summary:', '').strip()
                elif line.startswith('Total-Citations:'):
                    current_paper['citations'] = line.replace('Total-Citations:', '').strip()
            
            if current_paper:
                papers.append(current_paper)
            
            if papers:
                logger.info(f"\n解析出 {len(papers)} 篇论文:")
                for i, paper in enumerate(papers[:5], 1):  # 只显示前5篇
                    logger.info(f"\n论文 {i}:")
                    logger.info(f"  标题: {paper.get('title', 'N/A')}")
                    logger.info(f"  作者: {paper.get('authors', 'N/A')}")
                    logger.info(f"  引用数: {paper.get('citations', 'N/A')}")
                
                # 保存解析后的结果
                parsed_output_file = "test/google_scholar_parsed_results.json"
                parsed_data = {
                    "timestamp": datetime.now().isoformat(),
                    "query": test_query,
                    "total_papers": len(papers),
                    "papers": papers
                }
                
                with open(parsed_output_file, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✓ 解析后的结果已保存到: {parsed_output_file}")
        
        except Exception as e:
            logger.warning(f"解析结果时出错: {str(e)}")
        
        return result
        
    except Exception as e:
        logger.error(f"✗ 测试失败: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    logger.info("开始测试 Google Scholar 搜索工具...")
    logger.info("="*80)
    result = test_google_scholar()
    
    if result:
        logger.info("\n" + "="*80)
        logger.info("✓ Google Scholar 测试完成！")
    else:
        logger.info("\n" + "="*80)
        logger.info("✗ Google Scholar 测试未完成，请检查错误信息")









