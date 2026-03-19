from typing import Dict, Any
from Memory import Memory


# 1. 初始执行提示词
INITIAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。
"""

# 2. 反思提示词
REFLECT_PROMPT_TEMPLATE = """
你是一位极其严格的代码评审专家和资深算法工程师，对代码的性能有极致的要求。
你的任务是审查以下Python代码，并专注于找出其在**算法效率**上的主要瓶颈。

# 原始任务:
{task}

# 待审查的代码:
```python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种**算法上更优**的解决方案来显著提升性能。
如果存在，请清晰地指出当前算法的不足，并提出具体的、可行的改进算法建议（例如，使用筛法替代试除法）。
如果代码在算法层面已经达到最优，才能回答“无需改进”。

请直接输出你的反馈，不要包含任何额外的解释。
"""

# 3. 优化提示词
REFINE_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务:
{task}

# 你上一轮尝试的代码:
{last_code_attempt}

# 评审员的反馈:
{feedback}

请根据评审员的反馈，生成一个优化后的新版本代码。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。
请直接输出优化后的代码，不要包含任何额外的解释。
"""


class ReflectionAgent:
    def __init__(self, llm_client, max_iterations=3, verbose: bool = True):
        """
        初始化反思智能体。
        
        参数:
            llm_client: LLM 客户端实例
            max_iterations: 最大迭代次数
            verbose: 是否输出详细过程（默认 True）
        """
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations
        self.verbose = verbose

    def run(self, task: str):
        if self.verbose:
            print(f"\n--- 开始处理任务 ---\n任务：{task}")

        # --- 1. 初始执行 ---
        if self.verbose:
            print("\n--- 正在进行初始尝试 ---")
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)

        # --- 2. 迭代循环：反思与优化 ---
        for i in range(self.max_iterations):
            if self.verbose:
                print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            if self.verbose:
                print("\n-> 正在进行反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            # b. 检查是否需要停止
            if "无需改进" in feedback or "no need for improvement" in feedback.lower():
                if self.verbose:
                    print("\n✅ 反思认为代码已无需改进，任务完成。")
                break

            # c. 优化
            if self.verbose:
                print("\n-> 正在进行优化...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task, last_code_attempt=last_code, feedback=feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)

        final_code = self.memory.get_last_execution()
        if self.verbose:
            print(f"\n--- 任务完成 ---\n最终生成的代码:\n{final_code}")
        return final_code

    def _get_llm_response(self, prompt: str) -> str:
        """一个辅助方法，用于调用 LLM 并获取完整的流式响应。"""
        messages = [{"role": "user", "content": prompt}]
        # 确保能处理生成器可能返回 None 的情况
        response_text = self.llm_client.think(
            messages=messages, 
            verbose=self.verbose,
            show_timing=self.verbose,
        ) or ""
        return response_text


if __name__ == "__main__":
    from myHelloAgentsLLM import myHelloAgentsLLM

    try:
        llm_client = myHelloAgentsLLM()
    except Exception as e:
        print(f"初始化 LLM 客户端时出错：{e}")
        exit()

    # 2. 初始化 Reflection 智能体，设置最多迭代 2 轮
    agent = ReflectionAgent(llm_client, max_iterations=2, verbose=True)

    # 3. 定义任务并运行智能体
    task = "编写一个 Python 函数，找出 1 到 n 之间所有的素数 (prime numbers)。"
    agent.run(task)
