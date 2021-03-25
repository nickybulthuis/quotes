from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from fastapi import HTTPException, APIRouter

from app.models import Quote, Message
from app.utils import clean_fund_name

router = APIRouter(
    prefix='/zwitserleven',
    tags=['Zwitserleven']
)

QUOTES_REGEX = r'data:\s(\[{.*}+\])'

FUNDS_URL = 'https://www.zwitserleven.nl/webtools/fondskoersen_2011/fondskoersen.aspx?cms_id=14421&amp;cms_template' \
            '=NL2015+Infopagina'

cache = TTLCache(maxsize=128, ttl=60 * 60 * 4)  # ttl in seconds, 4hrs.


@router.get(
    "/",
    response_model=List[str],
    summary="Get all available funds"
)
async def get_funds():
    if len(cache) == 0:
        await fetch_funds()
    return list(cache.keys())


async def fetch_funds():
    r = requests.get(url=FUNDS_URL)

    if r.status_code != requests.codes.ok:
        raise HTTPException(status_code=502, detail={'message': 'Could not retrieve funds'})

    soup = BeautifulSoup(r.text, 'html.parser')
    cache.clear()

    for fund in soup.find_all('tr', {'class': 'showFonds'}):
        name = clean_fund_name(fund.find('a').text.strip())

        quotes = fund.find_all('td', {'class': 'koers'})
        close = float(quotes[0].text.strip().replace(',', '.'))
        date = datetime.strptime(quotes[1].text.strip(), '%d-%m-%Y')

        cache[name] = [Quote(Date=date, Close=close)]


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
        return cache[fund_name]
    else:
        raise HTTPException(status_code=404, detail={'message': 'Fund {0} could not be found'.format(fund_name)})
