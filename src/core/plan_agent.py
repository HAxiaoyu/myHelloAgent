# src/core/plan_agent.py
import ast
from typing import Callable, Optional, List
from .llm_client import myHelloAgentsLLM

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的 AI 规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个 Python 列表，其中每个元素都是一个描述子任务的字符串。

问题：{question}

请严格按照以下格式输出你的计划:
```python
["步骤 1", "步骤 2", "步骤 3", ...]
```
"""

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


class Planner:
    def __init__(self, llm_client: myHelloAgentsLLM, verbose: bool = True):
        self.llm_client = llm_client
        self.verbose = verbose

    def plan(
        self,
        question: str,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> List[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]

        response_text = self.llm_client.think(
            messages=messages,
            verbose=self.verbose,
            on_token=on_token,
        ) or ""

        try:
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError):
            return []


class Executor:
    def __init__(self, llm_client: myHelloAgentsLLM, verbose: bool = True):
        self.llm_client = llm_client
        self.verbose = verbose

    def execute(
        self,
        question: str,
        plan: List[str],
        on_token: Optional[Callable[[str], None]] = None,
        on_thinking: Optional[Callable[[str], None]] = None,
    ) -> str:
        history = ""

        for i, step in enumerate(plan):
            if on_thinking:
                on_thinking(f"执行步骤 {i+1}/{len(plan)}: {step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",
                current_step=step,
            )

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(
                messages=messages,
                verbose=self.verbose,
                on_token=on_token,
            ) or ""

            history += f"步骤 {i+1}: {step}\n结果：{response_text}\n\n"

        return response_text


class PlanAndSolveAgent:
    def __init__(self, llm_client: myHelloAgentsLLM, verbose: bool = True):
        self.llm_client = llm_client
        self.verbose = verbose
        self.planner = Planner(self.llm_client, verbose=verbose)
        self.executor = Executor(self.llm_client, verbose=verbose)

    def run_stream(
        self,
        question: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_thinking: Optional[Callable[[str], None]] = None,
    ):
        """
        Run plan-and-solve agent with streaming callbacks.

        Args:
            question: User question
            on_token: Callback for each token
            on_thinking: Callback for thinking events
        Returns:
            Final answer
        """
        if on_thinking:
            on_thinking("正在生成执行计划...")

        plan = self.planner.plan(question, on_token)
        if not plan:
            if on_thinking:
                on_thinking("无法生成有效的行动计划。")
            return None

        if on_thinking:
            on_thinking(f"计划已生成，共 {len(plan)} 个步骤，开始执行...")

        final_answer = self.executor.execute(question, plan, on_token, on_thinking)
        return final_answer

    def run(self, question: str):
        """Legacy sync method for CLI usage."""
        return self.run_stream(question)