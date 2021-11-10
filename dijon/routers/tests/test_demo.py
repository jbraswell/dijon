def test_ping(ctx):
    response = ctx.client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data == "pong"


def test_echo(ctx):
    response = ctx.client.post("/echo", json={"message": "hello"})
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "hello"
