def test_campaign_list(client, campaign_one, recipient_count):
    response = client.get("/api/campaigns")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert any(c["id"] == 1 for c in payload["campaigns"])
    campaign = next(c for c in payload["campaigns"] if c["id"] == 1)
    assert campaign["name"] == "E STAR Independence Day 2026"
    assert campaign["total_recipients"] == recipient_count
    assert recipient_count == 71627


def test_campaign_detail(client, recipient_count):
    response = client.get("/api/campaigns/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["name"] == "E STAR Independence Day 2026"
    assert payload["total_recipients"] == recipient_count


def test_campaign_stats_aggregation(client, recipient_count):
    response = client.get("/api/campaigns/1/stats")
    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == 1
    assert payload["total_recipients"] == recipient_count == 71627
    assert payload["pending"] + payload["sent"] + payload["failed"] <= payload["total_recipients"]
    assert payload["opened"] == payload["unique_opened"]
    assert payload["total_opens"] >= payload["unique_opened"]
    if payload["total_recipients"] > 0:
        expected_rate = round(
            (payload["unique_opened"] / payload["total_recipients"]) * 100,
            4,
        )
        assert payload["open_rate"] == expected_rate
    else:
        assert payload["open_rate"] == 0.0


def test_invalid_campaign_id(client):
    response = client.get("/api/campaigns/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"


def test_campaign_id_validation(client):
    response = client.get("/api/campaigns/0")
    assert response.status_code == 422
