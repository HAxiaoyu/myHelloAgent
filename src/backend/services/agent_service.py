# src/backend/services/agent_service.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.llm_client import myHelloAgentsLLM
from core.react_agent import ReActAgent
from core.reflection_agent import ReflectionAgent
from core.plan_agent import PlanAndSolveAgent
from core.tools import ToolExecutor, search


class AgentService:
    def __init__(self):
        self.llm_client = myHelloAgentsLLM(verbose=False)
        self.tool_executor = ToolExecutor()
        self.tool_executor.registerTool(
            "Search",
            "网页搜索引擎，用于搜索实时信息",
            func=search
        )
        self._init_agents()

    def _init_agents(self):
        self.agents = {
            "react": ReActAgent(
                llm_client=self.llm_client,
                tool_executor=self.tool_executor,
                verbose=False
            ),
            "reflection": ReflectionAgent(
                llm_client=self.llm_client,
                verbose=False
            ),
            "plan": PlanAndSolveAgent(
                llm_client=self.llm_client,
                verbose=False
            ),
        }

    def get_agent_list(self):
        return [
            {"id": "react", "name": "ReAct Agent", "description": "思考-行动循环，支持工具调用"},
            {"id": "reflection", "name": "Reflection Agent", "description": "生成-反思-优化迭代"},
            {"id": "plan", "name": "Plan-and-Solve Agent", "description": "先规划后执行"},
        ]

    def get_tool_list(self):
        tools = []
        for name, info in self.tool_executor.tools.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "available": True
            })
        return tools

    def run_agent_stream(self, agent_type: str, question: str, on_token, on_thinking):
        """
        Run agent with streaming callbacks.

        This method is called from a thread pool, so callbacks must be thread-safe.

        Args:
            agent_type: "react", "reflection", or "plan"
            question: User question
            on_token: Thread-safe callback for each token
            on_thinking: Thread-safe callback for thinking events
        Returns:
            Final result string
        """
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # All agents now support run_stream with callbacks
        result = agent.run_stream(
            question=question,
            on_token=on_token,
            on_thinking=on_thinking,
        )

        return result