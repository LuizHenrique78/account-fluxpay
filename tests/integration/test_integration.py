from utilities.frameworks.aws_event.api_gateway_v2_event import APIGatewayV2Event

from main import lambda_create_account


class FakeContext:
    function_name = "test_lambda"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:region:account-id:function:test_lambda"
    aws_request_id = "test-request-id"


def test_create_account():
    event_data = {
        "version": "2.0",
        "routeKey": "POST /accounts/create",
        "rawPath": "/accounts/create",
        "rawQueryString": "",
        "headers": {},
        "requestContext": {
            "accountId": "account-123",
            "http": {
                "method": "POST",
                "path": "/accounts/create"
            }
        },
        "body": '{"tenant_id": "tenant123", "owner_id": "owner456"}',
        "isBase64Encoded": False
    }

    event_data = APIGatewayV2Event(**event_data)
    event = event_data.model_dump(by_alias=True)

    context = FakeContext()
    response: tuple[dict, int] = lambda_create_account(event, context)
    assert response[1] == 200, f"Expected status code 200, got {response[1]}"
    assert "Account created successfully" in response[0]["message"], "Expected success message not found"



if __name__ == "__main__":
    test_create_account()
