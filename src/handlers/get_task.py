from common import get_user_id, response, table


def handler(event, context):
    try:
        user_id = get_user_id(event)
    except PermissionError:
        return response(401, {"message": "Unauthorized"})

    task_id = event["pathParameters"]["taskId"]
    result = table.get_item(Key={"userId": user_id, "taskId": task_id})
    item = result.get("Item")
    if not item:
        return response(404, {"message": "Task not found"})
    return response(200, item)
