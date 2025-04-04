# tests/test_dashboard.py
def test_dashboard_home(client):
    response = client.get("/dashboard/")
    assert response.status_code == 200

def test_spotify_visuals(client):
    response = client.get("/dashboard/spotify/visuals")
    assert response.status_code == 200
    assert "most_played_songs" in response.json
