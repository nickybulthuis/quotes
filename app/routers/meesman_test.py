from datetime import datetime

import pytest
import responses
from fastapi.testclient import TestClient

from .meesman import quote_cache, funds_cache
from ..main import app
from ..models import Quote

client = TestClient(app)

prefix = '/meesman/'


@pytest.fixture(autouse=True)
def clear_cache():
    funds_cache.clear()
    quote_cache.clear()
    yield


def setup_get_funds_response():
    body = '''<html><table>
    <tr>
        <td class="fund-name"><a href="/onze-fondsen/aandelen-wereldwijd-totaal/">Aandelen Wereldwijd Totaal</a></td>
    </tr>
    <tr>
        <td class="fund-name"><a href="/onze-fondsen/aandelen-ontwikkelde-landen/">Aandelen Ontwikkelde Landen</a></td>
    </tr>
    <tr>
        <td class="fund-name"><a href="/onze-fondsen/aandelen-opkomende-landen/">Aandelen Opkomende Landen</a></td>
    </tr>
    </table></html>'''

    responses.add(responses.GET, 'https://www.meesman.nl/onze-fondsen/',
                  body=body, status=200)


@responses.activate
def test_get_funds_returns_funds_list():
    setup_get_funds_response()
    response = client.get(prefix, allow_redirects=False)

    assert response.status_code == 200
    assert response.json() == ['aandelen-wereldwijd-totaal', 'aandelen-ontwikkelde-landen', 'aandelen-opkomende-landen']


@responses.activate
def test_get_funds_returns_502():
    responses.add(responses.GET, 'https://www.meesman.nl/onze-fondsen/',
                  body='error', status=502)
    response = client.get(prefix, allow_redirects=False)

    assert response.status_code == 502


def test_get_quotes_unknown_name_returns_http404():
    setup_get_funds_response()

    response = client.get(prefix + 'unknown', allow_redirects=False)
    assert response.status_code == 404


@responses.activate
def test_get_quotes_known_name_returns_http200():
    setup_get_funds_response()

    body = "data: [{\"x\":\"2021-01-01T00:00:00\",\"y\":10}," \
           "{\"x\":\"2021-01-02T00:00:00\",\"y\":10.50}," \
           "{\"x\":\"2021-01-03T00:00:00\",\"y\":11}]"
    responses.add(responses.GET, 'https://www.meesman.nl/onze-fondsen/aandelen-wereldwijd-totaal/',
                  body=body, status=200)

    response = client.get(prefix + 'aandelen-wereldwijd-totaal')

    assert len(quote_cache) == 1
    assert response.status_code == 200
    assert response.json() == [{'Close': 10.0, 'Date': '2021-01-01T00:00:00'},
                               {'Close': 10.5, 'Date': '2021-01-02T00:00:00'},
                               {'Close': 11.0, 'Date': '2021-01-03T00:00:00'}]


@responses.activate
def test_get_quotes_server_error_returns_http502():
    setup_get_funds_response()
    responses.add(responses.GET, 'https://www.meesman.nl/onze-fondsen/aandelen-wereldwijd-totaal/',
                  body='unknown', status=500)

    response = client.get(prefix + 'aandelen-wereldwijd-totaal')

    assert response.status_code == 502


@responses.activate
def test_get_quotes_are_cached():
    setup_get_funds_response()
    body = "data: [{\"x\":\"2021-01-01T00:00:00\",\"y\":10}," \
           "{\"x\":\"2021-01-02T00:00:00\",\"y\":10.50}," \
           "{\"x\":\"2021-01-03T00:00:00\",\"y\":11}]"
    responses.add(responses.GET, 'https://www.meesman.nl/onze-fondsen/aandelen-wereldwijd-totaal/',
                  body=body, status=200)
    responses.add(responses.GET, 'https://www.meesman.nl/onze-fondsen/aandelen-wereldwijd-totaal/',
                  body=body, status=500)

    assert len(quote_cache) == 0

    response = client.get(prefix + 'aandelen-wereldwijd-totaal')
    assert response.status_code == 200
    assert response.json() == [{'Close': 10.0, 'Date': '2021-01-01T00:00:00'},
                               {'Close': 10.5, 'Date': '2021-01-02T00:00:00'},
                               {'Close': 11.0, 'Date': '2021-01-03T00:00:00'}]

    assert len(quote_cache) == 1

    # let's call it again.
    response = client.get(prefix + 'aandelen-wereldwijd-totaal')
    assert response.status_code == 200
    assert quote_cache['aandelen-wereldwijd-totaal'] == [Quote(Date=datetime(2021, 1, 1, 0, 0, 0), Close=10.0),
                                                         Quote(Date=datetime(2021, 1, 2, 0, 0, 0), Close=10.5),
                                                         Quote(Date=datetime(2021, 1, 3, 0, 0, 0), Close=11.0)]
