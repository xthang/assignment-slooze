from typing import Any, Dict
from fastapi import HTTPException, WebSocketException


class ApiException(HTTPException):
   def __init__(self, status_code: int, code: str, message: str, detail: Any = None, headers: Dict[str, str] | None = None):
      super().__init__(status_code, message, headers)
      self.code = code
      self.detail_ = detail
