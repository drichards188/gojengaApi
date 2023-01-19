import decimal
import logging
from decimal import *
from opentelemetry import trace

from storage.Dynamo import Dynamo

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class AccountHandler:
    @staticmethod
    def handle_get_account(username: str, is_test: bool) -> dict:
        with tracer.start_as_current_span(
                "handle_get_account",
                attributes={'attr.username': username, 'attr.is_test': is_test},
                kind=trace.SpanKind.SERVER
        ):
            table_name: str = 'ledger'
            if is_test:
                table_name = 'ledgerTest'
            try:
                user = Dynamo.get_item(table_name, 'name', username)
                return user
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_create_account(username: str, balance: Decimal, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_create_user",
                attributes={'username': username, 'attr.is_test': is_test}
        ):
            table_name: str = 'ledger'
            if is_test:
                table_name = 'ledgerTest'
            try:
                resp = Dynamo.create_item(table_name, {'name': username,
                                                       'balance': balance})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_update_account(username: str, balance: Decimal, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_update_user",
                attributes={'attr.username': username, 'is_test': is_test}):
            table_name: str = 'ledger'
            if is_test:
                table_name = 'ledgerTest'
            try:
                resp = Dynamo.update_account_balance(table_name, {'name': username,
                                                                  'balance': balance})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)
