import logging

import boto3
from botocore.exceptions import ClientError
from opentelemetry import trace

dyn_resource = boto3.resource('dynamodb')
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class Dynamo:
    @staticmethod
    def get_item(table_name: str, key: str, value: str):
        with tracer.start_as_current_span(
                "get_item",
                attributes={'attr.table_name': table_name, 'attr.key': key, 'attr.value': value}):
            try:
                table = dyn_resource.Table(table_name)
                response = table.get_item(Key={key: value})

                if 'Item' in response:
                    return response['Item']
                else:
                    logger.error('item not found')
                    raise ValueError('item not found')
            except ClientError as e:
                logger.error(
                    f"{e.response['Error']['Code'], e.response['Error']['Message']}")
                raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")

    @staticmethod
    def create_item(table_name: str, item: dict) -> str:
        with tracer.start_as_current_span(
                "create_item",
                attributes={'table_name': table_name}):
            try:
                table = dyn_resource.Table(table_name)
                response = table.put_item(
                    Item=item
                )
                return 'insert item success'
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
                    Key=item
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
