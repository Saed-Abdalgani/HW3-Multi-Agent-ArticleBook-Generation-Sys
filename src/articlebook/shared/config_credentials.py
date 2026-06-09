"""Resolve LLM API keys from environment by provider (OpenAI vs Google Gemini)."""

from __future__ import annotations

import os


def _norm_provider(provider: str) -> str:
    return str(provider or "openai").strip().casefold()


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        s = v.strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _env_chain(*names: str) -> list[str]:
    raw: list[str] = []
    for n in names:
        v = os.getenv(n)
        if v:
            raw.append(v)
    return _dedupe_preserve_order(raw)


def parse_llm_routes_from_env() -> list[dict[str, str]] | None:
    """Parse ``ARTICLEBOOK_LLM_ROUTES`` or the simple ``*_KEY_SUFFIX`` triple (see below).

    **Explicit routes:** ``api_key|model_id`` per slot, slots separated by ``;``::

        sk-or-v1-...|openrouter/openai/gpt-4o;gsk_...|groq/llama-3.3-70b-versatile;nvapi-...|nvidia_nim/...

    **Shortcut (no pipes):** set all three of ``ARTICLEBOOK_OPENROUTER_KEY_SUFFIX``,
    ``ARTICLEBOOK_GROQ_KEY_SUFFIX``, and ``ARTICLEBOOK_NVIDIA_KEY_SUFFIX`` to the secret
    part *after* the usual prefix (``sk-or-v1-``, ``gsk_``, ``nvapi-``). If a value already
    includes its prefix, it is left unchanged. Models default to a sensible triple; override
    with ``ARTICLEBOOK_ROUTE_MODELS`` (three ids separated by ``;``).

    The first slot is always tried first on each LLM call; on rate-limit style errors
    the gatekeeper advances to the next ``key|model`` pair.

    ``MODEL_NAME`` is ignored when routes are active (explicit or suffix-built).
    """
    raw = os.getenv("ARTICLEBOOK_LLM_ROUTES", "").strip()
    if raw:
        out: list[dict[str, str]] = []
        for part in raw.split(";"):
            part = part.strip()
            if not part:
                continue
            if "|" not in part:
                raise ValueError(
                    "ARTICLEBOOK_LLM_ROUTES: each segment must be 'YOUR_API_KEY|litellm_model_id' "
                    "(separate failover slots with ';'). Example: "
                    "sk-or-v1-xxx|openrouter/openai/gpt-4o;gsk_yyy|groq/llama-3.3-70b-versatile"
                )
            key, model = part.split("|", 1)
            key, model = key.strip(), model.strip()
            if not key or not model:
                raise ValueError("ARTICLEBOOK_LLM_ROUTES: empty API key or model in a segment")
            out.append({"api_key": key, "model": model})
        return out or None
    return _llm_routes_from_key_suffixes()


_DEFAULT_TRIPLE_MODELS = (
    "nvidia_nim/meta/llama-3.1-70b-instruct;openrouter/openai/gpt-4o;groq/llama-3.3-70b-versatile"
)


def _full_openrouter_key(secret: str) -> str:
    s = secret.strip()
    if s.startswith("sk-or-v1-"):
        return s
    return f"sk-or-v1-{s}"


def _full_groq_key(secret: str) -> str:
    s = secret.strip()
    if s.startswith("gsk_"):
        return s
    return f"gsk_{s}"


def _full_nvidia_key(secret: str) -> str:
    s = secret.strip()
    if s.startswith("nvapi-"):
        return s
    return f"nvapi-{s}"


def _llm_routes_from_key_suffixes() -> list[dict[str, str]] | None:
    or_s = os.getenv("ARTICLEBOOK_OPENROUTER_KEY_SUFFIX", "").strip()
    gq_s = os.getenv("ARTICLEBOOK_GROQ_KEY_SUFFIX", "").strip()
    nv_s = os.getenv("ARTICLEBOOK_NVIDIA_KEY_SUFFIX", "").strip()
    if not (or_s and gq_s and nv_s):
        return None
    models_raw = os.getenv("ARTICLEBOOK_ROUTE_MODELS", _DEFAULT_TRIPLE_MODELS).strip()
    parts = [p.strip() for p in models_raw.split(";") if p.strip()]
    if len(parts) != 3:
        raise ValueError(
            "ARTICLEBOOK_ROUTE_MODELS must list exactly 3 LiteLLM model ids separated by ';' "
            "(NVIDIA slot, OpenRouter slot, Groq slot)."
        )
    return [
        {"api_key": _full_nvidia_key(nv_s), "model": parts[0]},
        {"api_key": _full_openrouter_key(or_s), "model": parts[1]},
        {"api_key": _full_groq_key(gq_s), "model": parts[2]},
    ]


def _resolve_llm_api_keys_plain(provider: str) -> list[str]:
    """Keys only from legacy env vars (no ``ARTICLEBOOK_LLM_ROUTES``)."""
    p = _norm_provider(provider)
    if p in {"google", "gemini", "google_genai", "vertex_ai", "vertex"}:
        if any(os.getenv(n) for n in ("GOOGLE_API_KEY", "GOOGLE_API_KEY_2", "GOOGLE_API_KEY_3")):
            keys = _env_chain("GOOGLE_API_KEY", "GOOGLE_API_KEY_2", "GOOGLE_API_KEY_3")
        elif any(os.getenv(n) for n in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3")):
            keys = _env_chain("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3")
        else:
            keys = _env_chain("ARTICLEBOOK_API_KEY")
        return keys
    if p in {"openai", "azure", "anthropic"}:
        keys = _env_chain("OPENAI_API_KEY", "OPENAI_API_KEY_2", "OPENAI_API_KEY_3")
        if keys:
            return keys
        return _env_chain("ARTICLEBOOK_API_KEY")
    keys = _env_chain("OPENAI_API_KEY", "OPENAI_API_KEY_2", "OPENAI_API_KEY_3")
    if keys:
        return keys
    keys = _env_chain("GOOGLE_API_KEY", "GOOGLE_API_KEY_2", "GOOGLE_API_KEY_3")
    if keys:
        return keys
    keys = _env_chain("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3")
    if keys:
        return keys
    return _env_chain("ARTICLEBOOK_API_KEY")


def resolve_llm_api_keys(provider: str) -> list[str]:
    """Return API keys in usage order, or keys extracted from ``ARTICLEBOOK_LLM_ROUTES``."""
    routes = parse_llm_routes_from_env()
    if routes:
        return [str(r["api_key"]) for r in routes]
    return _resolve_llm_api_keys_plain(provider)


def resolve_llm_api_key(provider: str) -> str | None:
    """Return the primary API key for ``provider``, or None if unset."""
    routes = parse_llm_routes_from_env()
    if routes:
        return str(routes[0]["api_key"])
    keys = _resolve_llm_api_keys_plain(provider)
    return keys[0] if keys else None


def missing_llm_api_key_message(provider: str) -> str:
    p = _norm_provider(provider)
    if p in {"google", "gemini", "google_genai", "vertex_ai", "vertex"}:
        return (
            "GOOGLE_API_KEY or GEMINI_API_KEY (optionally _2 / _3 variants for failover) "
            "is required for Google/Gemini runs. Set keys in the environment or .env "
            "(never commit secrets). For mixed OpenRouter/Groq/NVIDIA keys via LiteLLM, "
            "use ARTICLEBOOK_LLM_ROUTES instead and set ARTICLEBOOK_LLM_PROVIDER=openai."
        )
    return (
        "OPENAI_API_KEY (optionally OPENAI_API_KEY_2 / _3 for failover) is required "
        "for OpenAI-compatible runs, unless ARTICLEBOOK_LLM_ROUTES is set or all three "
        "ARTICLEBOOK_OPENROUTER_KEY_SUFFIX / ARTICLEBOOK_GROQ_KEY_SUFFIX / "
        "ARTICLEBOOK_NVIDIA_KEY_SUFFIX are set (see README). "
        "Set keys in the environment or .env (never commit secrets)."
    )
