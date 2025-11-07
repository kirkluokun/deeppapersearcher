# arXiv 论文检索系统

基于 Gemini 2.0 Flash 的智能论文检索和筛选系统，支持关键词搜索、LLM 智能筛选和批量复制链接功能。

## 功能特性

1. **关键词搜索**: 输入关键词搜索 arXiv 上的计算机科学论文（cs 分类）
2. **智能筛选**: 从相关度最高的30篇论文中，使用 Gemini 2.0 Flash 筛选出最多15篇最相关的论文
3. **摘要翻译**: 自动将论文摘要翻译成英文
4. **关键词提取**: 自动从摘要中提取3-5个关键词
5. **批量选择**: 支持多选论文，一键复制所有选中论文的链接
6. **友好界面**: 简洁美观的前端界面，支持全选/取消全选

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
│   │   ├── components/
│   │   │   ├── SearchForm.tsx
│   │   │   ├── PaperList.tsx
│   │   │   └── CopyButton.tsx
│   │   └── services/
│   │       └── api.ts
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

1. 在搜索表单中输入：
   - **关键词**: 例如 "machine learning", "neural networks"
   - **你想了解的问题**: 例如 "最新的深度学习优化方法有哪些？"

2. 点击"搜索论文"按钮

3. 系统会：
   - 在 arXiv 上搜索相关论文（相关度最高的30篇）
   - 使用 Gemini 2.0 Flash 从这30篇中筛选出最多15篇最相关的论文
   - 自动翻译摘要为英文并提取关键词
   - 显示筛选后的论文列表（最多15篇）

4. 查看论文信息：
   - 每篇论文显示关键词（蓝色高亮）
   - 显示原文摘要和英文摘要
   - 显示论文ID、发布时间、作者等信息

5. 选择论文：
   - 勾选你感兴趣的论文
   - 可以使用"全选"快速选择所有论文

6. 复制链接：
   - 点击"复制链接"按钮
   - 所有选中论文的链接会以每行一个的格式复制到剪贴板

## 配置说明

### 修改分类限制

编辑 `backend/config.py` 文件，可以修改 `ARXIV_CATEGORY` 来限制其他分类：

```python
ARXIV_CATEGORY = "cs"  # 目前仅支持 cs（计算机科学）
```

未来可以在 `AVAILABLE_CATEGORIES` 中添加更多分类。

### 修改检索和筛选数量

在 `backend/config.py` 中修改：

```python
MAX_SEARCH_RESULTS = 30  # 最大检索数量（相关度最高的30篇）
MAX_FILTERED_RESULTS = 15  # LLM 筛选后最多返回的论文数量
```

## 技术栈

- **后端**: Python + FastAPI + LangChain + Gemini 2.0 Flash
- **前端**: React + TypeScript + Vite
- **论文检索**: arxiv Python 库

## 注意事项

1. 需要有效的 Gemini API 密钥
2. arXiv API 是公开的，无需 API 密钥
3. 首次搜索可能需要一些时间，因为需要检索和筛选大量论文
4. 如果 LLM 筛选失败，系统会返回所有搜索结果供用户手动选择

## 许可证

MIT
# deeppapersearcher
