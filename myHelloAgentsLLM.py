import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# 加载 .env 文件中的环境变量
load_dotenv()

class myHelloAgentsLLM:

    def __init__(
        self,
        model: Optional[str] = None,
        apiKey: Optional[str] = None,
        baseUrl: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0,
        verbose: bool = True,
        show_timing: bool = True,
    ) -> Optional[str]:
        """
        调用大语言模型进行思考，并返回其响应。
        
        参数:
            messages: 对话消息列表
            temperature: 温度参数，控制生成随机性
            verbose: 是否输出详细信息（默认 True）
            show_timing: 是否显示性能统计（默认 True）
        """
        start_time = time.time()
        if verbose:
            print(f"🧠 正在调用 {self.model} 模型...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,  # type: ignore
                messages=messages,  # type: ignore
                temperature=temperature,
                stream=True,
            )

            # 处理流式响应 - 优化版
            collected_content = []
            buffer = []
            BUFFER_SIZE = 5  # 累积 5 个 token 后输出，减少 I/O 次数
            first_token_time = None
            token_count = 0

            for chunk in response:
                # 记录首字时间（TTFB - Time To First Byte）
                if first_token_time is None:
                    first_token_time = time.time()
                    ttfb = first_token_time - start_time
                    if verbose and show_timing:
                        print(f"\n⏱️  首字延迟 (TTFB): {ttfb:.2f}s")
                    if verbose:
                        print("✅ 大语言模型响应成功:")

                content = chunk.choices[0].delta.content or ""
                if content:
                    buffer.append(content)
                    token_count += 1
                    collected_content.append(content)

                    # 批量输出：累积到 BUFFER_SIZE 个 token 后打印
                    if len(buffer) >= BUFFER_SIZE:
                        print(''.join(buffer), end='', flush=True)
                        buffer = []

            # 输出剩余 buffer
            if buffer:
                print(''.join(buffer), end='', flush=True)
            
            print()  # 在流式输出结束后换行
            
            # 显示性能统计
            total_time = time.time() - start_time
            if verbose and show_timing:
                tokens_per_sec = token_count / total_time if total_time > 0 else 0
                print(f"⏱️  总耗时：{total_time:.2f}s | 生成 {token_count} tokens | 速度：{tokens_per_sec:.1f} tokens/s")
            
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用 LLM API 时发生错误：{e}")
            return None


# --- 客户端使用示例 ---
if __name__ == "__main__":
    try:
        llmClient = myHelloAgentsLLM()

        exampleMessages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes Python code.",
            },
            {"role": "user", "content": "写一个快速排序算法"},
        ]

        print("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n--- 完整模型响应 ---")
            print(responseText)

    except ValueError as e:
        print(e)
