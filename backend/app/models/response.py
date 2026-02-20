from typing import Any, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class StandardResponse(BaseModel):
  status: bool
  code: int
  message: str
  data: Optional[Any] = None


def success_response(
  data: Any = None,
  message: str = "Success",
  code: int = 200,
) -> JSONResponse:
  return JSONResponse(
    status_code=code,
    content=StandardResponse(
      status=True,
      code=code,
      message=message,
      data=data,
    ).model_dump(),
  )


def error_response(
  message: str = "An error occurred",
  code: int = 400,
  data: Any = None,
) -> JSONResponse:
  return JSONResponse(
    status_code=code,
    content=StandardResponse(
      status=False,
      code=code,
      message=message,
      data=data,
    ).model_dump(),
  )
