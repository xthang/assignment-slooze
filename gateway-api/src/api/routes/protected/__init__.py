from fastapi import APIRouter, Depends

from src.security.auth import jwt_validation
from src.security.access_matrix import check_member_role_access

from ...endpoints import (
    account,
    order,
    payment
)


router = APIRouter(
    tags=["APIs for authenticated users"],
    dependencies=[Depends(jwt_validation), Depends(check_member_role_access)],
)


router.add_api_route('/invite-user', account.invite_user, methods=['POST'])

router.add_api_route('/order-create', order.create, methods=['POST'])
router.add_api_route('/order-tracking', order.tracking, methods=['GET'])

router.add_api_route('/payment-create', payment.create, methods=['POST'])
router.add_api_route('/pay', payment.pay, methods=['POST'])
