import json
import re
from datetime import date, datetime
from typing import List, Optional

import requests
from cachetools import TTLCache
from fastapi import APIRouter, HTTPException

from app.models import Fund, Quote, Message

router = APIRouter(
    prefix='/brandnewday',
    tags=['Brand New Day']
)

BASE_URL = 'https://secure.brandnewday.nl/service/{0}/'
QUOTE_REGEX = r'\/Date\(([0-9]+)\)\/'
funds_cache = TTLCache(maxsize=128, ttl=60 * 60 * 4)  # ttl in seconds, 4hrs.
quote_cache = TTLCache(maxsize=128, ttl=60 * 60 * 4)  # ttl in seconds, 4hrs.


@router.get(
    "/",
    response_model=List[str],
    summary="Get all available funds",
    responses={502: {'description': 'When an error occurred while retrieving the funds', 'model': Message}}
)
async def get_funds():
    return [f.name for f in await list_funds()]


async def list_funds():
    if len(funds_cache) == 0:
        await fetch_funds()
    return list(funds_cache.values())


async def fetch_funds():
    r = requests.get(url=BASE_URL.format('getfundsnew'))

    if r.status_code != requests.codes.ok:
        raise HTTPException(status_code=502, detail={'message': 'Could not retrieve funds'})

    funds = json.loads(r.json()['Message'])

    # clear the caches, there might be new funds how unlikely it might be.
    quote_cache.clear()
    funds_cache.clear()

    for fund in funds:
        fund_name = str.lower(fund['Value']).replace(' ', '-')
        fund_id = fund['Key']

        funds_cache[fund_id] = Fund(name=fund_name, id=fund_id)


@router.get(
    "/{fund_name}",
    response_model=List[Quote],
    summary="Delivers quotes for the specified fund by name",
    responses={502: {'description': 'When an error occurred while retrieving the quotes', 'model': Message},
               404: {'description': 'When the specified fund could not be found, or the fund is unknown',
                     'model': Message}},
)
async def get_quotes(fund_name: str, page: Optional[int] = 1):
    funds = await list_funds()
    fund = next((f for f in funds if f.name == fund_name.strip().lower()), None)

    if fund:

        cache_id = get_cache_id(fund.id, page)
        if cache_id not in quote_cache:
            await fetch_quotes(fund.id, page)

        return quote_cache[cache_id]

    else:
        raise HTTPException(status_code=404, detail="Fund {0} could not be found".format(fund_name))


async def fetch_quotes(fund_id, page):
    if page < 1:
        raise HTTPException(status_code=400, detail="Invalid page, must be >= 1")

    r = requests.post(
        url=BASE_URL.format('navvaluesforfund'),
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        data={'page': page,
              'pageSize': 60,
              'fundId': fund_id,
              'startDate': '01-01-2010',
              'endDate': date.today().strftime('%d-%m-%Y'),
              })

    if r.status_code != requests.codes.ok:
        raise HTTPException(status_code=502, detail={'message': 'Could not retrieve quotes'})

    cache_id = get_cache_id(fund_id, page)
    quote_cache[cache_id] = [
        Quote(Date=datetime.utcfromtimestamp(int(re.match(QUOTE_REGEX, q["RateDate"]).group(1)) / 1000),
              Close=q["LastRate"])
        for q in r.json()["Data"]
    ]


def get_cache_id(fund_id, page):
    return '{0}@{1}'.format(fund_id, page)
