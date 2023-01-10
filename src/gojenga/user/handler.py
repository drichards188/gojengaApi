import logging

from botocore.exceptions import ClientError

from storage.dynamo import get_item, create_item

logger = logging.getLogger(__name__)


def get_user(username: str) -> dict:
    try:
        user = get_item('users', 'Account', username)
        return user
    except Exception as e:
        logger.info(f'error {e}')
        raise ValueError(e)

def create_user(username: str, balance: float) -> str:
    try:
        resp = create_item('usersTest', {'Account': 'losey',
        'Amount': '200'})
        return resp
    except Exception as e:
        logger.info(f'error {e}')
        raise ValueError(e)
