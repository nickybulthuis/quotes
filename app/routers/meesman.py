import json
import re
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from fastapi import HTTPException, APIRouter

from app.models import Quote, Message

router = APIRouter(
    prefix='/meesman',
    tags=['meesman']
)

QUOTES_REGEX = r'data:\s(\[{.*}+\])'

BASE_URL = 'https://www.meesman.nl/onze-fondsen/'
QUOTE_URL = BASE_URL + '{0}/'

funds_cache = TTLCache(maxsize=128, ttl=60 * 60 * 4)  # ttl in seconds, 4hrs.
quote_cache = TTLCache(maxsize=128, ttl=60 * 60 * 4)  # ttl in seconds, 4hrs.


@router.get(
    "/",
    response_model=List[str],
    summary="Get all available funds"
)
async def get_funds():
    if len(funds_cache) == 0:
        await fetch_funds()
    return list(funds_cache.values())


async def fetch_funds():
    r = requests.get(url=BASE_URL)

    if r.status_code != requests.codes.ok:
        raise HTTPException(status_code=502, detail={'message': 'Could not retrieve funds'})

    soup = BeautifulSoup(r.text, 'html.parser')

    # clear the caches, there might be new funds how unlikely it might be.
    quote_cache.clear()
    funds_cache.clear()

    for fund_name in soup.find_all('td', {'class': 'fund-name'}):
        fund = fund_name.find('a').get('href').split('/')[2]
        funds_cache[fund] = fund


@router.get(
    "/{fund_name}",
    response_model=List[Quote],
    summary="Delivers quotes for the specified fund by name",
    responses={502: {'description': 'When an error occurred while retrieving the quotes', 'model': Message},
               404: {'description': 'When the specified fund could not be found, or the fund is unknown',
                     'model': Message}},
)
async def get_quotes(fund_name: str):
    funds = await get_funds()

    if fund_name in funds:

        if fund_name not in quote_cache:
            await fetch_quotes(fund_name)

        return quote_cache[fund_name]
    else:
        raise HTTPException(status_code=404, detail={'message': 'Fund {0} could not be found'.format(fund_name)})


async def fetch_quotes(fund_name: str):

    r = requests.get(url=QUOTE_URL.format(fund_name))

    if r.status_code == requests.codes.ok:

        quotes: List[Quote] = []

        for result in re.findall(QUOTES_REGEX, str(r.text)):
            quotes += [Quote(Date=datetime.strptime(q['x'], '%Y-%m-%dT%H:%M:%S'), Close=q['y'])
                       for q in json.loads(result)]

        quote_cache[fund_name] = quotes

    else:
        raise HTTPException(status_code=502, detail={'message': 'Could not retrieve quotes'})
