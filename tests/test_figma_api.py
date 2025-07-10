import types
import figma_api


def test_get_file(monkeypatch):
    client = figma_api.FigmaClient("TOKEN")

    def fake_get(url, headers):
        assert headers["X-Figma-Token"] == "TOKEN"
        response = types.SimpleNamespace()
        response.raise_for_status = lambda: None
        response.json = lambda: {"file": "data"}
        return response

    monkeypatch.setattr(figma_api.requests, "get", fake_get)
    data = client.get_file("abc")
    assert data == {"file": "data"}

