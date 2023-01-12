import logging

from botocore.exceptions import ClientError
from opentelemetry.propagate import extract
from opentelemetry import trace
from opentelemetry.trace import Tracer

from storage.dynamo import Dynamo

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class UserHandler:
    @staticmethod
    def handle_get_user(username: str) -> dict:
        with tracer.start_as_current_span(
                "handle_get_user",
                kind=trace.SpanKind.SERVER
        ):
            try:
                user = Dynamo.get_item('usersTest', 'name', username)
                return user
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_create_user(username: str, password: str) -> str:
        with tracer.start_as_current_span("handle_create_user"):
            try:
                resp = Dynamo.create_item('usersTest', {'name': username,
                                                 'password': password})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_update_user(username: str, password: str) -> str:
        with tracer.start_as_current_span("handle_update_user"):
            try:
                resp = Dynamo.update_user_password('usersTest', {'name': username,
                                                          'password': password})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_delete_user(username: str) -> str:
        with tracer.start_as_current_span("handle_delete_user"):
            try:
                resp = Dynamo.delete_item('usersTest', {'name': username})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)
