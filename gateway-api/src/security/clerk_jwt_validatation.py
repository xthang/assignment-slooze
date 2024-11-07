from typing import Annotated, Optional

import jwt
from pydantic import ValidationError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.types.exceptions import ApiException
from src.utils.logging import logger
from src.constants.env import JWT_PUBLIC_KEY


token_auth_scheme = HTTPBearer(description="Clerk Bearer token authentication")


class ClerkJwtValidation:
   def __init__(self, signed_algorithm: str = 'RS256', public_key: Optional[bytes] = None, salt: bytes = b"", info: bytes = b"Clerk Generated Encryption Key",):
      # Clerk's Security algorithm
      self.signed_algorithm = signed_algorithm
      # Public key provided by Clerk Dashboard
      self.public_key = public_key or JWT_PUBLIC_KEY

   def __call__(self, request: Request,
                http_authorization_credentials: Annotated[HTTPAuthorizationCredentials, Depends(token_auth_scheme)]):
      if not http_authorization_credentials.scheme == "Bearer":
         raise ApiException(status_code=403,
                            code='INVALID_AUTH_SCHEME',
                            message="Invalid authentication scheme.")
      return self.verify_jwt(request, http_authorization_credentials.credentials)

   def verify_jwt(self, request: Request, jwtoken: str):
      try:
         payload = jwt.decode(jwtoken, key=self.public_key,
                              algorithms=[self.signed_algorithm])

         # if "exp" not in payload:
         #     raise ApiException(
         #         status_code=401, detail="Invalid JWT format, missing exp")
         # check_expiry_in_seconds(float(payload['exp']))

         request.scope["user"] = {"id": payload["sub"],
                                  'role': payload['role'],
                                  "org-id": payload["org-id"] if "org-id" in payload else None}

         return payload
      except HTTPException as error:
         raise error
      except (jwt.PyJWTError, ValidationError) as error:
         request.scope["auth"] = {"token": jwtoken}

         try:
            payload = jwt.decode(jwtoken, key=self.public_key,
                                 algorithms=[self.signed_algorithm], verify=False, options={"verify_signature": False, "verify_exp": False})
            request.scope["user"] = {"id": payload["sub"],
                                     "org-id": payload["org-id"] if "org-id" in payload else None}
         except BaseException:
            logger.exception('!-  Error while decode jwt:')

         raise ApiException(status_code=status.HTTP_403_FORBIDDEN,
                            code='JWT_VALIDATION_ERROR',
                            message=f"Could not validate credentials [{type(error).__name__}: {error}]")
      except BaseException as error:
         logger.exception("!-  Verify JWT ERROR: {e}")
         if isinstance(request, Request):
            raise ApiException(status_code=500,
                               code='SOMETHING_WENT_WRONG',
                               message=f"Something went wrong [{type(error).__name__}: {error}]")
         else:
            raise WsException(code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              error_code='SOMETHING_WENT_WRONG',
                              reason=f"Something went wrong [{type(error).__name__}: {error}]")
