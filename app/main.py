import json
import os
import traceback
from http import HTTPStatus

from app import app_logger
from app.api.api_v1.api import api_router
from app.core.config import settings
from fastapi import FastAPI
from fastapi import HTTPException as StarletteHTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response
from app.app_logger_formatter import CustomFormatter

# Set Time Zone
os.environ["TZ"] = "Asia/Kabul"

app = FastAPI(
    title="HR user management service",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# Format the system logs and store it to the logfile.log
# formatter = CustomFormatter('%(asctime)s')
# logger = app_logger.get_logger(__name__, formatter)
# status_reasons = {x.value:x.name for x in list(HTTPStatus)}

# def get_extra_info(request: Request, response: Response):
#     return {'req': {
#         'url': request.url.path,
#         'headers': {'host': request.headers['host'],
#                     'user-agent': request.headers['user-agent'],
#                     'accept': request.headers['accept']},
#         'method': request.method,
#         'httpVersion': request.scope['http_version'],
#         'originalUrl': request.url.path,
#         'query': {}
#         },
#         'res': {'statusCode': response.status_code, 'body': {'statusCode': response.status_code,
#                 'status': status_reasons.get(response.status_code)}}}
#
# def write_log_data(request, response):
#     logger.info(request.method + ' ' + request.url.path, extra={'extra_info': get_extra_info(request, response)})


# @app.middleware("http")
# async def log_request(request: Request, call_next):
#     response = await call_next(request)
#     response.background = BackgroundTask(write_log_data, request, response)
#     return response

# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as e:
#         # you probably want some kind of logging here
#         exception_class = e.__class__
#         logger.error("      " + exception_class.__name__ + ": " + str(e))
#         return Response("Internal server error", status_code=500)
#     except:
#         logger.error("uncaught exception: %s", traceback.format_exc())
#         return False
# app.middleware("http")(catch_exceptions_middleware)

# The custom error messaging for HTTP Requestes
@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(request, exception):
    exc = exception.__dict__
    response = {}
    if exc["status_code"] == 422:
        response.update({exc["detail"]["field_name"]: exc["detail"]["message"]})
    elif (
        "status" in exc["detail"]
        and "message" in exc["detail"]
        and "subscriber_id" in exc["detail"]
    ):
        response.update(
            {
                "status": exc["detail"]["status"],
                "message": exc["detail"]["message"],
                "subscriber_id": exc["detail"]["subscriber_id"],
            }
        )
    elif "status" in exc["detail"] and "message" in exc["detail"]:
        response.update(
            {"status": exc["detail"]["status"], "message": exc["detail"]["message"]}
        )
    else:
        response.update({"message": exc["detail"]})

    return ORJSONResponse(
        response,
        status_code=exc["status_code"],
    )


# This function will provide custom validatio error upon each request that comes to the
# API endpoint for POST, PUT and DELETE
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # print(f"OMG! The client sent invalid data: {exc}")
    exc_json = json.loads(exc.json())
    # response = {"message": [], "data": None}
    response = {}
    for error in exc_json:
        response.update({error["loc"][-1]: f"{error['msg']}"})
    return ORJSONResponse(response, status_code=422)


@app.exception_handler(SQLAlchemyError)
async def sqlAlchemy_exception_handler(request, exc):
    exc.__dict__
    print("SQLAlchemy Exception Started")
    print(exc)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    # logger.info("Server started listening on port: 8001")
    uvicorn.run('main:app', host="0.0.0.0", port=8001, log_level="debug", reload=True)
