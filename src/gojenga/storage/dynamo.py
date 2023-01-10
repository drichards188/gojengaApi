import logging

import boto3
from botocore.exceptions import ClientError

dyn_resource = boto3.resource('dynamodb')
logger = logging.getLogger(__name__)


def get_item(table_name: str, key: str, value: str):
    try:
        table = dyn_resource.Table(table_name)
        response = table.get_item(Key={key: value})

        if 'item' in response:
            return response['Item']
        else:
            logger.error('item not found')
            raise ValueError('item not found')
    except ClientError as e:
        logger.error(
            f"{e.response['Error']['Code'], e.response['Error']['Message']}")
        raise Exception(f"dynamo error {e.response['Error']['Code']} and msg {e.response['Error']['Message']}")


# todo how to add multiple key value pairs
def create_item(table_name: str, item: dict) -> str:

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
