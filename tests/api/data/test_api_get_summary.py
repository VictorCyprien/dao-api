from flask.app import Flask
from rich import print
from unittest.mock import ANY
import unittest.mock
from datetime import datetime

from api.models.user import User


def test_get_summary(client: Flask, victor: User, victor_logged_in: str):
    sample_data = [
        (1, "cid1", "summary", "source1", "Daily Summary for 2024-01-01", "Summary text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}")
    ]

    with unittest.mock.patch('api.views.data.data_view.query_db', return_value=sample_data) as mock_query_db:
        res = client.get("/data/summary?date_start=2024-01-01&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
        assert res.status_code == 200
        data = res.json
        print(data)
        assert mock_query_db.call_count == 1

        assert "summary" in data
        assert isinstance(data["summary"], list)
        assert len(data["summary"]) == 1
        assert "2024-01-01" in data["summary"][0]
        assert data["summary"][0]["2024-01-01"][0]["title"] == "Daily Summary for 2024-01-01"


def test_get_summary_invalid_dates(client: Flask, victor: User, victor_logged_in: str):
    res = client.get("/data/summary?date_start=invalid&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data["status"] == "Bad Request"
    assert data["message"] == "The date format is invalid for date_start"

    res = client.get("/data/summary?date_start=2024-01-02&date_end=invalid", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data["status"] == "Bad Request"
    assert data["message"] == "The date format is invalid for date_end"


def test_get_summary_not_logged(client: Flask, victor: User):
    res = client.get("/data/summary?date_start=2024-01-01&date_end=2024-01-02")
    assert res.status_code == 401
    data = res.json
    print(data)
    assert data == {
        'code': 401,
        'message': "Not Authenticated",
        'status': 'Unauthorized',
    }


def test_get_summary_source_list(client: Flask, victor: User, victor_logged_in: str):
    sample_data = [
        (1, "cid1", "summary", '[{"name": "source1", "url": "http://source1.com"}, {"name": "source2", "url": "http://source2.com"}]', "Daily Summary for 2024-01-01", "Summary text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}")
    ]

    with unittest.mock.patch('api.views.data.data_view.query_db', return_value=sample_data) as mock_query_db:
        res = client.get("/data/summary?date_start=2024-01-01&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
        assert res.status_code == 200
        data = res.json
        print(data)
        assert mock_query_db.call_count == 1

        assert "summary" in data
        assert isinstance(data["summary"], list)
        assert len(data["summary"]) == 1
        assert "2024-01-01" in data["summary"][0]
        summary = data["summary"][0]["2024-01-01"][0]
        assert isinstance(summary["source"], list)
        assert len(summary["source"]) == 2
        assert summary["source"][0]["name"] == "source1"
        assert summary["source"][1]["name"] == "source2"


def test_get_summary_source_dict(client: Flask, victor: User, victor_logged_in: str):
    sample_data = [
        (1, "cid1", "summary", '{"name": "source1", "url": "http://source1.com"}', "Daily Summary for 2024-01-01", "Summary text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}")
    ]

    with unittest.mock.patch('api.views.data.data_view.query_db', return_value=sample_data) as mock_query_db:
        res = client.get("/data/summary?date_start=2024-01-01&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
        assert res.status_code == 200
        data = res.json
        print(data)
        assert mock_query_db.call_count == 1

        assert "summary" in data
        assert isinstance(data["summary"], list)
        assert len(data["summary"]) == 1
        assert "2024-01-01" in data["summary"][0]
        summary = data["summary"][0]["2024-01-01"][0]
        assert isinstance(summary["source"], dict)
        assert summary["source"]["name"] == "source1"
        assert summary["source"]["url"] == "http://source1.com"




def test_get_summary_source_not_convertible(client: Flask, victor: User, victor_logged_in: str):
    sample_data = [
        (1, "cid1", "summary", '{"name": "source1", "url": "http://source1.com"}', "Daily Summary for 2024-01-01", "Summary text 1", "http://link1.com", "topic1,topic2", 1704067200, "{}")
    ]

    with unittest.mock.patch('api.views.data.data_view.query_db', return_value=sample_data) as mock_query_db:
        with unittest.mock.patch('api.views.data.data_view.literal_eval', side_effect=Exception) as mock_literal_eval:
            res = client.get("/data/summary?date_start=2024-01-01&date_end=2024-01-02", headers={"Authorization": f"Bearer {victor_logged_in}"})
            assert res.status_code == 200
            data = res.json
            print(data)
            assert mock_query_db.call_count == 1
            assert mock_literal_eval.call_count == 1

            assert "summary" in data
            assert isinstance(data["summary"], list)
            assert len(data["summary"]) == 1
            assert "2024-01-01" in data["summary"][0]
            summary = data["summary"][0]["2024-01-01"][0]
            assert isinstance(summary["source"], str)
            assert summary["source"] == '{"name": "source1", "url": "http://source1.com"}'

