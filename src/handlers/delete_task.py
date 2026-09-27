from common import get_user_id, response, table


def handler(event, context):
    try:
        user_id = get_user_id(event)
    except PermissionError:
        return response(401, {"message": "Unauthorized"})

    task_id = event["pathParameters"]["taskId"]
    existing = table.get_item(Key={"userId": user_id, "taskId": task_id}).get("Item")
    if not existing:
        return response(404, {"message": "Task not found"})

    table.delete_item(Key={"userId": user_id, "taskId": task_id})
    return response(204)
