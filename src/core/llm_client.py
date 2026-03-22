# src/core/llm_client.py
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional, Callable

load_dotenv()


class myHelloAgentsLLM:
    def __init__(
        self,
        model: Optional[str] = None,
        apiKey: Optional[str] = None,
        baseUrl: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("model_id, api_key, base_url must be provided")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        verbose: bool = True,
        show_timing: bool = True,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        """
        Call LLM with optional streaming callback.

        Args:
            messages: Chat messages
            temperature: Generation randomness
            verbose: Print to console
            show_timing: Show timing stats
            on_token: Callback for each token (for WebSocket streaming)
        """
        start_time = time.time()
        if verbose:
            print(f"Calling {self.model}...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            collected_content = []
            buffer = []
            BUFFER_SIZE = 5
            first_token_time = None
            token_count = 0

            for chunk in response:
                if first_token_time is None:
                    first_token_time = time.time()
                    ttfb = first_token_time - start_time
                    if verbose and show_timing:
                        print(f"\nTTFB: {ttfb:.2f}s")
                    if verbose:
                        print("Response:")

                content = chunk.choices[0].delta.content or ""
                if content:
                    buffer.append(content)
                    token_count += 1
                    collected_content.append(content)

                    # Callback for WebSocket streaming
                    if on_token:
                        on_token(content)

                    if len(buffer) >= BUFFER_SIZE:
                        if verbose:
                            print(''.join(buffer), end='', flush=True)
                        buffer = []

            if buffer and verbose:
                print(''.join(buffer), end='', flush=True)

            if verbose:
                print()

            total_time = time.time() - start_time
            if verbose and show_timing:
                tokens_per_sec = token_count / total_time if total_time > 0 else 0
                print(f"Time: {total_time:.2f}s | {token_count} tokens | {tokens_per_sec:.1f} tokens/s")

            return "".join(collected_content)

        except Exception as e:
            print(f"LLM API error: {e}")
            return None