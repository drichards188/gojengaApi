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
    def handle_get_user(username: str, is_test: bool) -> dict:
        with tracer.start_as_current_span(
                "handle_get_user",
                attributes={'attr.username': username, 'attr.is_test': is_test},
                kind=trace.SpanKind.SERVER
        ):
            table_name: str = 'users'
            if is_test:
                table_name = 'usersTest'
            try:
                user = Dynamo.get_item(table_name, 'name', username)
                return user
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_create_user(username: str, password: str, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_create_user",
                attributes={'username': username, 'attr.is_test': is_test}
        ):
            table_name: str = 'users'
            if is_test:
                table_name = 'usersTest'
            try:
                resp = Dynamo.create_item(table_name, {'name': username,
                                                       'password': password})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_update_user(username: str, password: str, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_update_user",
                attributes={'attr.username': username, 'is_test': is_test}):
            table_name: str = 'users'
            if is_test:
                table_name = 'usersTest'
            try:
                resp = Dynamo.update_user_password(table_name, {'name': username,
                                                                'password': password})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_delete_user(username: str, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_delete_user",
                attributes={'username': username, 'is_test': is_test}):
            table_name: str = 'users'
            if is_test:
                table_name = 'usersTest'
            try:
                resp = Dynamo.delete_item(table_name, {'name': username})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)
