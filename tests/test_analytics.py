def test_analytics_campaign(client, recipient_count):
    response = client.get("/api/analytics/campaign/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == 1
    assert payload["total_recipients"] == recipient_count == 71627
    assert "open_rate" in payload
    assert "unique_opened" in payload


def test_analytics_recipient(client, existing_recipient):
    response = client.get(f"/api/analytics/recipient/{existing_recipient.id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == existing_recipient.id
    assert payload["tracking_token"] == existing_recipient.tracking_token
    assert "/track/open/" in payload["tracking_url"]


def test_analytics_recipient_events(client, existing_recipient):
    response = client.get(
        f"/api/analytics/recipient/{existing_recipient.id}/events",
        params={"limit": 10},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recipient_id"] == existing_recipient.id
    assert "events" in payload
    assert payload["limit"] == 10


def test_campaign_opens(client):
    response = client.get(
        "/api/analytics/campaign/1/opens",
        params={"limit": 10},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == 1
    assert len(payload["opens"]) <= 10
    if payload["opens"]:
        item = payload["opens"][0]
        assert "event_id" in item
        assert "recipient_email" in item
        assert item["event_type"] == "OPENED"


def test_open_timeline(client):
    response = client.get("/api/analytics/campaign/1/opens/timeline")
    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == 1
    assert isinstance(payload["timeline"], list)
    for item in payload["timeline"]:
        assert "date" in item
        assert "opens" in item


def test_invalid_analytics_campaign(client):
    response = client.get("/api/analytics/campaign/999999")
    assert response.status_code == 404


def test_invalid_analytics_recipient(client):
    response = client.get("/api/analytics/recipient/999999999")
    assert response.status_code == 404
