import time
import uuid

from common import get_user_id, parse_body, response, table


def handler(event, context):
    try:
        user_id = get_user_id(event)
    except PermissionError:
        return response(401, {"message": "Unauthorized"})

    body = parse_body(event)
    title = (body.get("title") or "").strip()
    if not title:
        return response(400, {"message": "'title' is required"})

    now = int(time.time())
    item = {
        "userId": user_id,
        "taskId": str(uuid.uuid4()),
        "title": title,
        "description": body.get("description", ""),
        "done": bool(body.get("done", False)),
        "createdAt": now,
        "updatedAt": now,
    }
    table.put_item(Item=item)
    return response(201, item)
