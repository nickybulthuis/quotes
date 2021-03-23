import json
from datetime import date, datetime

import pytest
import responses
from fastapi.testclient import TestClient

from .brandnewday import funds_cache, quote_cache
from ..main import app
from ..models import Quote

client = TestClient(app)

prefix = '/brandnewday/'


@pytest.fixture(autouse=True)
def clear_cache():
    funds_cache.clear()
    quote_cache.clear()
    yield


def setup_get_funds_response():
    body = {'Message': json.dumps([{"Key": "1002", "Value": "bnd-wereld-indexfonds-c-hedged"},
                                   {"Key": "1012", "Value": "bnd-wereld-indexfonds-c-unhedged"}])}
    responses.add(responses.GET, 'https://secure.brandnewday.nl/service/getfundsnew/', json=body, status=200)


@responses.activate
def test_get_funds_returns_funds_list():
    setup_get_funds_response()

    response = client.get(prefix, allow_redirects=False)

    assert response.status_code == 200
    assert response.json() == ['bnd-wereld-indexfonds-c-hedged', 'bnd-wereld-indexfonds-c-unhedged']


@responses.activate
def test_get_funds_returns_502():
    responses.add(responses.GET, 'https://secure.brandnewday.nl/service/getfundsnew/',
                  body='error', status=502)
    response = client.get(prefix, allow_redirects=False)

    assert response.status_code == 502


def test_get_quotes_unknown_name_returns_http404():
    setup_get_funds_response()

    response = client.get(prefix + 'unknown', allow_redirects=False)
    assert response.status_code == 404


@responses.activate
def test_get_quotes_server_error_returns_http502():
    setup_get_funds_response()
    responses.add(
        responses.POST,
        url='https://secure.brandnewday.nl/service/navvaluesforfund/',
        body='error',
        status=500
    )

    response = client.get(prefix + 'bnd-wereld-indexfonds-c-unhedged')

    assert response.status_code == 502


@responses.activate
def test_get_quotes_invalid_page():
    setup_get_funds_response()

    response = client.get(prefix + 'bnd-wereld-indexfonds-c-unhedged?page=0')

    assert response.status_code == 400


@responses.activate
def test_get_quotes_known_name_returns_http200():
    setup_get_funds_response()

    body = {'Data': [
        {'FundId': 1012, 'FundLabel': None, 'LastRate': 13.535882, 'BidRate': 13.535882, 'AskRate': 13.535882,
         'RateDate': '/Date(1616284800000)/', 'Yield': -0.2612228741355754, 'InsertedBy': None,
         'Inserted': '/Date(-62135596800000)/', 'UpdatedBy': None, 'Updated': '/Date(-62135596800000)/'},
        {'FundId': 1012, 'FundLabel': None, 'LastRate': 13.535846, 'BidRate': 13.535846, 'AskRate': 13.535846,
         'RateDate': '/Date(1616198400000)/', 'Yield': -0.2612228741355754, 'InsertedBy': None,
         'Inserted': '/Date(-62135596800000)/', 'UpdatedBy': None, 'Updated': '/Date(-62135596800000)/'},
        {'FundId': 1012, 'FundLabel': None, 'LastRate': 13.535809, 'BidRate': 13.535809, 'AskRate': 13.535809,
         'RateDate': '/Date(1616112000000)/', 'Yield': -0.2612228741355754, 'InsertedBy': None,
         'Inserted': '/Date(-62135596800000)/', 'UpdatedBy': None, 'Updated': '/Date(-62135596800000)/'},
    ],
        'Total': 1224, 'AggregateResults': None, 'Errors': None}

    responses.add(
        responses.POST,
        url='https://secure.brandnewday.nl/service/navvaluesforfund/',
        json=body,
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        match=[
            responses.urlencoded_params_matcher({'page': '1',
                                                 'pageSize': '60',
                                                 'fundId': '1012',
                                                 'startDate': '01-01-2010',
                                                 'endDate': date.today().strftime('%d-%m-%Y'),
                                                 })
        ],
        status=200
    )

    response = client.get(prefix + 'bnd-wereld-indexfonds-c-unhedged')

    assert len(quote_cache) == 1
    assert response.status_code == 200
    assert response.json() == [{'Close': 13.535882, 'Date': '2021-03-21T00:00:00'},
                               {'Close': 13.535846, 'Date': '2021-03-20T00:00:00'},
                               {'Close': 13.535809, 'Date': '2021-03-19T00:00:00'}]


@responses.activate
def test_get_quotes_are_cached():
    setup_get_funds_response()

    body = {'Data': [
        {'FundId': 1012, 'FundLabel': None, 'LastRate': 13.535882, 'BidRate': 13.535882, 'AskRate': 13.535882,
         'RateDate': '/Date(1616284800000)/', 'Yield': -0.2612228741355754, 'InsertedBy': None,
         'Inserted': '/Date(-62135596800000)/', 'UpdatedBy': None, 'Updated': '/Date(-62135596800000)/'},
        {'FundId': 1012, 'FundLabel': None, 'LastRate': 13.535846, 'BidRate': 13.535846, 'AskRate': 13.535846,
         'RateDate': '/Date(1616198400000)/', 'Yield': -0.2612228741355754, 'InsertedBy': None,
         'Inserted': '/Date(-62135596800000)/', 'UpdatedBy': None, 'Updated': '/Date(-62135596800000)/'},
        {'FundId': 1012, 'FundLabel': None, 'LastRate': 13.535809, 'BidRate': 13.535809, 'AskRate': 13.535809,
         'RateDate': '/Date(1616112000000)/', 'Yield': -0.2612228741355754, 'InsertedBy': None,
         'Inserted': '/Date(-62135596800000)/', 'UpdatedBy': None, 'Updated': '/Date(-62135596800000)/'},
    ],
        'Total': 1224, 'AggregateResults': None, 'Errors': None}

    responses.add(
        responses.POST,
        url='https://secure.brandnewday.nl/service/navvaluesforfund/',
        json=body,
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        match=[responses.urlencoded_params_matcher(
            {'page': '1', 'pageSize': '60', 'fundId': '1012', 'startDate': '01-01-2010',
             'endDate': date.today().strftime('%d-%m-%Y')})],
        status=200
    )
    responses.add(
        responses.POST,
        url='https://secure.brandnewday.nl/service/navvaluesforfund/',
        body='error',
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        match=[responses.urlencoded_params_matcher(
            {'page': '1', 'pageSize': '60', 'fundId': '1012', 'startDate': '01-01-2010',
             'endDate': date.today().strftime('%d-%m-%Y')})],
        status=500
    )

    assert len(quote_cache) == 0
    response = client.get(prefix + 'bnd-wereld-indexfonds-c-unhedged')

    assert response.status_code == 200
    assert response.json() == [{'Close': 13.535882, 'Date': '2021-03-21T00:00:00'},
                               {'Close': 13.535846, 'Date': '2021-03-20T00:00:00'},
                               {'Close': 13.535809, 'Date': '2021-03-19T00:00:00'}]

    assert len(quote_cache) == 1
    response = client.get(prefix + 'bnd-wereld-indexfonds-c-unhedged')
    assert response.status_code == 200
    assert quote_cache['1012@1'] == [Quote(Date=datetime(2021, 3, 21, 0, 0, 0), Close=13.535882),
                                     Quote(Date=datetime(2021, 3, 20, 0, 0, 0), Close=13.535846),
                                     Quote(Date=datetime(2021, 3, 19, 0, 0, 0), Close=13.535809)]
