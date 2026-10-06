"""The model wrapper (M2 step 3): validation, retry, flagging, caching, logging. All offline with FakeModel."""
from pydantic import BaseModel

from twm import llm
from twm.llm import FakeModel, ModelConfig, call, extract_json


class Toy(BaseModel):
    title: str
    rate: float | None = None


def setup_function():
    llm.LOG.clear()


def test_valid_answer_is_validated_and_logged():
    m = FakeModel(['{"title": "Developer", "rate": 120.0}'])
    r = call(Toy, "sys", "user", m)
    assert r.output == Toy(title="Developer", rate=120.0) and not r.flagged
    assert r.log.validated and r.log.attempts == 1 and r.log.contract == "Toy"
    assert llm.log_summary()["validated"] == 1


def test_malformed_answer_is_retried_then_accepted():
    m = FakeModel(["not json at all", '{"title": "Developer"}'])
    r = call(Toy, "sys", "user", m)
    assert r.output.title == "Developer" and r.log.attempts == 2
    assert "did not fit the required JSON schema" in m.calls[1][1]   # the retry explains the failure


def test_three_bad_answers_flag_not_guess():
    m = FakeModel(["x", "y", "z"])
    r = call(Toy, "sys", "user", m)
    assert r.output is None and r.flagged and r.log.attempts == 3
    assert "never fit Toy" in r.flag_reason


def test_fenced_json_is_tolerated():
    assert extract_json('Here you go:\n```json\n{"a": 1}\n```').strip() == '{"a": 1}'


def test_cache_means_no_second_spend(tmp_path):
    m = FakeModel(['{"title": "Tester"}'])
    cfg = ModelConfig(model="fake", cache_dir=tmp_path)
    a = call(Toy, "sys", "same input", m, cfg)
    b = call(Toy, "sys", "same input", m, cfg)
    assert a.output == b.output and b.cached and len(m.calls) == 1
