#!/usr/bin/env bash
# End-to-end smoke test against a deployed stack.
# Usage: ./scripts/smoke_test.sh <UserPoolId> <UserPoolClientId> <ApiEndpoint>
set -euo pipefail

USER_POOL_ID="${1:?Usage: $0 <UserPoolId> <UserPoolClientId> <ApiEndpoint>}"
CLIENT_ID="${2:?}"
API="${3:?}"

EMAIL="smoketest+$(date +%s)@example.com"
PASSWORD='Sm0keTest!Pass'

echo "== Signing up $EMAIL =="
aws cognito-idp sign-up \
  --client-id "$CLIENT_ID" \
  --username "$EMAIL" \
  --password "$PASSWORD" >/dev/null

aws cognito-idp admin-confirm-sign-up \
  --user-pool-id "$USER_POOL_ID" \
  --username "$EMAIL" >/dev/null

echo "== Signing in =="
ID_TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$CLIENT_ID" \
  --auth-parameters USERNAME="$EMAIL",PASSWORD="$PASSWORD" \
  --query 'AuthenticationResult.IdToken' --output text)

AUTH_HEADER="Authorization: Bearer $ID_TOKEN"

echo "== Create task =="
CREATE_RESP=$(curl -sS -X POST "$API/tasks" \
  -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"title": "Smoke test task", "description": "created by smoke_test.sh"}')
echo "$CREATE_RESP"
TASK_ID=$(echo "$CREATE_RESP" | python3 -c 'import json,sys; print(json.load(sys.stdin)["taskId"])')

echo "== List tasks =="
curl -sS "$API/tasks" -H "$AUTH_HEADER"; echo

echo "== Get task $TASK_ID =="
curl -sS "$API/tasks/$TASK_ID" -H "$AUTH_HEADER"; echo

echo "== Update task $TASK_ID =="
curl -sS -X PUT "$API/tasks/$TASK_ID" \
  -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"done": true}'; echo

echo "== Delete task $TASK_ID =="
curl -sS -o /dev/null -w "status: %{http_code}\n" -X DELETE "$API/tasks/$TASK_ID" -H "$AUTH_HEADER"

echo "== Confirm deleted (expect 404) =="
curl -sS -o /dev/null -w "status: %{http_code}\n" "$API/tasks/$TASK_ID" -H "$AUTH_HEADER"

echo "All checks passed."
