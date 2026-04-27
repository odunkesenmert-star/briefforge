"""
Thin Claude client wrapper used by FastAPI endpoints.
"""

import os
from typing import Dict, List, Optional

from anthropic import Anthropic


class ClaudeClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def complete(
        self,
        prompt: str,
        max_tokens: int = 1200,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Execute a Claude completion; falls back to deterministic placeholder
        if API key is not configured so local development can proceed.
        """
        if self.client is None:
            return (
                "ANTHROPIC_API_KEY is not set. "
                "This is a local fallback response.\n\n"
                f"Prompt preview:\n{prompt[:400]}"
            )

        conversation_history = history or []
        normalized_history = []
        for item in conversation_history:
            role = item.get("role", "").strip().lower()
            content = item.get("content", "")
            if role not in {"user", "assistant"}:
                continue
            normalized_history.append({"role": role, "content": content})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[*normalized_history, {"role": "user", "content": prompt}],
        )

        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts).strip()
