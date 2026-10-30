def test_tasks_list_response_404(anon_client):
    response = anon_client.get("/tasks")
    assert response.status_code == 404
