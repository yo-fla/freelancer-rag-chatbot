import json
import unittest
from unittest.mock import Mock
from lambda_function import lambda_handler


class ApiTest(unittest.TestCase):
    def event(self, path, method="GET"):
        return {"rawPath": path, "requestContext": {"http": {"method": method}}}

    def test_health_does_not_need_database(self):
        table = Mock()
        result = lambda_handler(self.event("/health"), None, table)
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(json.loads(result["body"])["status"], "ok")
        table.get_item.assert_not_called()

    def test_availability_reads_current_item_and_omits_private_fields(self):
        table = Mock()
        table.get_item.return_value = {"Item": {
            "ownerId": "demo", "canAcceptNewRequests": False,
            "bookedUntil": "2026-12-04", "nextAvailableDate": "2026-12-07",
            "updatedAt": "2026-11-25T10:00:00+09:00", "privateClient": "DO_NOT_EXPOSE"}}
        result = lambda_handler(self.event("/availability"), None, table)
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(json.loads(result["body"])["nextAvailableDate"], "2026-12-07")
        self.assertNotIn("DO_NOT_EXPOSE", result["body"])
        table.get_item.assert_called_once_with(Key={"ownerId": "demo"}, ConsistentRead=True)

    def test_missing_or_invalid_data_never_claims_availability(self):
        for item in [None, {"canAcceptNewRequests": True},
                     {"canAcceptNewRequests": False, "bookedUntil": "2026-12-07",
                      "nextAvailableDate": "2026-12-04"}]:
            with self.subTest(item=item):
                table = Mock()
                table.get_item.return_value = {"Item": item}
                result = lambda_handler(self.event("/availability"), None, table)
                self.assertEqual(result["statusCode"], 503)
                self.assertNotIn("canAcceptNewRequests", result["body"])

    def test_database_failure_returns_safe_error(self):
        table = Mock()
        table.get_item.side_effect = RuntimeError("internal sensitive details")
        result = lambda_handler(self.event("/availability"), None, table)
        self.assertEqual(result["statusCode"], 503)
        self.assertNotIn("internal sensitive details", result["body"])

    def test_unknown_path_and_write_method_are_rejected(self):
        self.assertEqual(lambda_handler(self.event("/missing"), None)["statusCode"], 404)
        self.assertEqual(lambda_handler(self.event("/availability", "POST"), None)["statusCode"], 405)


if __name__ == "__main__":
    unittest.main()

