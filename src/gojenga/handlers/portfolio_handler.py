import logging
from typing import List

from opentelemetry import trace

from models.Portfolio import Portfolio
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

    @staticmethod
    def handle_create_portfolio(username: str, portfolio: Portfolio, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_create_portfolio",
                attributes={'username': username, 'attr.is_test': is_test}
        ):
            table_name: str = 'portfolio'
            if is_test:
                table_name = 'portfolioTest'
            try:
                resp = Dynamo.create_item(table_name, {'name': portfolio.name, 'portfolio': portfolio.portfolio})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_update_portfolio(username: str, portfolio: Portfolio, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_create_portfolio",
                attributes={'username': username, 'attr.is_test': is_test}
        ):
            table_name: str = 'portfolio'
            if is_test:
                table_name = 'portfolioTest'
            try:
                original_portfolio = PortfolioHandler.handle_get_portfolio(username, is_test)

                new_portfolio: list = original_portfolio['portfolio']

                # todo handle adding more of a coin
                for coin in portfolio.portfolio:
                    if coin.id in portfolio.portfolio:
                        coin_index = portfolio.portfolio.index(coin.id)
                        portfolio.portfolio[coin_index] = coin
                    new_portfolio.append(coin)

                resp = Dynamo.create_item(table_name, {'name': portfolio.name, 'portfolio': new_portfolio})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_delete_portfolio(username: str, is_test: bool) -> str:
        with tracer.start_as_current_span(
                "handle_delete_portfolio",
                attributes={'username': username, 'is_test': is_test}):
            table_name: str = 'portfolio'
            if is_test:
                table_name = 'portfolioTest'
            try:
                resp = Dynamo.delete_item(table_name, {'name': username})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)
