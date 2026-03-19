from myHelloAgentsLLM import myHelloAgentsLLM
from tools import ToolExecutor

import re

# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""


class ReActAgent:
    def __init__(
        self,
        llm_client: myHelloAgentsLLM,
        tool_executor: ToolExecutor,
        max_steps: int = 5,
        verbose: bool = True,
    ) -> None:
        """
        初始化 ReAct 智能体。
        
        参数:
            llm_client: LLM 客户端实例
            tool_executor: 工具执行器实例
            max_steps: 最大思考步数
            verbose: 是否输出详细过程（默认 True）
        """
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.verbose = verbose
        self.history = []

    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。"""
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """
        解析Action字符串，提取工具名称和输入。
        例如从Search[罗技鼠标]中提取出工具名称“Search”和搜索内容“罗技鼠标”
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _parse_action_input(self, action_text: str):
        """Finish 场景提取答案"""
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""

    def run(self, question: str):
        """
        运行 ReAct 智能体来回答一个问题。
        run 方法是智能体的入口。它的 while 循环构成了 ReAct 范式的主体，max_steps 参数则是一个重要的安全阀，防止智能体陷入无限循环而耗尽资源。
        """
        self.history = []  # 每次运行时重置历史记录
        current_step: int = 0

        while current_step < self.max_steps:
            current_step += 1
            if self.verbose:
                print(f"--- 第 {current_step} 步 ---")

            tool_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tool_desc, question=question, history=history_str
            )

            # 2. 调用 LLM 进行思考
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(
                messages=messages, 
                verbose=self.verbose,
                show_timing=self.verbose,
            )

            # 3. 解析 LLM 输出
            if not response_text:
                if self.verbose:
                    print("错误:LLM 未能返回有效响应。")
                break

            thought, action = self._parse_output(response_text)
            if thought and self.verbose:
                print(f"思考：{thought}")
            if not action:
                if self.verbose:
                    print("警告：未能解析出有效的 Action，流程终止。")
                break

            # 4. 执行 Action
            if action.startswith("Finish"):
                # 如果是 Finish 指令，提取最终答案并结束
                final_answer = self._parse_action_input(action)
                if self.verbose:
                    print(f"🎉 最终答案：{final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # ... 处理无效 Action 格式 ...
                continue
            if self.verbose:
                print(f"🎬 行动：{tool_name}[{tool_input}]")

            tool_func = self.tool_executor.getTool(name=tool_name)
            if not tool_func:
                observation = f"错误：未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_func(tool_input)  # 调用实际获取的工具

            # 5. 将获取的信息添加到历史信息中，为下一轮循环提供上下文，形成闭环
            if self.verbose:
                print(f"👀 观察：{observation}")
            # 将本轮的 Action 和 Observation 添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")
        # 循环结束
        if self.verbose:
            print("已达到最大步数，流程终止。")
        return None


if __name__ == "__main__":
    from tools import search

    llm = myHelloAgentsLLM()
    tool_executor = ToolExecutor()
    search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tool_executor.registerTool("Search", search_desc, func=search)
    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor, verbose=True)
    question = "罗技鼠标最好的是哪一款？它的主要卖点是什么？"
    agent.run(question)
