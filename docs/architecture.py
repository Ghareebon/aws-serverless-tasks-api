"""
Generates docs/architecture.png.

Requires the `diagrams` python package and the `graphviz` system package:
    pip install diagrams
    apt-get install graphviz   # or: brew install graphviz

Run from the repo root:
    python3 docs/architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.database import Dynamodb
from diagrams.aws.security import Cognito
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.client import Client

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.4",
}

with Diagram(
    "Serverless Tasks REST API",
    filename="docs/architecture",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    client = Client("Client\n(web / mobile / curl)")

    with Cluster("AWS Cloud"):
        cognito = Cognito("Cognito\nUser Pool\n(JWT auth)")
        api = APIGateway("API Gateway\n(HTTP API)")

        with Cluster("Lambda functions (Python 3.12)"):
            create_fn = Lambda("createTask\nPOST /tasks")
            list_fn = Lambda("listTasks\nGET /tasks")
            get_fn = Lambda("getTask\nGET /tasks/{id}")
            update_fn = Lambda("updateTask\nPUT /tasks/{id}")
            delete_fn = Lambda("deleteTask\nDELETE /tasks/{id}")

        table = Dynamodb("DynamoDB\nTasksTable\n(userId, taskId)")
        logs = Cloudwatch("CloudWatch\nLogs & X-Ray")

        client >> Edge(label="1. sign up / sign in") >> cognito
        cognito >> Edge(label="2. JWT", style="dashed") >> client
        client >> Edge(label="3. HTTPS + Bearer JWT") >> api
        api >> Edge(label="JWT authorizer") >> cognito
        api >> create_fn
        api >> list_fn
        api >> get_fn
        api >> update_fn
        api >> delete_fn

        create_fn >> table
        list_fn >> table
        get_fn >> table
        update_fn >> table
        delete_fn >> table

        [create_fn, list_fn, get_fn, update_fn, delete_fn] >> Edge(style="dotted") >> logs
