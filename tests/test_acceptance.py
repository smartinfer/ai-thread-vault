"""Acceptance tests — the real user journeys through the CLI.

They drive the external interface (the CLI) with tiny fixtures — no network,
no accounts, no AI service is ever contacted.
"""
import json
import subprocess
import sys
from pathlib import Path


def _cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ai_thread_vault.cli", *args],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True, text=True,
    )


def test_jsonl_import_then_search(tmp_path):
    db = str(tmp_path / "v.db")
    src = tmp_path / "chat.jsonl"
    src.write_text("\n".join(json.dumps(m) for m in [
        {"thread_id": "t1", "role": "user", "content": "how do I enable sqlite fts5 search?"},
        {"thread_id": "t1", "role": "assistant", "content": "use a virtual table using fts5"},
    ]))
    assert _cli("init", db).returncode == 0
    assert _cli("import", db, "jsonl", str(src)).returncode == 0
    out = _cli("search", db, "fts5")
    assert out.returncode == 0 and "fts5" in out.stdout.lower(), out.stdout + out.stderr


def test_markdown_import_then_search(tmp_path):
    db = str(tmp_path / "v.db")
    d = tmp_path / "md"
    d.mkdir()
    (d / "conv.md").write_text("## user\nenable fts5 please\n\n## assistant\nfts5 virtual table\n")
    assert _cli("init", db).returncode == 0
    assert _cli("import", db, "markdown", str(d)).returncode == 0
    out = _cli("search", db, "fts5")
    assert out.returncode == 0 and "fts5" in out.stdout.lower(), out.stdout + out.stderr


def test_stats_after_import(tmp_path):
    db = str(tmp_path / "v.db")
    src = tmp_path / "chat.jsonl"
    src.write_text(json.dumps({"thread_id": "t1", "role": "user", "content": "hello"}) + "\n")
    _cli("init", db)
    _cli("import", db, "jsonl", str(src))
    out = _cli("stats", db)
    assert out.returncode == 0 and out.stdout.strip() not in ("", "{}"), out.stdout + out.stderr


def test_roles_are_preserved(tmp_path):
    """A conversation vault must keep who-said-what: assistant stays assistant."""
    db = str(tmp_path / "v.db")
    src = tmp_path / "chat.jsonl"
    src.write_text("\n".join(json.dumps(m) for m in [
        {"thread_id": "t1", "role": "user", "content": "question here"},
        {"thread_id": "t1", "role": "assistant", "content": "answer here"},
    ]))
    _cli("init", db)
    _cli("import", db, "jsonl", str(src))
    thread = json.loads(_cli("show", db, "t1").stdout)
    roles = [m["role"] for m in thread["messages"]]
    assert "assistant" in roles, f"assistant role lost: {roles}"
    assert "user" in roles, roles


def test_gemini_import_then_search(tmp_path):
    """Gemini export (roles user/model) imports and is searchable; model->assistant."""
    db = str(tmp_path / "v.db")
    src = tmp_path / "gemini.json"
    src.write_text(json.dumps({"conversations": [{
        "id": "g1", "title": "Gemini chat",
        "messages": [
            {"role": "user", "content": "explain sqlite fts5 quickly"},
            {"role": "model", "content": "fts5 is a full text search extension for sqlite"},
        ],
    }]}))
    assert _cli("init", db).returncode == 0
    assert _cli("import", db, "gemini", str(src)).returncode == 0, _cli("import", db, "gemini", str(src)).stderr
    out = _cli("search", db, "fts5")
    assert out.returncode == 0 and "fts5" in out.stdout.lower(), out.stdout + out.stderr
    thread = json.loads(_cli("show", db, "g1").stdout)
    assert "assistant" in [m["role"] for m in thread["messages"]], "gemini 'model' role not mapped to assistant"
