"""
配置文件
定义 arXiv 检索和 LLM 筛选的配置参数
"""

# arXiv 默认分类（向后兼容）
ARXIV_CATEGORY = "cs"

# 每个检索引擎的最大检索数量（每个引擎都使用相同的配置）
MAX_SEARCH_RESULTS_PER_ENGINE = 50

# LLM 筛选后最多返回的论文数量
MAX_FILTERED_RESULTS = 20

# Gemini 模型配置
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TEMPERATURE = 0

# arXiv 所有主要分类定义
# 包含 8 个主要学科分类及其中文名称
ARXIV_CATEGORIES = {
    "physics": "物理学",
    "math": "数学",
    "cs": "计算机科学",
    "q-bio": "定量生物学",
    "q-fin": "定量金融",
    "stat": "统计学",
    "eess": "电气工程与系统科学",
    "econ": "经济学",
}

# 分类代码到中文名称的映射（兼容旧代码）
AVAILABLE_CATEGORIES = ARXIV_CATEGORIES.copy()


def is_valid_arxiv_category(category: str) -> bool:
    """
    验证 arXiv 分类代码是否有效
    
    Args:
        category: 分类代码（如 "cs", "physics", "math"）
        
    Returns:
        如果分类有效返回 True，否则返回 False
    """
    return category in ARXIV_CATEGORIES


def get_category_display_name(category: str) -> str:
    """
    获取分类的中文显示名称
    
    Args:
        category: 分类代码
        
    Returns:
        分类的中文名称，如果分类无效返回原分类代码
    """
    return ARXIV_CATEGORIES.get(category, category)
