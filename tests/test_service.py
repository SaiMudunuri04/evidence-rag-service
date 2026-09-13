from fastapi.testclient import TestClient

from service import app, rag


class FakeGenerator:
    def complete(self, system, user):
        assert "[S1]" in user
        return "Drain the queue before restart. [S1]"


def test_grounded_answer_and_citation():
    documents = [{"source": "runbook.md", "offset": 0, "text": "Drain the queue before restarting the worker."}]
    result = rag.answer("How to restart worker?", rag.BM25Index(documents), FakeGenerator())
    assert result["citation_check"] == "valid_ids"
    assert result["sources"][0]["source"] == "runbook.md"


def test_ready_requires_documents(monkeypatch):
    monkeypatch.setenv("DOCUMENT_ROOT", "/does-not-exist")
    app.index.cache_clear()
    assert TestClient(app.app).get("/health/ready").status_code == 503
