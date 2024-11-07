from datetime import datetime
import pytz
from fastapi import status

from src.types.exceptions import ApiException


tz = pytz.timezone('UTC')


def check_expiry_in_seconds(exp: float, cur_time: float | None = None, raise_error: bool = True):
   if exp < (cur_time or datetime.now(tz).timestamp()):
      if raise_error:
         raise ApiException(status.HTTP_401_UNAUTHORIZED, code='TOKEN_EXPIRED', message="Token expired")
      else:
         return False
   return True


def check_expiry(exp: datetime, cur_time: datetime | None = None, raise_error: bool = True):
   if exp.replace(tzinfo=tz) < (cur_time or datetime.now(tz)):
      if raise_error:
         raise ApiException(status.HTTP_401_UNAUTHORIZED, code='TOKEN_EXPIRED', message="Token expired")
      else:
         return False
   return True
