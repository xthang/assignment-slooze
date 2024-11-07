from prisma import Json, enums, models

from src.database import db


async def send_account_invitation(from_account: models.Account, to_email: str, role: enums.OrganizationMemberRole, token: str):
   await db.tasksendemail.create({
       'category': 'account-invitation',
       'from_addr': 'admin@slooze.xyz',
       'to': [Json({'address': to_email})],
       'subject': 'Slooze Inviation',
       'html': f'''Hi,</br>
      {from_account.firstName} has invited you to be a {role}. Click the following link to sign up:</br>
      <a href="http://slooze.xyz/sign-up?invitation-token={token}">SIGN UP</a>''',
       'text': f'''Hi,
      {from_account.firstName} has invited you to be a {role}. Click the following link to sign up:
      http://slooze.xyz/sign-up?invitation-token={token}''',
       'createdBy': from_account.id
   })
