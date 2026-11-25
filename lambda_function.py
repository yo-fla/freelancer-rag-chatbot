"""Week 2: public test API. Only fictional availability data is exposed."""
import json
import logging
import os
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_table = None


def availability_table():
    global _table
    if _table is None:
        import boto3
        from botocore.config import Config
        config = Config(connect_timeout=1, read_timeout=2,
                        retries={"mode": "standard", "total_max_attempts": 2})
        _table = boto3.resource("dynamodb", config=config).Table(os.environ["TABLE_NAME"])
    return _table


def public_availability(table):
    response = table.get_item(Key={"ownerId": os.environ.get("OWNER_ID", "demo")},
                              ConsistentRead=True)
    item = response.get("Item")
    if not item or not isinstance(item.get("canAcceptNewRequests"), bool):
        raise ValueError("Availability is not configured")
    booked = date.fromisoformat(item["bookedUntil"])
    available = date.fromisoformat(item["nextAvailableDate"])
    if available <= booked:
        raise ValueError("Invalid availability dates")
    # An explicit allowlist prevents accidental disclosure of private DB fields.
    return {"demo": True, "freelancer": "샘플 프리랜서",
            "canAcceptNewRequests": item["canAcceptNewRequests"],
            "bookedUntil": booked.isoformat(),
            "nextAvailableDate": available.isoformat(),
            "timezone": "Asia/Seoul", "updatedAt": item["updatedAt"],
            "source": "Amazon DynamoDB"}


def lambda_handler(event, context, table=None):
    request = event.get("requestContext", {})
    path = event.get("rawPath", "/")
    method = request.get("http", {}).get("method", "GET")
    request_id = getattr(context, "aws_request_id", request.get("requestId", "local"))
    content_type = "application/json; charset=utf-8"
    if method != "GET":
        status, body = 405, {"message": "GET 요청만 사용할 수 있습니다."}
    elif path == "/health":
        status, body = 200, {"status": "ok", "service": "freelancer-chatbot",
                             "stage": "week2", "message": "AWS 테스트 API가 정상 실행 중입니다."}
    elif path == "/availability":
        try:
            body = public_availability(table if table is not None else availability_table())
            status = 200
        except Exception as error:
            logger.error(json.dumps({"event": "availability_error", "requestId": request_id,
                                     "errorType": type(error).__name__}))
            status, body = 503, {"message": "현재 일정을 확인할 수 없습니다. 잠시 후 다시 확인해 주세요."}
    elif path == "/":
        status = 200
        content_type = "text/html; charset=utf-8"
        body = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    else:
        status, body = 404, {"message": "요청한 경로가 없습니다."}
    logger.info(json.dumps({"event": "request", "requestId": request_id,
                            "path": path, "method": method, "status": status}))
    headers = {"Content-Type": content_type, "Cache-Control": "no-store",
               "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
               "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'"}
    if status == 405:
        headers["Allow"] = "GET"
    return {"statusCode": status, "headers": headers,
            "body": body if content_type.startswith("text/html") else json.dumps(body, ensure_ascii=False)}

