from flask.app import Flask
from rich import print
from unittest.mock import ANY
import unittest.mock
from datetime import datetime

from api.models.user import User


def test_get_items(client: Flask, victor: User, victor_logged_in: str):
    sample_data = [
        (1, "cid1", "article", "source1", "Title 1", "Text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}"),
        (2, "cid2", "article", "source2", "Title 2", "Text 2", "http://link2.com", "topic2,topic3", 1704153600, "{}")
    ]

    with unittest.mock.patch('api.views.data.data_view.query_db', return_value=sample_data) as mock_query_db:
        res = client.get("/data/items?date_start=2024-01-01&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
        assert res.status_code == 200
        data = res.json
        print(data)
        assert mock_query_db.call_count == 1

        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2
        assert data["data"][0]["title"] == "Title 1"
        assert data["data"][1]["title"] == "Title 2"


def test_get_items_with_source(client: Flask, victor: User, victor_logged_in: str):
    sample_data = [
        (1, "cid1", "article", "source1", "Title 1", "Text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}"),
        (1, "cid1", "article", "source1", "Title 2", "Text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}")
    ]

    with unittest.mock.patch('api.views.data.data_view.query_db', return_value=sample_data) as mock_query_db:
        # Due to mock, we can't get only one source. So we suppose that all data is from the same source
        res = client.get("/data/items?date_start=2024-01-01&date_end=2024-01-02&source=source1", headers={"Authorization": f"Bearer {victor_logged_in}"})
        assert res.status_code == 200
        data = res.json
        print(data)
        assert mock_query_db.call_count == 1

        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2
        assert data["data"][0]["title"] == "Title 1"
        assert data["data"][1]["title"] == "Title 2"


def test_get_items_invalid_dates(client: Flask, victor: User, victor_logged_in: str):
    res = client.get("/data/items?date_start=invalid&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data["status"] == "Bad Request"
    assert data["message"] == "The date format is invalid for date_start"


    res = client.get("/data/items?date_start=2024-01-02&date_end=invalid", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data["status"] == "Bad Request"
    assert data["message"] == "The date format is invalid for date_end"


def test_get_items_not_logged(client: Flask, victor: User):
    res = client.get("/data/items?date_start=2024-01-01&date_end=2024-01-02")
    assert res.status_code == 401
    data = res.json
    print(data)
    assert data == {
        'code': 401,
        'message': "Not Authenticated",
        'status': 'Unauthorized',
    }
