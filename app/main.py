from fastapi import FastAPI

from app.routers import meesman, brandnewday

tags_metadata = [
    {
        "name": "meesman",
        "description": "<a href='https://meesman.nl'>Meesman</a>",
    }, {
        "name": "brandnewday",
        "description": "<a href='https://brandnewday.nl'>Brand New Day</a>",
    },
]
app = FastAPI(
    title="Quotes",
    description="The prices of different funds for use in <a "
                "href='https://www.portfolio-performance.info/'>Portfolio Performance</a>.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url='/',
    redoc_url=None
)

app.include_router(meesman.router)
app.include_router(brandnewday.router)
