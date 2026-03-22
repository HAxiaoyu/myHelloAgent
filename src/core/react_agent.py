# src/core/react_agent.py
from .llm_client import myHelloAgentsLLM
from .tools import ToolExecutor
import re

REACT_PROMPT_TEMPLATE = """
你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程
Action: 你决定采取的行动，格式如下:
- `{{tool_name}}[{{tool_input}}]`: 调用工具
- `Finish[最终答案]`: 返回最终答案

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
    ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.verbose = verbose
        self.history = []

    def _parse_output(self, text: str):
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""

    def run_stream(
        self,
        question: str,
        on_token: callable = None,
        on_thinking: callable = None,
    ):
        """
        Run agent with streaming callbacks.

        Args:
            question: User question
            on_token: Callback for each token
            on_thinking: Callback for thinking/tool events
        Yields:
            Event dicts for WebSocket streaming
        """
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1

            tool_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tool_desc, question=question, history=history_str
            )

            messages = [{"role": "user", "content": prompt}]

            if on_thinking:
                on_thinking(f"Step {current_step}: Thinking...")

            response_text = self.llm_client.think(
                messages=messages,
                verbose=self.verbose,
                on_token=on_token,
            )

            if not response_text:
                if on_thinking:
                    on_thinking("Error: No response from LLM")
                break

            thought, action = self._parse_output(response_text)

            if not action:
                if on_thinking:
                    on_thinking("Warning: No valid action parsed")
                break

            if action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                continue

            if on_thinking:
                on_thinking(f"Action: {tool_name}[{tool_input}]")

            tool_func = self.tool_executor.getTool(name=tool_name)
            if not tool_func:
                observation = f"Error: Tool '{tool_name}' not found"
            else:
                observation = tool_func(tool_input)

            if on_thinking:
                on_thinking(f"Observation: {observation}")

            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        return None

    def run(self, question: str):
        """Legacy sync method for CLI usage."""
        return self.run_stream(question)