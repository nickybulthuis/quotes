from fastapi import FastAPI

from app.routers import meesman, brandnewday, zwitserleven

tags_metadata = [
    {
        "name": "Brand New Day",
    }, {
        "name": "Meesman",
    }, {
        "name": "Zwitserleven",
    },
]
app = FastAPI(
    title="Quotes",
    description='''
The purpose of this project is to provide stock quotes for specific funds, by accessing the fund manager's website, by
filling in forms, or by using other APIs to request them. The stock prices are then converted into a structured format
for use in [Portfolio Performance](https://www.portfolio-performance.info/), Excel or equivalent.

It's basically trying to automate what you could do by hand.

## Supported websites

* [Brand New Day](https://brandnewday.nl)
* [Meesman](https://meesman.nl)
* [Zwitserleven](https://zwitserleven.nl)

## Disclaimer

This API is not affiliated, associated, authorized, endorsed by or in any way officially associated with the said
websites, or any of its subsidiaries or affiliates. The official websites can be found at their respective links. All 
names and related names, brands, emblems and images are registered trademarks of theirs respective owners.

Source code is available at [GitHub](https://github.com/nbult/quotes)
    ''',
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url='/',
    redoc_url=None,
)

app.include_router(meesman.router)
app.include_router(brandnewday.router)
app.include_router(zwitserleven.router)
