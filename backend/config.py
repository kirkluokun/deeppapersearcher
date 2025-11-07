"""
配置文件
定义 arXiv 检索和 LLM 筛选的配置参数
"""

# arXiv 分类限制（目前仅支持 cs）
ARXIV_CATEGORY = "cs"

# 每个检索引擎的最大检索数量（每个引擎都使用相同的配置）
MAX_SEARCH_RESULTS_PER_ENGINE = 50

# LLM 筛选后最多返回的论文数量
MAX_FILTERED_RESULTS = 20

# Gemini 模型配置
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TEMPERATURE = 0

# 未来可扩展的分类列表
AVAILABLE_CATEGORIES = {
    "cs": "Computer Science",
    # 后续可以添加更多分类
    # "math": "Mathematics",
    # "physics": "Physics",
    # "econ": "Economics",
}
