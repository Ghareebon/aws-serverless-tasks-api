import time

from common import get_user_id, parse_body, response, table


def handler(event, context):
    try:
        user_id = get_user_id(event)
    except PermissionError:
        return response(401, {"message": "Unauthorized"})

    task_id = event["pathParameters"]["taskId"]
    existing = table.get_item(Key={"userId": user_id, "taskId": task_id}).get("Item")
    if not existing:
        return response(404, {"message": "Task not found"})

    body = parse_body(event)
    update_expr = ["SET updatedAt = :u"]
    expr_values = {":u": int(time.time())}

    if "title" in body:
        title = (body["title"] or "").strip()
        if not title:
            return response(400, {"message": "'title' cannot be empty"})
        update_expr.append("title = :t")
        expr_values[":t"] = title
    if "description" in body:
        update_expr.append("description = :d")
        expr_values[":d"] = body["description"]
    if "done" in body:
        update_expr.append("done = :done")
        expr_values[":done"] = bool(body["done"])

    table.update_item(
        Key={"userId": user_id, "taskId": task_id},
        UpdateExpression=", ".join(update_expr),
        ExpressionAttributeValues=expr_values,
    )
    updated = table.get_item(Key={"userId": user_id, "taskId": task_id})["Item"]
    return response(200, updated)
