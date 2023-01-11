import logging

from botocore.exceptions import ClientError
from opentelemetry.propagate import extract
from opentelemetry import trace
from opentelemetry.trace import Tracer

from storage.dynamo import get_item, create_item, update_user_password, delete_item

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def handle_get_user(username: str) -> dict:
    with tracer.start_as_current_span(
            "handle_get_user",
            kind=trace.SpanKind.SERVER
    ):
        try:
            user = get_item('usersTest', 'name', username)
            return user
        except Exception as e:
            logger.info(f'error {e}')
            raise ValueError(e)


def handle_create_user(username: str, password: str) -> str:
    with tracer.start_as_current_span("handle_create_user"):
        try:
            resp = create_item('usersTest', {'name': username,
                                             'password': password})
            return resp
        except Exception as e:
            logger.info(f'error {e}')
            raise ValueError(e)


def handle_update_user(username: str, password: str) -> str:
    with tracer.start_as_current_span("handle_update_user"):
        try:
            resp = update_user_password('usersTest', {'name': username,
                                                      'password': password})
            return resp
        except Exception as e:
            logger.info(f'error {e}')
            raise ValueError(e)


def handle_delete_user(username: str) -> str:
    with tracer.start_as_current_span("handle_delete_user"):
        try:
            resp = delete_item('usersTest', {'name': username})
            return resp
        except Exception as e:
            logger.info(f'error {e}')
            raise ValueError(e)
