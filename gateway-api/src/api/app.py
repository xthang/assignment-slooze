from typing import cast
from contextlib import asynccontextmanager

from starlette.middleware.base import RequestResponseEndpoint
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import prisma

from src.types.exceptions import ApiException
from src.utils.logging import logger
from src.utils.fastapi.response import allow_explicit_origin
from src.database import db
from src.security.access_matrix import start_loading_member_role_access_cache, stop_loading_member_role_access_matrix_cache

from .routes import public, protected


# API setup

@asynccontextmanager
async def lifespan(app: FastAPI):
   await db.connect()
   prisma.register(db)

   # Load the caches
   await start_loading_member_role_access_cache()

   yield

   await stop_loading_member_role_access_matrix_cache()

   # release the DB connection
   await db.disconnect()

app = FastAPI(title="Slooze Gateway API", lifespan=lifespan)


# API middlewares

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Return 429 Too Many Requests HTTP response code if requests are coming in too quickly.
limiter = Limiter(key_func=get_remote_address, default_limits=['10/10second', '20/minute'])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)  # Rate-limit all requests


@app.middleware("http")
async def process(request: Request, call_next: RequestResponseEndpoint):
   try:
      response = await call_next(request)
   except BaseException as error:
      logger.exception("!-  ERROR while processing request:")
      request.scope["error"] = error

      # Add CORS header, since CORSMiddleware won't be called
      response = JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              headers=allow_explicit_origin(request),
                              content={"error": {"message": f"Something went wrong [{type(error).__name__}]"}})

   return response


# API exception handlers

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
   request.scope["error"] = exc

   error_content = {'message': exc.detail}
   if isinstance(exc, ApiException):
      error_content['code'] = exc.code
      if exc.detail_:
         error_content["detail"] = exc.detail_
   return JSONResponse(status_code=exc.status_code,
                       headers=allow_explicit_origin(request, exc.headers),
                       content={'error': error_content})


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
   request.scope["error"] = exc

   errors = [{k: e[k] for k in e.keys() - {'input'}} if isinstance(e, dict) else e for e in exc.errors()]

   return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                       headers=allow_explicit_origin(request),
                       content={'error': {'message': "Unable to process entity",
                                          "detail": jsonable_encoder(errors)}})


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
   response = JSONResponse({"error": {"message": f"Rate limit exceeded: {exc.detail}"}},
                           status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                           headers=allow_explicit_origin(request))
   response = cast(Limiter, app.state.limiter)._inject_headers(response, request.state.view_rate_limit)
   return response


# Routers

app.include_router(public.router)
app.include_router(protected.router)
