import asyncio
from typing import cast

from fastapi import Request, status
from prisma import enums

from src.types.exceptions import ApiException
from src.utils.logging import logger
from src.database import db

access_matrix = None

running = True


async def start_loading_member_role_access_cache():
   await __load_member_role_access_matrix_cache()
   logger.info(f"Access Matrix loaded: {len(cast(dict, access_matrix))}")

   loop_task = asyncio.create_task(__load_member_role_access_cache_with_interval(), name="interval-load-prompts")
   loop_task.add_done_callback(lambda x: logger.info(f"Task DONE: {x.get_name()}"))


async def __load_member_role_access_cache_with_interval():
   await asyncio.sleep(30)

   # Infinite loop to query the keys from DB after each 10s
   while running:
      try:
         await __load_member_role_access_matrix_cache()
      except BaseException as error:
         logger.exception("Load ERROR: %s", error)

      await asyncio.sleep(10)


async def __load_member_role_access_matrix_cache():
   db_access_matrix = await db.memberroleaccessmatrix.find_many(where={})
   global access_matrix
   access_matrix = {}
   for access in db_access_matrix:
      if access.endpoint not in access_matrix:
         access_matrix[access.endpoint] = {}

      access_matrix[access.endpoint][access.role] = True


async def stop_loading_member_role_access_matrix_cache():
   global running
   running = False


def check_member_role_access(request: Request):
   assert access_matrix

   endpoint = request.url.path
   account = request.user
   role = enums.OrganizationMemberRole(account['role'])

   if endpoint not in access_matrix or role not in access_matrix[endpoint]:
      raise ApiException(status.HTTP_403_FORBIDDEN, 'FORBIDDEN', 'You are not allowed to perform this request')
