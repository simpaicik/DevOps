def test_index_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "GymLog".encode() in resp.data


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}
