from myHelloAgentsLLM import myHelloAgentsLLM
import os
import ast
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的 AI 规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个 Python 列表，其中每个元素都是一个描述子任务的字符串。

问题：{question}

请严格按照以下格式输出你的计划，```python 与```作为前后缀是必要的:
```python
["步骤 1", "步骤 2", "步骤 3", ...]
```
"""


class Planner:
    def __init__(self, llm_client, verbose: bool = True):
        """
        初始化规划器。
        
        参数:
            llm_client: LLM 客户端实例
            verbose: 是否输出详细信息（默认 True）
        """
        self.llm_client = llm_client
        self.verbose = verbose

    def plan(self, question: str) -> list[str]:
        """
        根据用户问题生成一个行动计划。并且返回一个列表，方便后续处理
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        # 为了生成计划，我们构建一个简单的消息列表
        messages = [{"role": "user", "content": prompt}]

        if self.verbose:
            print("--- 正在生成计划 ---")
        # 使用流式输出来获取完整的计划
        response_text = self.llm_client.think(
            messages=messages, 
            verbose=self.verbose,
            show_timing=self.verbose,
        ) or ""

        if self.verbose:
            print(f"\n✅ 计划已生成:\n{response_text}")

        # 解析 LLM 输出的列表字符串
        try:
            # 找到```python 和```之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用 ast.literal_eval 来安全地执行字符串，将其转换为 Python 列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错：{e}")
            print(f"原始响应：{response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误：{e}")
            return []


EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的 AI 执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


class Executor:
    def __init__(self, llm_client, verbose: bool = True):
        """
        初始化执行器。
        
        参数:
            llm_client: LLM 客户端实例
            verbose: 是否输出详细信息（默认 True）
        """
        self.llm_client = llm_client
        self.verbose = verbose

    def execute(self, question: str, plan: list[str]) -> str:
        """
        根据计划，逐步执行并解决问题。
        """
        history = ""  # 用于存储历史步骤和结果的字符串

        if self.verbose:
            print("\n--- 正在执行计划 ---")

        for i, step in enumerate(plan):
            if self.verbose:
                print(f"\n-> 正在执行步骤 {i+1}/{len(plan)}: {step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",  # 如果是第一步，则历史为空
                current_step=step,
            )

            messages = [{"role": "user", "content": prompt}]

            response_text = self.llm_client.think(
                messages=messages, 
                verbose=self.verbose,
                show_timing=self.verbose,
            ) or ""

            # 更新历史记录，为下一步做准备
            history += f"步骤 {i+1}: {step}\n结果：{response_text}\n\n"

            if self.verbose:
                print(f"✅ 步骤 {i+1} 已完成，结果：{response_text}")

        # 循环结束后，最后一步的响应就是最终答案
        final_answer = response_text
        return final_answer


class PlanAndSolveAgent:
    """组合优于继承的原则。它本身不包含复杂的逻辑，而是作为一个协调者 (Orchestrator)，清晰地调用其内部组件来完成任务。"""

    def __init__(self, llm_client: myHelloAgentsLLM, verbose: bool = True):
        """
        初始化 PlanAndSolve 智能体。
        
        参数:
            llm_client: LLM 客户端实例
            verbose: 是否输出详细信息（默认 True）
        """
        self.llm_client = llm_client
        self.verbose = verbose
        self.planner = Planner(self.llm_client, verbose=verbose)
        self.executor = Executor(self.llm_client, verbose=verbose)

    def run(self, question: str):
        if self.verbose:
            print(f"\n--- 开始处理问题 ---\n问题：{question}")
        plan = self.planner.plan(question)
        if not plan:
            if self.verbose:
                print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return
        final_answer = self.executor.execute(question, plan)
        if self.verbose:
            print(f"\n--- 任务完成 ---\n最终答案：{final_answer}")


if __name__ == "__main__":
    try:
        llm_client = myHelloAgentsLLM()
        agent = PlanAndSolveAgent(llm_client)
        question = "一个水果店周一卖出了 15 个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了 5 个。请问这三天总共卖出了多少个苹果？"
        agent.run(question)
    except ValueError as e:
        print(e)
