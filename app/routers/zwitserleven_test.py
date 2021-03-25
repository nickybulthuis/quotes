from datetime import datetime

import pytest
import responses
from fastapi.testclient import TestClient

from .zwitserleven import cache
from ..main import app
from ..models import Quote

client = TestClient(app)

prefix = '/zwitserleven/'


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield


def setup_get_funds_response():
    body = '''<html>
<table>
<tr class="showFonds" id="139">
<td>
<a href="https://www.zwitserleven.nl/over-zwitserleven/verantwoord-beleggen/fondsen/zwitserleven-ultra-long
-duration-fonds/">Zwitserleven Ultra Long Duration Fonds</a>
</td>
<td class="koers">64,25</td><td class="koers">25-03-2021</td>
</tr>
<tr class="showFonds" id="317">
<td>
<a href="https://www.zwitserleven.nl/over-zwitserleven/verantwoord-beleggen/fondsen/zwitserleven-variabele
-rente/">Zwitserleven Variabele Rente</a>
</td>
<td class="koers">21,36</td><td class="koers">24-03-2021</td>
</tr>
<tr class="showFonds" id="101">
<td>
<a href="https://www.zwitserleven.nl/over-zwitserleven/verantwoord-beleggen/fondsen/zwitserleven
-vastgoedfonds/">Zwitserleven Vastgoedfonds</a>
</td>
<td class="koers">24,26</td><td class="koers">24-03-2021</td>
</tr>
</table>
</html>'''

    responses.add(responses.GET,
                  'https://www.zwitserleven.nl/webtools/fondskoersen_2011/fondskoersen.aspx?cms_id=14421&amp'
                  ';cms_template=NL2015+Infopagina', body=body, status=200)


@responses.activate
def test_get_funds_returns_funds_list():
    setup_get_funds_response()
    response = client.get(prefix, allow_redirects=False)

    assert response.status_code == 200
    assert response.json() == ['zwitserleven-ultra-long-duration-fonds', 'zwitserleven-variabele-rente',
                               'zwitserleven-vastgoedfonds']


@responses.activate
def test_get_funds_returns_502():
    responses.add(responses.GET,
                  'https://www.zwitserleven.nl/webtools/fondskoersen_2011/fondskoersen.aspx?cms_id=14421&amp'
                  ';cms_template=NL2015+Infopagina',
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

    response = client.get(prefix + 'zwitserleven-vastgoedfonds')

    assert len(cache) == 3
    assert response.status_code == 200
    assert response.json() == [{'Close': 24.26, 'Date': '2021-03-24T00:00:00'}]


@responses.activate
def test_get_quotes_server_error_returns_http502():
    responses.add(responses.GET,
                  'https://www.zwitserleven.nl/webtools/fondskoersen_2011/fondskoersen.aspx?cms_id=14421&amp'
                  ';cms_template=NL2015+Infopagina',
                  body='error', status=500)

    response = client.get(prefix + 'zwitserleven-vastgoedfonds')

    assert response.status_code == 502


@responses.activate
def test_get_quotes_are_cached():
    setup_get_funds_response()
    responses.add(responses.GET,
                  'https://www.zwitserleven.nl/webtools/fondskoersen_2011/fondskoersen.aspx?cms_id=14421&amp'
                  ';cms_template=NL2015+Infopagina',
                  body='error', status=500)

    assert len(cache) == 0

    response = client.get(prefix + 'zwitserleven-vastgoedfonds')
    assert response.status_code == 200
    assert response.json() == [{'Close': 24.26, 'Date': '2021-03-24T00:00:00'}]

    assert len(cache) == 3

    # let's call it again.
    response = client.get(prefix + 'zwitserleven-vastgoedfonds')
    assert response.status_code == 200
    assert cache['zwitserleven-vastgoedfonds'] == [Quote(Date=datetime(2021, 3, 24, 0, 0, 0), Close=24.26)]
