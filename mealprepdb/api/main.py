from .._version import VERSION
from .. import config

import orjson
from .base import orjson_serializer, HyperModel
from .deps import db

# from .auth import auth0

from sqlalchemy.ext.asyncio import create_async_engine
import sqlalchemy as sa

from aiodal.oqm.views import AiodalHTTPException


from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware import cors
from fastapi.responses import ORJSONResponse, Response
from fastapi.utils import is_body_allowed_for_status_code
from fastapi.encoders import jsonable_encoder

import sys

from .ingredient.route import router as ingredient_router
from .dish.route import router as dish_router

description = """ 
Database backend for Meal Prepping.
"""


# app config
app = FastAPI(
    title="mealprepdb",
    version=VERSION,
    description=description,
    debug=config.DEBUG,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_origin_regex=config.ALLOW_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=[
        "Authorization",
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
    ],
    max_age=60 * 30,
)

# initiate HATEOAS helper model
HyperModel.init_app(app)


@app.exception_handler(AiodalHTTPException)
async def aiodal_httpexception_handler(
    req: Request, exc: AiodalHTTPException
) -> ORJSONResponse | Response:
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)

    return ORJSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=headers
    )


# improve some logging for unhandled exception
# this ensures uvicorn logs traces on the server even if debug = False which I think is useful
import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.getLevelName(logging.INFO))


@app.exception_handler(Exception)
async def unhandled_exception_error(req: Request, exc: Exception) -> ORJSONResponse:
    host = getattr(getattr(req, "client", None), "host", None)
    port = getattr(getattr(req, "client", None), "port", None)

    url = f"{req.url.path}?{req.query_params}" if req.query_params else req.url.path

    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)

    logger.error(
        f'{host}:{port} - "{req.method} {url}" 500 Internal Server Error \n----<{exception_name}: {exception_value}> \n {exception_traceback}'
    )
    return ORJSONResponse(status_code=500, content={"detail": "Internal Server Error."})


@app.on_event("startup")
async def startup() -> None:  # configure and load postgres
    engine = create_async_engine(
        config.POSTGRES_URI,
        max_overflow=int(config.MAX_OVERFLOW),
        pool_size=int(config.POOL_SIZE),
        json_serializer=orjson_serializer,
        json_deserializer=orjson.loads,
    )
    metadata = sa.MetaData()
    # auth0.initialize_jwks()
    await db.reflect(engine, metadata)  # reflect the tables and initialize a session


router = APIRouter(prefix="/v1")

app.include_router(router)
app.include_router(ingredient_router)
app.include_router(dish_router)
