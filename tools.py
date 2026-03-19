"""
一个良好定义的工具应包含以下三个核心要素：
1. 名称 (Name)： 一个简洁、唯一的标识符，供智能体在 Action 中调用，例如 Search。
2. 描述 (Description)： 一段清晰的自然语言描述，说明这个工具的用途。这是整个机制中最关键的部分，因为大语言模型会依赖这段描述来判断何时使用哪个工具。
3. 执行逻辑 (Execution Logic)： 真正执行任务的函数或方法。
"""

from serpapi import SerpApiClient
from typing import Optional, Dict, Any, Callable

from dotenv import load_dotenv
import os

load_dotenv()


class ToolExecutor:
    def __init__(self) -> None:
        """初始化工具执行器"""
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: Callable):
        """向工具箱中注册一个新工具。"""
        if name in self.tools:
            print(f"警告:工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> Callable[..., Any] | None:
        """获取名称获取工具可用函数"""
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """获取所有可用工具的描述"""
        return "\n".join(
            [f"- {name}: {info['description']}" for name, info in self.tools.items()]
        )


def search(query: str) -> str:
    """
    一个基于SerpApi的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        serp_api_key: Optional[str] = os.getenv("SERPAPI_API_KEY")
        if not serp_api_key:
            return "错误:SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": serp_api_key,
            "gl": "us",
            "hl": "zh-cn",
        }

        client = SerpApiClient(params_dict=params)
        results = client.get_dict()
        # 智能解析:优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


if __name__ == "__main__":

    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)

    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4. 智能体的Action调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误:未找到名为 '{tool_name}' 的工具。")
