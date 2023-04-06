import logging
from opentelemetry import trace

from storage.Dynamo import Dynamo

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class PortfolioHandler:
    @staticmethod
    def handle_get_portfolio(username: str, is_test: bool) -> dict:
        with tracer.start_as_current_span(
                "handle_get_portfolio",
                attributes={'attr.username': username, 'attr.is_test': is_test},
                kind=trace.SpanKind.SERVER
        ):
            table_name: str = 'portfolio'
            if is_test:
                table_name = 'portfolioTest'
            try:
                user = Dynamo.get_item(table_name, {'name': username})
                return user
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)
