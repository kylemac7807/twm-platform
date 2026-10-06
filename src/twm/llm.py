"""The one model wrapper (architecture decision 2; M2 step 3).

Every model call in the platform goes through call(): the model name is configuration, temperature is 0 for
extraction, the answer is validated against the task contract (a pydantic model), a malformed answer is retried
at most twice and then flagged, and every call is logged (model, tokens, latency, validation pass or fail). The
log is the raw material for the Claude-versus-GPT comparison in M3. A FakeModel keeps tests free and offline.

The credential comes from .env (ANTHROPIC_API_KEY) and is never logged or printed. In a client deployment the
same wrapper points at Azure Foundry instead; nothing else changes.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.environ.get("TWM_MODEL", "claude-opus-5-5")
DEFAULT_EFFORT = os.environ.get("TWM_EFFORT", "low")   # extraction is copying, not reasoning; raise if evaluation says so
MAX_RETRIES = 2


@dataclass
class ModelConfig:
    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    max_tokens: int = 8000
    cache_dir: Optional[Path] = None        # content-hash cache of answers; same input -> same answer, no spend


@dataclass
class CallLog:
    model: str
    contract: str
    input_chars: int
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    latency_s: float
    attempts: int
    validated: bool
    error: Optional[str] = None
    cached: bool = False


@dataclass
class CallResult:
    output: Optional[BaseModel]
    log: CallLog
    raw: Optional[str] = None
    flagged: bool = False
    flag_reason: Optional[str] = None
    cached: bool = False


class Model(Protocol):
    name: str

    def complete(self, system: str, user: str, max_tokens: int, temperature: float) -> tuple[str, Optional[int], Optional[int]]:
        """Return (text, input_tokens, output_tokens)."""
        ...


# ---------------------------------------------------------------- real model (Anthropic API, direct)
class AnthropicModel:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.name = model
        self._client = None

    def _c(self):
        if self._client is None:
            _load_dotenv()
            import anthropic
            self._client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
        return self._client

    def complete(self, system, user, max_tokens, temperature):
        # Current models (Opus 5.5, Sonnet 5.5) take no sampling parameters: temperature is rejected. Determinism
        # comes from the content-hash cache in call(); depth of reasoning is controlled with output_config.effort.
        r = self._c().messages.create(model=self.name, max_tokens=max_tokens, system=system,
                                      output_config={"effort": DEFAULT_EFFORT},
                                      messages=[{"role": "user", "content": user}])
        if r.stop_reason == "refusal":
            raise RuntimeError(f"model declined the request ({getattr(getattr(r, 'stop_details', None), 'category', None)})")
        if r.stop_reason == "max_tokens":
            raise ValueError("answer truncated at max_tokens; section too large")
        text = "".join(getattr(b, "text", "") for b in r.content if getattr(b, "type", "") == "text")
        return text, r.usage.input_tokens, r.usage.output_tokens


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        for parent in [Path.cwd(), *Path(__file__).resolve().parents]:
            env = parent / ".env"
            if env.exists():
                load_dotenv(env, override=False)
                return
    except ImportError:
        pass


# ---------------------------------------------------------------- fake model for tests
class FakeModel:
    """Answers from a script: a list of strings returned in order, or a callable(system, user) -> str."""

    name = "fake"

    def __init__(self, answers=None, fn=None):
        self.answers = list(answers or [])
        self.fn = fn
        self.calls: list[tuple[str, str]] = []

    def complete(self, system, user, max_tokens, temperature):
        self.calls.append((system, user))
        if self.fn:
            return self.fn(system, user), len(user) // 4, 100
        if not self.answers:
            raise RuntimeError("FakeModel has no scripted answer left")
        return self.answers.pop(0), len(user) // 4, 100


# ---------------------------------------------------------------- the call
LOG: list[CallLog] = []  # in-process log; the run writes it out with the run report


def extract_json(text: str) -> str:
    """The model is told to answer with JSON only; tolerate a fenced block or leading prose."""
    m = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.S)
    if m:
        return m.group(1)
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start >= 0:
        return text[start:]
    return text


def call(contract: Type[T], system: str, user: str, model: Model, config: Optional[ModelConfig] = None) -> CallResult:
    """Ask the model to fill `contract`. Validate; retry a malformed answer at most MAX_RETRIES times; then flag."""
    config = config or ModelConfig(model=getattr(model, "name", DEFAULT_MODEL))
    t0 = time.time()
    key = hashlib.sha256((config.model + chr(0) + system + chr(0) + user + chr(0) + contract.__name__).encode("utf-8")).hexdigest()
    if config.cache_dir:
        cached = Path(config.cache_dir) / f"{key}.json"
        if cached.exists():
            try:
                out = contract.model_validate_json(cached.read_text(encoding="utf-8"))
                log = CallLog(config.model, contract.__name__, len(user), None, None, 0.0, 0, True, cached=True)
                LOG.append(log)
                return CallResult(output=out, log=log, cached=True)
            except Exception:
                pass
    attempts, last_err, raw, in_tok, out_tok = 0, None, None, None, None
    user_now = user
    while attempts <= MAX_RETRIES:
        attempts += 1
        try:
            raw, in_tok, out_tok = model.complete(system, user_now, config.max_tokens, config.temperature)
            out = contract.model_validate_json(extract_json(raw))
            log = CallLog(config.model, contract.__name__, len(user), in_tok, out_tok, round(time.time() - t0, 2), attempts, True)
            LOG.append(log)
            if config.cache_dir:
                Path(config.cache_dir).mkdir(parents=True, exist_ok=True)
                (Path(config.cache_dir) / f"{key}.json").write_text(out.model_dump_json(), encoding="utf-8")
            return CallResult(output=out, log=log, raw=raw)
        except (ValidationError, ValueError, json.JSONDecodeError) as e:
            last_err = f"{type(e).__name__}: {str(e)[:300]}"
            user_now = user + chr(10) + chr(10) + "Your previous answer did not fit the required JSON schema: " + last_err[:400] + chr(10) + "Answer again with JSON only, exactly matching the schema. Leave any field you are not certain of as null."
        except Exception as e:  # transport errors are not retried blindly
            last_err = f"{type(e).__name__}: {str(e)[:300]}"
            break
    log = CallLog(config.model, contract.__name__, len(user), in_tok, out_tok, round(time.time() - t0, 2), attempts, False, error=last_err)
    LOG.append(log)
    return CallResult(output=None, log=log, raw=raw, flagged=True, flag_reason=f"model answer never fit {contract.__name__} after {attempts} attempt(s): {last_err}")


def log_summary() -> dict[str, Any]:
    n = len(LOG)
    return {
        "calls": n,
        "validated": sum(1 for l in LOG if l.validated),
        "flagged": sum(1 for l in LOG if not l.validated),
        "cached": sum(1 for l in LOG if l.cached),
        "input_tokens": sum(l.input_tokens or 0 for l in LOG),
        "output_tokens": sum(l.output_tokens or 0 for l in LOG),
        "models": sorted({l.model for l in LOG}),
    }
