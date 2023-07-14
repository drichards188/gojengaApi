import logging
from typing import List
from decimal import *

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
                resp = Dynamo.create_item(table_name, {'name': portfolio.username, 'portfolio': portfolio.portfolio})
                return resp
            except Exception as e:
                logger.info(f'error {e}')
                raise ValueError(e)

    @staticmethod
    def handle_update_portfolio(username: str, portfolio: Portfolio, is_test: bool, update_type: str) -> str:
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
                coin_portfolio: list[object] = portfolio.portfolio

                if update_type == 'buy':

                    for coin in coin_portfolio:
                        coin["amount"] = Decimal(coin["amount"])
                        print(f'coin is: {coin}')
                        print(f'coin id is: {coin["id"]}')
                        coin_id = coin["id"]
                        found_coins = [item for item in new_portfolio if item.get('id') == coin_id]
                        # this section modifies existing quantity of coin already in portfolio

                        if len(found_coins) > 0:
                            coin_index = new_portfolio.index(found_coins[0])
                            # overwrite existing coin with updated quantity
                            new_portfolio[coin_index] = coin
                        else:
                            new_portfolio.append(coin)

                elif update_type == 'sell':
                    coin_id = coin_portfolio[0]["id"]

                    new_portfolio = [coin for coin in new_portfolio if coin["id"] != coin_id]

                resp = Dynamo.create_item(table_name, {'name': portfolio.username, 'portfolio': new_portfolio})
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
