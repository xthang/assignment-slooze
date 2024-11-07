from fastapi import Request


def allow_explicit_origin(request: Request, response_headers: dict[str, str] | None = None) -> dict[str, str] | None:
   request_origin = request.headers.get('Origin')
   request_referer = request.headers.get('Referer')
   if request_origin:
      if not response_headers:
         response_headers = {}
      response_headers["Access-Control-Allow-Origin"] = request_origin
   elif request_referer and request_referer.startswith('http://localhost:'):
      if not response_headers:
         response_headers = {}
      response_headers["Access-Control-Allow-Origin"] = '*'
   return response_headers


def expose_all_headers(request: Request, response_headers: dict[str, str] | None = None) -> dict[str, str] | None:
   if not response_headers:
      response_headers = {}
   response_headers["access-control-expose-headers"] = "*"
   return response_headers
