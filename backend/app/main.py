from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import time
import logging
from app.api import auth, agent, health
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import HeimdallException
from app.models.response import error_response

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  setup_logging()
  yield

app = FastAPI(
  title=settings.PROJECT_NAME,
  openapi_url=f"{settings.API_V1_STR}/openapi.json",
  lifespan=lifespan
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
  start_time = time.time()
  response = await call_next(request)
  duration = time.time() - start_time

  logger.info(
    "request_processed",
    extra={
      "method": request.method,
      "path": request.url.path,
      "status_code": response.status_code,
      "duration": duration
    }
  )
  return response

@app.exception_handler(HeimdallException)
async def heimdall_exception_handler(request: Request, exc: HeimdallException):
  return error_response(
    message=exc.message,
    code=exc.status_code,
    data=exc.details if exc.details else None,
  )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
  return error_response(
    message="Request validation failed",
    code=422,
    data={"errors": exc.errors()},
  )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
  logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
  return error_response(
    message="An unexpected error occurred",
    code=500,
  )

# Register routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(agent.router, prefix=f"{settings.API_V1_STR}/agent", tags=["agent"])
app.include_router(health.router, tags=["health"])


