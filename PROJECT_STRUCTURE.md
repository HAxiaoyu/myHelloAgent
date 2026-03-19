# 📁 项目结构

```
myHelloAgent/
├── 📄 README.md                  # 项目说明文档
├── 📄 PROJECT_STRUCTURE.md       # 项目结构说明（本文件）
├── 📄 pyproject.toml             # Python 项目配置（依赖管理）
├── 📄 uv.lock                    # 依赖锁定文件
├── 📄 .env                       # 环境变量配置（需自行创建）
├── 📄 .env.example               # 环境变量示例
│
├── 🐍 myHelloAgentsLLM.py        # LLM 客户端核心
├── 🐍 tools.py                   # 工具注册与执行器
├── 🐍 Memory.py                  # 短期记忆模块
│
├── 🐍 ReActAgent.py              # ReAct 智能体实现
├── 🐍 Reflection.py              # Reflection 智能体实现
├── 🐍 Plan_and_solve.py          # Plan-and-Solve 智能体实现
│
└── 📂 __pycache__/               # Python 字节码缓存（可忽略）
```

---

## 📂 文件说明

### 📖 文档文件

| 文件 | 说明 |
|-----|------|
| `README.md` | 项目主文档，包含简介、功能、架构图、快速开始指南 |
| `PROJECT_STRUCTURE.md` | 项目结构说明，详解每个文件的作用和依赖关系 |
| `.env.example` | 环境变量模板（实际使用时需复制为 `.env`） |

---

### ⚙️ 配置文件

| 文件 | 说明 |
|-----|------|
| `pyproject.toml` | Python 项目配置文件，定义项目名称、版本、依赖 |
| `uv.lock` | 依赖版本锁定文件（由 `uv` 包管理器生成） |
| `.env` | **敏感文件**，包含 API Key 等配置（不应提交到 Git） |

---

### 🧠 核心模块

#### 1. `myHelloAgentsLLM.py` — LLM 客户端

**职责**：封装 LLM API 调用，提供统一的 `think()` 接口

**核心功能**：
- ✅ 流式输出优化（批量输出，减少 95% I/O）
- ✅ 性能监控（TTFB、生成速度）
- ✅ verbose 模式控制
- ✅ 环境变量加载

**对外接口**：
```python
class myHelloAgentsLLM:
    def think(messages, temperature=0, verbose=True, show_timing=True) -> str
```

**依赖**：
- `openai` SDK
- `python-dotenv`（环境变量）

---

#### 2. `tools.py` — 工具系统

**职责**：管理可用工具，提供注册、查询、执行功能

**核心功能**：
- ✅ 工具注册表（`ToolExecutor`）
- ✅ 工具描述生成（供 LLM 理解）
- ✅ SerpApi 搜索引擎（`search` 函数）

**对外接口**：
```python
class ToolExecutor:
    def registerTool(name, description, func)
    def getTool(name) -> Callable
    def getAvailableTools() -> str

def search(query: str) -> str
```

**依赖**：
- `google-search-results`（SerpApi 客户端）
- `os`（环境变量读取）

---

#### 3. `Memory.py` — 记忆模块

**职责**：存储智能体的短期记忆（执行轨迹）

**核心功能**：
- ✅ 类型化记录（execution / reflection）
- ✅ 轨迹查询
- ✅ 最近执行查询

**对外接口**：
```python
class Memory:
    def add_record(record_type, content)
    def get_trajectory() -> str
    def get_last_execution() -> str
```

**依赖**：无（纯 Python 实现）

---

### 🤖 Agent 实现

#### 4. `ReActAgent.py` — ReAct 智能体

**范式**：Reason + Act 循环

**核心流程**：
```
Thought → Action → Observation → 循环...
```

**依赖模块**：
- `myHelloAgentsLLM`（LLM 调用）
- `tools.ToolExecutor`（工具执行）

**关键方法**：
```python
class ReActAgent:
    def run(question) -> str
    def _parse_output(text) -> (thought, action)
    def _parse_action(action_text) -> (tool_name, tool_input)
```

**输出控制**：
- `verbose=True`：输出思考、行动、观察全过程
- `verbose=False`：静默执行

---

#### 5. `Reflection.py` — Reflection 智能体

**范式**：生成 → 反思 → 优化 迭代

**核心流程**：
```
初始代码 → 代码评审 → 优化代码 → 循环...
```

**依赖模块**：
- `myHelloAgentsLLM`（LLM 调用）
- `Memory`（存储执行轨迹）

**关键方法**：
```python
class ReflectionAgent:
    def run(task) -> str
    def _get_llm_response(prompt) -> str
```

**提示词模板**：
- `INITIAL_PROMPT_TEMPLATE`：初始生成
- `REFLECT_PROMPT_TEMPLATE`：代码评审
- `REFINE_PROMPT_TEMPLATE`：优化代码

---

#### 6. `Plan_and_solve.py` — Plan-and-Solve 智能体

**范式**：先规划，后执行

**核心流程**：
```
问题 → 分解计划 → 逐步执行 → 汇总答案
```

**依赖模块**：
- `myHelloAgentsLLM`（LLM 调用）
- `ast`（安全解析列表）

**内部类**：
- `Planner`：生成任务计划
- `Executor`：执行每个子任务
- `PlanAndSolveAgent`：协调者（组合 Planner + Executor）

**关键方法**：
```python
class Planner:
    def plan(question) -> list[str]

class Executor:
    def execute(question, plan) -> str

class PlanAndSolveAgent:
    def run(question) -> str
```

---

## 🔗 依赖关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent 层（3 个智能体）                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ ReActAgent  │  │ Reflection   │  │ PlanAndSolveAgent   │   │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────┘   │
└─────────┼────────────────┼─────────────────────┼──────────────┘
          │                │                     │
          └────────────────┼─────────────────────┘
                           │
                  ┌────────▼────────┐
                  │ myHelloAgentsLLM │ ←───┐ 核心 LLM 客户端
                  └────────┬────────┘     │
                           │              │
         ┌─────────────────┼──────────────┤
         │                 │              │
┌────────▼────────┐ ┌─────▼──────┐ ┌─────▼────────┐
│  tools.py       │ │  Memory.py │ │  外部 API     │
│  (工具执行器)    │ │ (短期记忆)  │ │  (SerpApi)   │
└─────────────────┘ └────────────┘ └──────────────┘
```

---

## 📦 依赖包说明

| 包名 | 版本 | 用途 |
|-----|------|------|
| `openai` | >=2.29.0 | LLM API 调用（兼容 DashScope） |
| `python-dotenv` | >=1.2.2 | 环境变量管理（`.env` 文件加载） |
| `google-search-results` | >=2.4.2 | SerpApi 搜索引擎客户端 |

---

## 🔒 敏感文件说明

### `.env` 文件（不应提交到 Git）

```bash
# .env
LLM_API_KEY="sk-..."           # LLM API 密钥
LLM_MODEL_ID="qwen3.5-plus"    # 模型名称
LLM_BASE_URL="https://..."     # LLM 服务地址
LLM_TIMEOUT=120                # 超时时间（秒）
SERPAPI_API_KEY="..."          # SerpApi 密钥
```

### `.gitignore` 建议配置

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
env/

# 敏感信息
.env
*.key
*.secret

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

## 🚀 模块调用示例

### 1. 单独使用 LLM 客户端

```python
from myHelloAgentsLLM import myHelloAgentsLLM

llm = myHelloAgentsLLM()
messages = [{"role": "user", "content": "Hello"}]
response = llm.think(messages, verbose=True, show_timing=True)
```

---

### 2. 使用 ReAct 智能体

```python
from ReActAgent import ReActAgent
from tools import ToolExecutor, search
from myHelloAgentsLLM import myHelloAgentsLLM

llm = myHelloAgentsLLM()
tool_executor = ToolExecutor()
tool_executor.registerTool("Search", "网页搜索引擎", func=search)

agent = ReActAgent(llm_client=llm, tool_executor=tool_executor, max_steps=5, verbose=True)
answer = agent.run("华为最新的手机是哪一款？")
```

---

### 3. 使用 Reflection 智能体

```python
from Reflection import ReflectionAgent
from myHelloAgentsLLM import myHelloAgentsLLM

llm = myHelloAgentsLLM()
agent = ReflectionAgent(llm_client=llm, max_iterations=3, verbose=True)
code = agent.run("编写一个函数，找出 1 到 n 之间的所有素数")
```

---

### 4. 使用 Plan-and-Solve 智能体

```python
from Plan_and_solve import PlanAndSolveAgent
from myHelloAgentsLLM import myHelloAgentsLLM

llm = myHelloAgentsLLM()
agent = PlanAndSolveAgent(llm_client=llm, verbose=True)
answer = agent.run("一个水果店周一卖出 15 个苹果，周二卖出的是周一的两倍，周三比周二少 5 个，三天总共卖出多少？")
```

---

## 📊 代码行数统计

| 文件 | 行数 | 说明 |
|-----|------|------|
| `myHelloAgentsLLM.py` | ~90 | LLM 客户端（核心） |
| `tools.py` | ~110 | 工具系统 + SerpApi 封装 |
| `Memory.py` | ~45 | 短期记忆模块 |
| `ReActAgent.py` | ~160 | ReAct 智能体 |
| `Reflection.py` | ~140 | Reflection 智能体 |
| `Plan_and_solve.py` | ~155 | Plan-and-Solve 智能体 |
| **总计** | **~700** | 核心代码约 700 行 |

---

## 🎯 扩展建议

### 新增 Agent
1. 在根目录创建 `NewAgent.py`
2. 导入 `myHelloAgentsLLM`
3. 实现 `run()` 方法作为入口
4. 添加 `verbose` 参数支持

### 新增工具
1. 在 `tools.py` 中定义新函数
2. 函数签名：`def tool_name(param: str) -> str`
3. 使用 `tool_executor.registerTool()` 注册

### 新增记忆类型
1. 修改 `Memory.py` 的 `add_record()` 方法
2. 添加新的记录类型（如 `planning`、`execution_result`）
3. 实现对应的查询方法

---

<div align="center">

**📂 清晰的 project structure 是良好代码组织的开始**

</div>
