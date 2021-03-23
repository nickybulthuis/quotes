from fastapi import FastAPI

from app.routers import meesman, brandnewday

tags_metadata = [
    {
        "name": "Meesman",
    }, {
        "name": "Brand New Day",
    },
]
app = FastAPI(
    title="Quotes",
    description='''
This API offers [Meesman](https://meesman.nl) and [Brand New Day](https://brandnewday.nl) customers an opportunity 
to use stock prices in, for example, Portfolio Performance, Excel or equivalent. 

## Portfolio Performance
[Portfolio Performance](https://www.portfolio-performance.info/) is an open-source tool to track your investments. It 
allows you to automatically download stock prices or quotes for your securities.

#### Meesman
Use the following settings to download Historical Quotes for *Meesman* funds. For Latest Quote, use the (same as 
historical quotes) option.
|Setting|Value|
| ----------- | ----------- |
|Provider|JSON|
|Feed URL|https://quotes.totalechaos.nl/meesman/aandelen-wereldwijd-totaal|
|Path to Date|$.[*].Date|
|Path to Close|$.[*].Close|

You can replace **aandelen-wereldwijd-totaal** with any of the other available fund names.

#### Brand New Day
Use the following settings to download Historical Quotes for *Brand New Day* funds. For Latest Quote, use the (same 
as historical quotes) option.
|Setting|Value|
| ----------- | ----------- |
|Provider|JSON|
|Feed URL|https://quotes.totalechaos.nl/brandnewday/bnd-wereld-indexfonds-c-unhedged?page={PAGE}|
|Path to Date|$.[*].Date|
|Path to Close|$.[*].Close|

You can replace **bnd-wereld-indexfonds-c-unhedged** with any of the other available fund names.

## Excel 
Excel has the ability to download json data from the web and transform it in to a table. To use the API in excel, 
follow the following steps.

1. Navigate to the Data tab.
2. Click 'From Web' and use URL: https://quotes.totalechaos.nl/meesman/aandelen-wereldwijd-totaal.
3. Excel will now load the JSON data and you should see a list of 'Records'.
4. Click 'To Table' on the 'Transform' tab.
5. Click the 'Expand Column' icon on the Column 1 header.
6. Select the columns you wish (Date, Close) and click Ok.
7. For each column, click the type icon in the header and select the appropriate type (Date/Time and Decimal).
8. Click 'Close and Load' and the should now see the stock prices for your fund.


## Disclaimer
This API is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Meesman or 
Brand New Day, or any of its subsidiaries or its affiliates. The official websites of [Meesman](https://meesman.nl) 
and [Brand New Day](https://brandnewday.nl) can by found by their respective links.

The names Meesman and Brand New Day as well as related names, marks, emblems and images are 
registered trademarks of their respective owners.

Source code is available at [GitHub](https://github.com/nbult/quotes)
    ''',
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url='/',
    redoc_url=None,
)

app.include_router(meesman.router)
app.include_router(brandnewday.router)
