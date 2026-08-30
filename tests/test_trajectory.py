"""The trajectory renderer has to survive the thing it is rendering.

A prompt contains the module source inside its own fenced block. Wrapping that
in three backticks silently truncates the document at the first inner fence,
which is how a judge would lose the one page they were asked to read.
"""

from __future__ import annotations

import json
from pathlib import Path

from pindown.eval.trajectory import _fence, export, render


def test_fence_is_longer_than_any_inner_fence():
    inner = "```python\ndef f():\n    return 1\n```"
    rendered = _fence(inner, 40, "text")
    assert rendered.startswith("````")
    assert rendered.count("````") == 2
    assert "def f():" in rendered


def test_export_writes_one_file_per_record(tmp_path: Path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "model": "stub",
                "temperature": 0.0,
                "python": "3.12.3",
                "git_revision": "test",
            }
        )
    )
    record = {
        "module_id": "toy.math",
        "arm": "golden",
        "score": 0.25,
        "n_tests": 3,
        "killed": 2,
        "timeout": 0,
        "survived": 6,
        "total": 8,
        "wall_clock_s": 1.2,
        "cost_usd": 0.0,
        "iterations": [
            {
                "n": 1,
                "phase": "golden",
                "tests_proposed": 3,
                "tests_kept": 3,
                "discarded": [],
                "score_before": 0.0,
                "score_after": 0.25,
                "survivors_before": 8,
                "survivors_after": 6,
                "duration_s": 1.0,
                "note": "",
            }
        ],
        "error": None,
    }
    (run_dir / "records.jsonl").write_text(json.dumps(record) + "\n")
    (run_dir / "suites").mkdir()
    (run_dir / "suites" / "toy.math.golden.py").write_text("def test_one():\n    assert True\n")
    (run_dir / "suites" / "toy.math.golden.survivors.txt").write_text(
        "m00001.0-comparison  line 4  comparison `<` -> `<=`\n"
    )

    written = export(run_dir, tmp_path / "out")
    assert len(written) == 1
    text = written[0].read_text()
    assert "toy.math" in text
    assert "25.0%" in text
    assert "comparison `<` -> `<=`" in text
    assert "def test_one()" in text


def test_render_includes_a_rejection_reason(tmp_path: Path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "model": "stub",
                "temperature": 0.0,
                "python": "3.12.3",
                "git_revision": "test",
            }
        )
    )
    record = {
        "module_id": "toy.math",
        "arm": "golden",
        "score": 0.0,
        "n_tests": 0,
        "killed": 0,
        "timeout": 0,
        "survived": 0,
        "total": 0,
        "wall_clock_s": 0.4,
        "cost_usd": 0.0,
        "iterations": [],
        "error": "suite fails at import: ModuleNotFoundError",
    }
    text = render(run_dir, record)
    assert "did not produce a usable suite" in text
    assert "ModuleNotFoundError" in text
