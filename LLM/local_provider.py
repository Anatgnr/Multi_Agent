"""
Simple adapter to expose a callable LLM (pipeline) as an object with a .call(...) method
that returns a dict containing an 'output' key so it can be used with creai's expectations.
"""
from typing import Any, List


class LocalLLM:
    def __init__(self, gen_fn, provider: str = "local"):
        """gen_fn should be a callable that accepts a prompt string and returns generated text."""
        self._gen = gen_fn
        self._provider = provider

    def _messages_to_prompt(self, messages: Any) -> str:
        # messages can be a list of dicts like [{'role': 'user', 'content': '...'}, ...]
        if isinstance(messages, list):
            parts = []
            for m in messages:
                if isinstance(m, dict) and 'content' in m:
                    parts.append(m['content'])
                else:
                    parts.append(str(m))
            return "\n".join(parts)
        return str(messages)

    def call(self, messages: Any, **kwargs) -> dict:
        """Return a dict with an 'output' key (compatible with creai expectations).

        The adapter is intentionally simple: it concatenates message contents and calls
        the underlying generator function.
        """
        prompt = self._messages_to_prompt(messages)
        text = self._gen(prompt)
        return {"output": text}
