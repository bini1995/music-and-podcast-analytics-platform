def test_login(client, db_session):
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123",
        "role": "user"
    })

    db_session.commit()

    response = client.post("/auth/login", json={
        "username": "testuser",  # ✅ use username, not email
        "password": "TestPass123"
    })

    assert response.status_code == 200
