import logging

import boto3
from botocore.exceptions import ClientError
from opentelemetry import trace

from models.Portfolio import Portfolio

dyn_resource = boto3.resource('dynamodb')
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class Dynamo:
    @staticmethod
    def get_item(table_name: str, query: dict):
        with tracer.start_as_current_span(
                "get_item",
                attributes={'attr.table_name': table_name, 'attr.query': query}):
            try:
                table = dyn_resource.Table(table_name)
                response = table.get_item(Key=query)

                if 'Item' in response:
                    return response['Item']
                else:
                    logger.error('item not found')
                    return {'message': 'item not found'}
                    # raise ValueError(f'item not found {query}')
            except ClientError as e:
                logger.error(
                    f"{e.response['Error']['Code'], e.response['Error']['Message']}")
                raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")

    @staticmethod
    def create_item(table_name: str, item: dict | Portfolio) -> str:
        with tracer.start_as_current_span(
                "create_item",
                attributes={'table_name': table_name}):
            try:
                table = dyn_resource.Table(table_name)
                response = table.put_item(
                    Item=item,
                    ReturnValues="ALL_OLD"
                )
                return 'insert item succeeded'

            except ClientError as e:
                logger.error(
                    f"{e.response['Error']['Code'], e.response['Error']['Message']}")
                raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")

    @staticmethod
    def delete_item(table_name: str, item: dict) -> str:
        with tracer.start_as_current_span(
                "delete_item",
                attributes={'table_name': table_name}):
            try:
                table = dyn_resource.Table(table_name)
                response = table.delete_item(
                    Key=item,
                    ReturnValues="ALL_OLD"
                )
                return 'delete item success'
            except ClientError as e:
                logger.error(
                    f"{e.response['Error']['Code'], e.response['Error']['Message']}")
                raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")

    # todo create a general update handlers function
    @staticmethod
    def update_user_password(table_name: str, item: dict) -> str:
        with tracer.start_as_current_span(
                "update_item",
                attributes={'attr.table_name': table_name}):
            name = item["name"]
            password = item["password"]
            try:
                table = dyn_resource.Table(table_name)
                response = table.update_item(
                    Key={'name': name},
                    UpdateExpression="set password=:p",
                    ExpressionAttributeValues={
                        ':p': password},
                    ReturnValues="UPDATED_NEW")
                print(response)
                return 'update item success'
            except ClientError as e:
                logger.error(
                    f"{e.response['Error']['Code'], e.response['Error']['Message']}")
                raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")

    @staticmethod
    def update_account_balance(table_name: str, item: dict | list) -> str:
        with tracer.start_as_current_span(
                "update_balance",
                attributes={'attr.table_name': table_name}):
            name = item["name"]
            balance = item["balance"]
            try:
                table = dyn_resource.Table(table_name)
                response = table.update_item(
                    Key={'name': name},
                    UpdateExpression="set balance=:p",
                    ExpressionAttributeValues={
                        ':p': balance},
                    ReturnValues="UPDATED_NEW")
                return 'update item success'
            except ClientError as e:
                logger.error(
                    f"{e.response['Error']['Code'], e.response['Error']['Message']}")
                raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")
