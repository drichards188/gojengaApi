import logging
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
