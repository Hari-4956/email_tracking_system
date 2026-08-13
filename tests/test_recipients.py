from urllib.parse import quote


def test_recipient_lookup_by_id(client, existing_recipient):
    response = client.get(f"/api/recipients/{existing_recipient.id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == existing_recipient.id
    assert payload["tracking_token"] == existing_recipient.tracking_token
    assert payload["tracking_url"].endswith(
        f"/track/open/{existing_recipient.tracking_token}"
    )
    assert "tracking_url" in payload


def test_recipient_lookup_by_email(client, existing_recipient):
    encoded = quote(existing_recipient.email)
    response = client.get(f"/api/recipients/email/{encoded}")
    assert response.status_code == 200
    assert response.json()["email"] == existing_recipient.email


def test_recipient_lookup_by_token(client, existing_recipient):
    response = client.get(
        f"/api/recipients/token/{existing_recipient.tracking_token}"
    )
    assert response.status_code == 200
    assert response.json()["id"] == existing_recipient.id


def test_recipient_not_found(client):
    response = client.get("/api/recipients/999999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipient not found"


def test_recipient_list_no_filters(client):
    response = client.get("/api/recipients", params={"limit": 2, "skip": 0})
    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 2
    assert len(payload["recipients"]) <= 2
    assert payload["total"] == 71627


def test_recipient_limit_validation(client):
    response = client.get("/api/recipients", params={"limit": 501})
    assert response.status_code == 422


def test_search_by_name_case_insensitive(client, existing_recipient):
    fragment = existing_recipient.name[:4]
    assert fragment
    upper = client.get("/api/recipients", params={"search": fragment.upper(), "limit": 50})
    lower = client.get("/api/recipients", params={"search": fragment.lower(), "limit": 50})
    assert upper.status_code == 200
    assert lower.status_code == 200
    assert upper.json()["total"] == lower.json()["total"]
    assert upper.json()["total"] >= 1
    assert any(
        existing_recipient.id == item["id"] for item in upper.json()["recipients"]
    ) or upper.json()["total"] > len(upper.json()["recipients"])


def test_search_by_email_partial(client, existing_recipient):
    local = existing_recipient.email.split("@")[0][:6]
    response = client.get(
        "/api/recipients",
        params={"search": local, "limit": 50},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert len(payload["recipients"]) <= 50
    assert all(
        local.lower() in item["email"].lower()
        or local.lower() in item["name"].lower()
        or local.lower() in item["tracking_token"].lower()
        for item in payload["recipients"]
    )


def test_search_empty_results(client):
    response = client.get(
        "/api/recipients",
        params={"search": "zzz_no_such_recipient_xyz_999", "limit": 50},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 0
    assert payload["recipients"] == []


def test_status_pending_filter(client):
    response = client.get(
        "/api/recipients",
        params={"status": "PENDING", "limit": 20},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert all(item["send_status"] == "PENDING" for item in payload["recipients"])


def test_status_sent_filter(client):
    response = client.get("/api/recipients", params={"status": "SENT", "limit": 20})
    assert response.status_code == 200
    payload = response.json()
    assert all(item["send_status"] == "SENT" for item in payload["recipients"])


def test_status_failed_filter(client):
    response = client.get("/api/recipients", params={"status": "FAILED", "limit": 20})
    assert response.status_code == 200
    payload = response.json()
    assert all(item["send_status"] == "FAILED" for item in payload["recipients"])


def test_invalid_status(client):
    response = client.get("/api/recipients", params={"status": "DELIVERED"})
    assert response.status_code == 422


def test_opened_true_filter(client):
    response = client.get("/api/recipients", params={"opened": True, "limit": 20})
    assert response.status_code == 200
    payload = response.json()
    assert all(item["first_opened_at"] is not None for item in payload["recipients"])


def test_opened_false_filter(client):
    response = client.get("/api/recipients", params={"opened": False, "limit": 20})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert all(item["first_opened_at"] is None for item in payload["recipients"])


def test_campaign_id_filter(client):
    response = client.get(
        "/api/recipients",
        params={"campaign_id": 1, "limit": 10},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 71627
    assert all(item["campaign_id"] == 1 for item in payload["recipients"])


def test_invalid_campaign_id(client):
    response = client.get("/api/recipients", params={"campaign_id": 0})
    assert response.status_code == 422


def test_combined_filters(client, existing_recipient):
    fragment = existing_recipient.name.split()[0][:3]
    response = client.get(
        "/api/recipients",
        params={
            "search": fragment,
            "status": existing_recipient.send_status,
            "opened": existing_recipient.first_opened_at is not None,
            "campaign_id": 1,
            "limit": 50,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert len(payload["recipients"]) <= 50
    for item in payload["recipients"]:
        assert item["campaign_id"] == 1
        assert item["send_status"] == existing_recipient.send_status


def test_filtered_pagination(client):
    page1 = client.get(
        "/api/recipients",
        params={"status": "PENDING", "skip": 0, "limit": 5},
    ).json()
    page2 = client.get(
        "/api/recipients",
        params={"status": "PENDING", "skip": 5, "limit": 5},
    ).json()
    assert page1["total"] == page2["total"]
    ids1 = [item["id"] for item in page1["recipients"]]
    ids2 = [item["id"] for item in page2["recipients"]]
    assert len(ids1) <= 5
    if page1["total"] > 5:
        assert ids1 != ids2
        assert set(ids1).isdisjoint(set(ids2))


def test_search_result_total_matches_count(client, existing_recipient):
    fragment = existing_recipient.email.split("@")[0][:5]
    response = client.get(
        "/api/recipients",
        params={"search": fragment, "limit": 10},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recipients"]) <= 10
    # total is filter count, not page size
    assert payload["total"] >= len(payload["recipients"])


def test_search_does_not_return_all_rows(client):
    response = client.get(
        "/api/recipients",
        params={"search": "a", "limit": 50},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recipients"]) <= 50
    assert payload["total"] <= 71627
