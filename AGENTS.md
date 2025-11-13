<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# DeepPaperSearcher 项目指南

本文档为 AI 助手提供项目开发指南，帮助理解项目架构和开发规范。

## 项目概述

DeepPaperSearcher 是一个基于 Gemini 2.0 Flash 的智能论文检索和筛选系统，支持多引擎搜索（arXiv、Semantic Scholar、PubMed），使用 LLM 进行智能筛选，并提供摘要翻译和关键词提取功能。

**新功能**: 系统现在支持 arXiv 的所有 8 个主要学科分类，并提供独立的 arXiv 专用搜索页面，用户可以选择特定分类进行搜索。

## 项目结构

```
DeepPaperSearcher/
├── start.sh                    # 一键启动脚本（前后端）
├── backend/                    # Python 后端
│   ├── main.py                 # FastAPI 主服务（API 入口）
│   ├── arxiv_search.py         # arXiv 检索模块
│   ├── semantic_scholar_search.py  # Semantic Scholar 检索模块
│   ├── pubmed_search.py        # PubMed 检索模块
│   ├── llm_filter.py           # LLM 智能筛选模块
│   ├── translate_extract.py   # 翻译和关键词提取模块
│   ├── config.py               # 配置文件（检索数量、模型参数等）
│   └── requirements.txt        # Python 依赖
├── frontend/                   # React + TypeScript 前端
│   ├── src/
│   │   ├── App.tsx             # 主应用组件（路由配置）
│   │   ├── pages/              # 页面组件
│   │   │   ├── MultiEngineSearch.tsx  # 多引擎搜索页面
│   │   │   └── ArxivSearch.tsx        # arXiv 专用搜索页面
│   │   ├── components/         # UI 组件
│   │   │   ├── SearchForm.tsx  # 搜索表单（多引擎）
│   │   │   ├── CategorySelector.tsx   # 分类选择组件
│   │   │   ├── PaperList.tsx   # 论文列表
│   │   │   └── CopyButton.tsx   # 批量复制按钮
│   │   └── services/
│   │       └── api.ts          # API 调用服务
│   └── package.json
└── README.md                   # 用户文档
```

## 核心工作流程

### 1. 多引擎搜索阶段
- **输入**: 用户关键词和问题
- **处理**: 并行调用多个检索引擎（arXiv、Semantic Scholar、PubMed）
- **输出**: 每个引擎返回最多 `MAX_SEARCH_RESULTS_PER_ENGINE`（默认50）篇论文
- **注意**: 引擎之间添加延迟，避免触发 API 速率限制

### 2. LLM 智能筛选阶段
- **输入**: 合并后的论文列表（可能包含多个引擎的结果）
- **处理**: 使用 Gemini 2.0 Flash 根据用户问题筛选最相关的论文
- **输出**: 最多 `MAX_FILTERED_RESULTS`（默认20）篇论文
- **特点**: 
  - 支持多来源论文（arXiv、Semantic Scholar、PubMed）的 ID 格式识别
  - 如果筛选失败，返回前 N 篇论文作为备选
  - 尝试平衡不同来源的论文数量

### 3. 翻译和关键词提取阶段
- **输入**: 筛选后的论文列表
- **处理**: 并发调用 Gemini API（最多5个并发）进行：
  - 摘要翻译（英文 → 中文）
  - 关键词提取（3-5个中文关键词）
  - 相关性评估概述（1-2句话）
- **输出**: 每篇论文包含 `abstract_zh`、`keywords`、`relevance_summary` 字段

### 4. 前端展示阶段
- 显示论文列表（标题、摘要、关键词等）
- 支持多选和批量复制链接
- 提供全选/取消全选功能

## 关键模块说明

### backend/main.py
- **职责**: FastAPI 主服务，提供 `/api/search` 接口
- **请求模型**: `SearchRequest`（keywords, question, engines）
- **响应模型**: `SearchResponse`（papers, total）
- **处理流程**: 调用各模块完成搜索 → 筛选 → 翻译的完整流程

### backend/arxiv_search.py
- **功能**: 搜索 arXiv 论文，支持所有 8 个主要学科分类
- **参数**: `category`（可选，默认为 "cs"）
- **辅助函数**: `build_arxiv_query()` - 构建查询字符串并验证分类
- **返回**: 包含 title, abstract, arxiv_id, url, pdf_url, authors, published

### backend/semantic_scholar_search.py
- **功能**: 搜索 Semantic Scholar 论文
- **特点**: 使用 Semantic Scholar API，可能需要 API 密钥
- **返回**: 包含 title, abstract, paper_id, url, authors, published

### backend/pubmed_search.py
- **功能**: 搜索 PubMed 论文
- **特点**: 主要用于生物医学领域
- **返回**: 包含 title, abstract, paper_id, url, authors, published

### backend/llm_filter.py
- **功能**: 使用 Gemini 2.0 Flash 筛选相关论文
- **输入**: 关键词、用户问题、论文列表
- **输出**: 筛选后的论文列表（最多 MAX_FILTERED_RESULTS 篇）
- **特点**:
  - 支持多来源论文 ID 格式识别
  - 包含宽松匹配机制（如果精确匹配失败）
  - 尝试平衡不同来源的论文数量

### backend/translate_extract.py
- **功能**: 翻译摘要并提取关键词
- **处理**: 
  - 将摘要翻译成中文
  - 提取 3-5 个中文关键词
  - 评估论文是否能解决用户问题
- **并发**: 使用 ThreadPoolExecutor（最多5个并发）
- **错误处理**: 如果翻译失败，使用原摘要

### backend/config.py
- **配置项**:
  - `ARXIV_CATEGORY`: arXiv 默认分类（默认 "cs"，向后兼容）
  - `ARXIV_CATEGORIES`: 所有支持的分类字典（8个主要分类及其中文名称）
  - `MAX_SEARCH_RESULTS_PER_ENGINE`: 每个引擎的最大检索数量（默认50）
  - `MAX_FILTERED_RESULTS`: LLM 筛选后最多返回的论文数量（默认20）
  - `GEMINI_MODEL`: Gemini 模型名称（默认 "gemini-2.0-flash"）
  - `GEMINI_TEMPERATURE`: 模型温度（默认0）
- **辅助函数**:
  - `is_valid_arxiv_category(category: str) -> bool`: 验证分类代码是否有效
  - `get_category_display_name(category: str) -> str`: 获取分类的中文显示名称

## 开发规范

### 代码风格
- Python 代码使用中文注释
- 函数和类使用中文文档字符串
- 变量名使用英文，但注释和文档使用中文

### 错误处理
- 各模块应捕获异常并记录日志
- 如果某个引擎搜索失败，不影响其他引擎
- LLM 调用失败时，返回备选结果（前 N 篇论文）

### 性能优化
- 多引擎搜索时添加延迟，避免触发 API 速率限制
- 翻译和关键词提取使用并发处理（最多5个并发）
- 保持论文顺序（使用索引映射）

### 环境变量
- `GEMINI_API_KEY`: Gemini API 密钥（必需）
- 环境变量文件位置：项目根目录的 `.env` 文件

## 常见任务

### 添加新的检索引擎
1. 在 `backend/` 目录创建新的搜索模块（如 `new_engine_search.py`）
2. 实现 `search_papers(keywords: str, limit: int) -> List[Dict]` 函数
3. 返回的字典必须包含 `source` 字段（标识引擎名称）
4. 在 `main.py` 中导入并集成新引擎
5. 更新 `valid_engines` 列表

### 修改检索数量限制
- 编辑 `backend/config.py` 中的 `MAX_SEARCH_RESULTS_PER_ENGINE` 和 `MAX_FILTERED_RESULTS`

### 修改 LLM 模型
- 编辑 `backend/config.py` 中的 `GEMINI_MODEL` 和 `GEMINI_TEMPERATURE`

### 修改 arXiv 分类
- 编辑 `backend/config.py` 中的 `ARXIV_CATEGORIES` 字典
- 分类代码和中文名称的映射都在此字典中定义

## 注意事项

1. **API 速率限制**: 
   - Semantic Scholar 和 PubMed API 可能有速率限制
   - 多引擎搜索时已添加延迟，但可能需要根据实际情况调整

2. **论文 ID 格式**:
   - arXiv: `2507.01376v1`（格式：YYMM.NNNNNvN）
   - Semantic Scholar: 长哈希值（40字符十六进制）
   - PubMed: 纯数字（通常8位）

3. **摘要缺失处理**:
   - Semantic Scholar 可能没有摘要
   - 系统会显示提示文本："(Semantic Scholar 数据源中未提供摘要)"

4. **LLM 筛选失败**:
   - 如果 LLM 调用失败或返回无效 ID，系统会返回前 N 篇论文作为备选
   - 这确保了系统的健壮性

5. **并发控制**:
   - 翻译和关键词提取使用最多5个并发，避免触发 Gemini API 限制
   - 可以根据实际情况调整 `ThreadPoolExecutor` 的 `max_workers` 参数

6. **启动服务**:
   - 使用 `./start.sh` 一键启动前后端
   - 后端默认端口：8001
   - 前端默认端口：3000

## 测试建议

- 测试不同关键词的搜索效果
- 测试多引擎搜索的稳定性
- 测试 LLM 筛选的准确性
- 测试翻译和关键词提取的质量
- 测试错误处理机制（API 失败、网络错误等）

