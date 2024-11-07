from fastapi import Depends, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.types.exceptions import ApiException
from src.security.clerk_jwt_validatation import ClerkJwtValidation


token_auth_scheme = HTTPBearer(
    description="Clerk Bearer token authentication", auto_error=False)

jwt_validation = ClerkJwtValidation()


def jwt_auth(request: Request, credentials: HTTPAuthorizationCredentials = Security(token_auth_scheme)):
   if not credentials:
      return None

   return jwt_validation(request, credentials)


async def auth(request: Request, jwt=Depends(jwt_auth)):
   if not jwt:
      raise ApiException(status_code=status.HTTP_401_UNAUTHORIZED,
                         code='NOT_AUTHENTICATED',
                         message="Not authenticated")

   return jwt
