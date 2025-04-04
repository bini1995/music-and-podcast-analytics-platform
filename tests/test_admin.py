# tests/test_admin.py
def test_admin_route(client):
    response = client.get("/admin/")
    assert response.status_code == 200
