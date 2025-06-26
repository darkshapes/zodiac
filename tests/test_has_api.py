import pytest
from unittest.mock import patch, MagicMock
import requests
from zodiac.providers.constants import check_host


def dbuq(error_log, message=None, status_code=None):
    print(f"Error Log: {error_log}, Message: {message}, Status Code: {status_code}")


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


def test_check_host_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"result": "OK"}
    mock_requests_get.return_value = mock_response

    assert check_host("API_SUCCESS", {"api_url": "http://127.0.0.1:7454"}) is True


def test_check_host_conn_err_then_succeed(mock_requests_get):
    mock_requests_get.side_effect = requests.exceptions.ConnectionError
    assert check_host("API_CONN_ERR", {"api_url": "http://127.0.0.1:7454"}) is False
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"result": "OK"}
    mock_requests_get.side_effect = None
    mock_requests_get.return_value = mock_response
    assert check_host("API_CONN_ERR_2", {"api_url": "http://127.0.0.1:7454"}) is True


def test_check_ok(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"result": "OK"}
    mock_requests_get.return_value = mock_response

    assert check_host("API_OK", {"api_url": "http://127.0.0.1:5110"}) is True


def test_check_200(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"result": "OK"}
    mock_requests_get.return_value = mock_response

    assert check_host("API_200", {"api_url": "http://127.0.0.1:5110"}) is True


def test_check_host_non_ok_status(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.ok = False
    mock_response.json.return_value = {}
    mock_requests_get.return_value = mock_response

    assert check_host("API_IS_NOT_OK", {"api_url": "http://127.0.0.1"}) is False


def test_check_host_connection_err(mock_requests_get):
    mock_requests_get.side_effect = requests.exceptions.ConnectionError("Mocked error")
    assert check_host("api_conn_err", {"api_url": "http://127.0.0.1"}) is False


# @pytest.fixture
# def mock_json_decoder():
#     from requests import JSONDecodeError

#     return JSONDecodeError("Mocked JSON decode error", "🤡.json", 69)


# def test_check_host_non_ok_json(mock_requests_get):
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.ok = True
#     mock_response.json.return_value = {"result": "Error"}
#     mock_requests_get.return_value = mock_response

#     assert check_host("API_OK_JSON", {"api_url": "http://127.0.0.1"}) is False

# def test_check_host_json_decode_error(mock_requests_get, mock_json_decoder):
#     from requests import JSONDecodeError

#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.ok = True
#     mock_response.json.side_effect = mock_json_decoder
#     mock_requests_get.return_value = mock_response
#     with pytest.raises(JSONDecodeError):
#         check_host("api_decode_error", {"api_url": "http://127.0.0.1"})

# Run the tests
if __name__ == "__main__":
    pytest.main(["-vv", __file__])
