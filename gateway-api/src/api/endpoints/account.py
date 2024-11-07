from typing import Annotated
import re
from hashlib import sha256

from fastapi import Form, Request, status
from prisma import enums, errors
import jwt

from src.types.exceptions import ApiException
from src.constants.env import JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, PASSWORD_SHA256_SALT
from src.database import db
from src.utils.send_email.account import send_account_invitation


async def invite_user(request: Request, email: Annotated[str, Form()], role: Annotated[str, Form()]):
   from_account = request.user
   from_account_ = await db.account.find_unique_or_raise({'id': from_account['id']})
   role = enums.OrganizationMemberRole(role)

   token = jwt.encode({
       'email': email,
       'org-id': from_account['org-id'],
       'role': role,
       'invited-by': from_account['id']
   }, JWT_PRIVATE_KEY, 'RS256')

   await send_account_invitation(from_account_, email, role, token)

   return {'result': 'ok'}


async def sign_up_by_invitation(token: Annotated[str, Form()],
                                username: Annotated[str, Form()],
                                first_name: Annotated[str, Form()],
                                last_name: Annotated[str, Form()],
                                password: Annotated[str, Form()]):
   token_payload = jwt.decode(token, JWT_PUBLIC_KEY, ['RS256'])
   email = token_payload['email']
   org_id = token_payload['org-id']
   role = enums.OrganizationMemberRole(token_payload['role'])
   invited_by = token_payload['invited-by']

   # validate & check
   assert re.compile('[a-z0-9]+').match(username)
   assert re.compile('[a-zA-Z]+').match(first_name)
   assert re.compile('[a-zA-Z]+').match(last_name)
   assert re.compile('[a-zA-Z0-9]+').match(password)

   pw_hash = sha256(password.encode('utf-8'))
   pw_hash.update(PASSWORD_SHA256_SALT.encode('utf-8'))
   hashed_pw = pw_hash.hexdigest()

   async with db.tx() as transaction:
      # create new Account
      try:
         account = await transaction.account.create({
             'username': username, 'firstName': first_name, 'lastName': last_name,
             'password': hashed_pw,
             'createdSource': 'invitation', 'createdBy': invited_by
         })
      except errors.UniqueViolationError:
         raise ApiException(status.HTTP_400_BAD_REQUEST, 'ACCOUNT_EXISTED', 'Account already existed')

      # create new Account Alias
      await transaction.accountalias.create({
          'accountId': account.id,
          'type': enums.AccountAliasType.emailAddr, 'rawValue': email, 'contactValue': email,
          'createdBy': account.id
      })
      # add new Account to organization
      await transaction.organizationmembership.create({
          'orgId': org_id,
          'accountId': account.id,
          'role': role,
          'createdBy': account.id
      })

   return {'result': 'ok'}


async def sign_in(email: Annotated[str, Form()], password: Annotated[str, Form()]):
   account_alias = await db.accountalias.find_unique({
       'type_contactValue_isActive': {'type': enums.AccountAliasType.emailAddr, 'contactValue': email.lower(), 'isActive': True}
   })
   if not account_alias:
      raise ApiException(status.HTTP_401_UNAUTHORIZED, 'UNAUTHORIZED', 'Unauthorized')

   account = await db.account.find_unique_or_raise({'id': account_alias.accountId})

   pw_hash = sha256(password.encode('utf-8'))
   pw_hash.update(PASSWORD_SHA256_SALT.encode('utf-8'))
   hashed_pw = pw_hash.hexdigest()
   print(hashed_pw)
   if account.password != hashed_pw:
      raise ApiException(status.HTTP_401_UNAUTHORIZED, 'UNAUTHORIZED', 'Unauthorized')

   org_membership = await db.organizationmembership.find_unique_or_raise({
       'accountId_isActive': {'accountId': account.id, 'isActive': True}
   })

   access_token = jwt.encode({
       'sub': account.id,
       'email': email,
       'org-id': org_membership.orgId,
       'role': org_membership.role,
   },
       JWT_PRIVATE_KEY,
       'RS256')

   return {'access-token': access_token}
