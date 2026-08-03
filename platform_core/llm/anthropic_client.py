"""Anthropic Claude wrapper for the RAG generation step.

Thin, synchronous single-turn client. Reads model + key from settings. Only the
'anthropic' provider is wired here; 'bedrock' (for the HIPAA/AWS-BAA path) is
deferred and raises at construction. See docs/DECISIONS.md ADR-008.
"""
from __future__ import annotations

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger

log = get_logger(__name__)

# Timeout for Anthropic API calls (seconds)
ANTHROPIC_TIMEOUT = 30.0


class LLMConfigError(RuntimeError):
    """Raised when the LLM provider isn't usable (missing key / unsupported provider)."""


def is_llm_configured() -> bool:
    """True if an LLMClient can be constructed (anthropic provider + key present)."""
    settings = get_settings()
    return settings.llm_provider == "anthropic" and bool(settings.anthropic_api_key)


class LLMClient:
    """Single-turn Claude client over the Anthropic Messages API."""

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        if settings.llm_provider != "anthropic":
            raise LLMConfigError(
                f"llm_provider={settings.llm_provider!r} not supported yet; use 'anthropic'"
            )
        if not settings.anthropic_api_key:
            raise LLMConfigError("ANTHROPIC_API_KEY is not set")
        # Imported lazily so the anthropic dep is only required when the LLM runs.
        import anthropic

        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = model or settings.anthropic_model_sonnet

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 1024,
        temperature: float | None = None,
    ) -> str:
        """Run a single-turn completion and return the assistant's text.

        temperature is omitted unless explicitly set — newer models (e.g.
        claude-sonnet-5) reject the now-deprecated temperature parameter.
        """
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            timeout=ANTHROPIC_TIMEOUT,
        )
        if temperature is not None:
            kwargs["temperature"] = temperature
        resp = self._client.messages.create(**kwargs)
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
        log.info(
            "llm_complete",
            model=self.model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
        )
        return text.strip()
