"""Main."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.models import Base, engine
from api.views import router

from webpages.views import router_web_pages


Base.metadata.create_all(bind=engine)


def get_application() -> FastAPI:
    """Configure FastApi.

    Returns:
        Application configured.
    """
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = get_application()

app.include_router(router)
app.include_router(router_web_pages)
