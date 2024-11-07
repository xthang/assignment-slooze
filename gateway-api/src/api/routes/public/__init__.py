from fastapi import APIRouter

from ...endpoints import (
    account
)


router = APIRouter(tags=["Public APIs"])


# API endpoints

router.add_api_route('/sign-up-by-invitation', account.sign_up_by_invitation, methods=['POST'])

router.add_api_route('/sign-in', account.sign_in, methods=['POST'])
