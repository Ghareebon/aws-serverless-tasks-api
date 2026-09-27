from boto3.dynamodb.conditions import Key

from common import get_user_id, response, table


def handler(event, context):
    try:
        user_id = get_user_id(event)
    except PermissionError:
        return response(401, {"message": "Unauthorized"})

    result = table.query(KeyConditionExpression=Key("userId").eq(user_id))
    return response(200, {"tasks": result.get("Items", [])})
