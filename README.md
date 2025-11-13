# arXiv 论文检索系统

基于 Gemini 2.0 Flash 的智能论文检索和筛选系统，支持关键词搜索、LLM 智能筛选和批量复制链接功能。

## 功能特性

1. **多引擎搜索**: 支持 arXiv、Semantic Scholar、PubMed 多个搜索引擎
2. **arXiv 全分类支持**: 支持搜索 arXiv 的所有 8 个主要学科分类（Physics、Mathematics、Computer Science、Quantitative Biology、Quantitative Finance、Statistics、Electrical Engineering and Systems Science、Economics）
3. **智能筛选**: 从相关度最高的论文中，使用 Gemini 2.0 Flash 筛选出最相关的论文
4. **摘要翻译**: 自动将论文摘要翻译成中文
5. **关键词提取**: 自动从摘要中提取3-5个中文关键词
6. **批量选择**: 支持多选论文，一键复制所有选中论文的链接
7. **友好界面**: 简洁美观的前端界面，支持全选/取消全选，提供独立的 arXiv 专用搜索页面

## 项目结构

```
DeepPaperSearcher/
├── start.sh              # 启动脚本（一键启动前后端）
├── backend/              # Python 后端
│   ├── main.py          # FastAPI 主服务
│   ├── arxiv_search.py  # arXiv 检索模块
│   ├── llm_filter.py    # LLM 筛选模块
│   ├── translate_extract.py  # 翻译和关键词提取模块
│   ├── config.py        # 配置文件
│   └── requirements.txt # Python 依赖
├── frontend/            # React 前端
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── MultiEngineSearch.tsx  # 多引擎搜索页面
│   │   │   └── ArxivSearch.tsx        # arXiv 专用搜索页面
│   │   ├── components/
│   │   │   ├── SearchForm.tsx         # 搜索表单
│   │   │   ├── CategorySelector.tsx   # 分类选择组件
│   │   │   ├── PaperList.tsx          # 论文列表
│   │   │   └── CopyButton.tsx         # 批量复制按钮
│   │   └── services/
│   │       └── api.ts                 # API 调用服务
│   └── package.json
└── README.md
```

## 安装和运行

### 快速启动（推荐）

使用启动脚本一键启动前后端：

```bash
./start.sh
```

脚本会自动：
- 检查依赖和环境配置
- 启动后端服务（端口 8001）
- 启动前端服务（端口 3000）
- 显示服务状态和日志位置
- 按 Ctrl+C 停止所有服务

### 手动启动

#### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件（参考 `.env.example`）：
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

4. 启动后端服务：
```bash
python main.py
```

后端服务将在 `http://localhost:8001` 启动

#### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

## 使用方法

### 多引擎搜索（默认页面）

1. 访问首页 `/`，在搜索表单中输入：
   - **关键词**: 例如 "machine learning", "neural networks"
   - **你想了解的问题**: 例如 "最新的深度学习优化方法有哪些？"
   - **选择搜索引擎**: 可以选择 arXiv、Semantic Scholar、PubMed 中的一个或多个

2. 点击"搜索论文"按钮

3. 系统会从选定的搜索引擎中搜索并筛选相关论文

### arXiv 专用搜索（支持分类选择）

1. 访问 `/arxiv` 页面，或点击导航栏的"arXiv 专用搜索"

2. 选择要搜索的 arXiv 分类：
   - **物理学** (physics)
   - **数学** (math)
   - **计算机科学** (cs)
   - **定量生物学** (q-bio)
   - **定量金融** (q-fin)
   - **统计学** (stat)
   - **电气工程与系统科学** (eess)
   - **经济学** (econ)

3. 输入搜索关键词和问题，点击"搜索论文"

4. 系统会：
   - 在指定分类下搜索相关论文
   - 使用 Gemini 2.0 Flash 筛选最相关的论文
   - 自动翻译摘要为中文并提取关键词
   - 显示筛选后的论文列表

### 查看和选择论文

- 每篇论文显示关键词（蓝色高亮）
- 显示原文摘要和中文摘要
- 显示论文ID、发布时间、作者等信息
- 勾选感兴趣的论文，可以使用"全选"快速选择
- 点击"复制链接"按钮，所有选中论文的链接会以每行一个的格式复制到剪贴板

## 配置说明

### arXiv 分类

系统支持所有 8 个 arXiv 主要分类，分类定义在 `backend/config.py` 的 `ARXIV_CATEGORIES` 中：

```python
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
```

### 修改检索和筛选数量

在 `backend/config.py` 中修改：

```python
MAX_SEARCH_RESULTS_PER_ENGINE = 50  # 每个引擎的最大检索数量
MAX_FILTERED_RESULTS = 20  # LLM 筛选后最多返回的论文数量
```

### arXiv 搜索模式

系统支持两种 arXiv 搜索模式，可在 `backend/config.py` 中配置：

```python
ARXIV_SEARCH_MODE = "oai-pmh"  # 默认使用 OAI-PMH，或 "traditional"
```

- **oai-pmh**（默认）: 使用 OAI-PMH 协议进行批量数据访问，arXiv 官方推荐用于大规模数据获取
- **traditional**: 使用 arxiv Python 库的传统 API，适合少量搜索

**注意**: OAI-PMH 模式需要安装 `sickle` 库（已包含在 requirements.txt 中）。OAI-PMH 模式不支持关键词搜索，会在获取元数据后在本地进行关键词过滤，因此可能比传统 API 慢，但更适合批量获取场景。

## 技术栈

- **后端**: Python + FastAPI + LangChain + Gemini 2.0 Flash
- **前端**: React + TypeScript + Vite
- **论文检索**: arxiv Python 库（传统 API）或 OAI-PMH 协议（批量访问）

## 注意事项

1. 需要有效的 Gemini API 密钥
2. arXiv API 是公开的，无需 API 密钥
3. 首次搜索可能需要一些时间，因为需要检索和筛选大量论文
4. 如果 LLM 筛选失败，系统会返回所有搜索结果供用户手动选择

## 许可证

MIT
# deeppapersearcher
