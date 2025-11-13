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
GEMINI_MODEL = "gemini-2.0-flash"  # 用于翻译和关键词提取
GEMINI_TEMPERATURE = 0

# Gemini 2.5 Flash 模型配置（用于摘要精炼）
GEMINI_REFINE_MODEL = "gemini-2.5-flash"  # 使用 Gemini 2.5 Flash 进行摘要精炼
GEMINI_REFINE_TEMPERATURE = 0.3  # 稍微提高温度，使输出更自然

# OAI-PMH 配置
OAI_PMH_BASE_URL = "https://oaipmh.arxiv.org/oai"
OAI_PMH_METADATA_PREFIX = "arXiv"  # 使用 arXiv 格式（包含作者、分类、许可证信息）
ARXIV_SEARCH_MODE = "traditional"  # 搜索模式：'traditional'（传统 API）或 'oai-pmh'（OAI-PMH 协议）
# 注意：关键词搜索强制使用 RESTful API（OAI-PMH 不支持关键词搜索）
# OAI-PMH 仅用于获取最新论文（不需要关键词过滤的场景）

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


def map_category_to_oai_set(category: str) -> str:
    """
    将主要分类代码映射为 OAI-PMH Set 格式
    
    Args:
        category: 主要分类代码（如 "cs", "physics", "math"）
        
    Returns:
        OAI-PMH Set 格式字符串（如 "cs", "physics", "math"）
        
    Raises:
        ValueError: 如果分类代码无效
    """
    if not is_valid_arxiv_category(category):
        raise ValueError(f"无效的 arXiv 分类: {category}")
    
    # arXiv OAI-PMH Set 格式：主要分类直接对应 Set 名称
    # 例如：cs -> cs, physics -> physics, math -> math
    return category
