import os
import unittest
from unittest.mock import patch, MagicMock
import requests

from te_wrapper import ThousandEyes
from te_wrapper.auth import ThousandEyesAuth
from te_wrapper.api import ThousandEyesAPI
from te_wrapper.models import TestResult


class TestThousandEyesAuth(unittest.TestCase):
    @patch.dict(os.environ, {"TE_API_TOKEN": "env_token"}, clear=True)
    def test_init_prefers_argument_over_env(self):
        auth = ThousandEyesAuth(api_token="arg_token")
        self.assertEqual(auth.api_token, "arg_token")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_requires_token(self):
        with self.assertRaises(ValueError):
            ThousandEyesAuth()

    def test_get_headers_content_and_auth(self):
        auth = ThousandEyesAuth(api_token="abc")
        expected = {
            "Content-Type": "application/hal+json",
            "Authorization": "Bearer abc"
        }
        self.assertDictEqual(auth.get_headers(), expected)


class TestThousandEyesAPI(unittest.TestCase):
    BASE_URL = "https://api.thousandeyes.com/v7"
    AUTH_HEADERS = {"Authorization": "Bearer tok"}

    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("te_wrapper.api.requests.request")
        cls.mock_request = cls.patcher.start()
        cls.addClassCleanup(cls.patcher.stop)

    def setUp(self):
        self.api = ThousandEyesAPI(auth=MagicMock(get_headers=lambda: self.AUTH_HEADERS))
        resp = MagicMock(status_code=200, raise_for_status=lambda: None)
        resp.json.return_value = {}
        self.mock_request.return_value = resp

    def expect_call(self, method, path, **kwargs):
        url = f"{self.BASE_URL}/{path}"
        self.mock_request.assert_called_with(method, url, headers=self.AUTH_HEADERS, **kwargs)

    def test_get_request_parsing(self):
        self.mock_request.return_value.json.return_value = {"x": 1}
        data = self.api._request("GET", "foo", params={"q": "v"})
        self.assertEqual(data, {"x": 1})
        self.expect_call("GET", "foo", params={"q": "v"})

    def test_post_request_sends_json_body(self):
        self.mock_request.return_value.json.return_value = {"y": True}
        data = self.api._request("POST", "foo", params={"a": 1})
        self.assertEqual(data, {"y": True})
        called_kwargs = self.mock_request.call_args[1]
        self.assertIn("json", called_kwargs)
        self.assertIsNone(called_kwargs.get("params"))

    def test_json_parse_error_raises(self):
        bad = MagicMock(status_code=200, raise_for_status=lambda: None)
        bad.json.side_effect = ValueError("bad")
        bad.text = "<html>"
        self.mock_request.return_value = bad
        with self.assertRaisesRegex(RuntimeError, "Error parsing JSON"):
            self.api._request("GET", "foo")

    def test_http_error_propagates(self):
        err = requests.exceptions.HTTPError("404")
        bad = MagicMock(
            status_code=404,
            raise_for_status=lambda: (_ for _ in ()).throw(err)
        )
        self.mock_request.return_value = bad
        with self.assertRaises(requests.exceptions.HTTPError):
            self.api._request("GET", "foo")

    def test_rate_limit_raises_request_exception(self):
        bad = MagicMock(status_code=400, text="limit exceeded", raise_for_status=lambda: None)
        self.mock_request.return_value = bad
        with self.assertRaisesRegex(
            requests.exceptions.RequestException,
            r"limit exceeded \(status 400\)"
        ):
            self.api._request("GET", "foo")

    def test_list_tests_empty_and_nonempty(self):
        self.mock_request.return_value.json.return_value = {"tests": []}
        self.assertEqual(self.api.list_tests(), {})

        payload = {"tests": [{"testId": 10, "testName": "T", "_links": {}}]}
        self.mock_request.return_value.json.return_value = payload
        out = self.api.list_tests()
        self.assertIn(10, out)
        self.assertDictEqual(out[10], {"testName": "T", "testResultsLinks": []})


class TestTestResult(unittest.TestCase):
    def test_from_dict_valid_extracts_fields(self):
        payload = {
            "test": {"testId": 2, "testName": "X"},
            "results": [{"status": "s", "date": "2025-04-29T00:00:00Z", "metric": 5}],
        }
        tr = TestResult.from_dict(payload)
        self.assertEqual(tr.test_id, 2)
        self.assertEqual(tr.test_name, "X")
        self.assertEqual(tr.status, "s")
        self.assertIsInstance(tr.metrics, dict)

    def test_from_dict_error_cases(self):
        cases = [
            ({"test": {}, "results": [{}]},            r"Missing 'testId'"),
            ({"test": {"testId": "x"}, "results": [{}]}, r"Invalid 'testId'"),
            ({"test": {"testId": 1}, "results": [{}]},   r"Missing 'testName'"),
            ({"results": [{}]},                         r"Missing or invalid 'test'"),
            ({"test": {"testId": 1, "testName": "Z"}},   r"no test results"),
            ({"test": {"testId": 1, "testName": "Z"}, "results": ["bad"]},
                                                       r"Latest result entry is malformed"),
        ]
        for payload, pattern in cases:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(Exception, pattern):
                    TestResult.from_dict(payload)


class TestThousandEyes(unittest.TestCase):
    def test_init_with_arg_and_env(self):
        with patch.dict(os.environ, {"TE_API_TOKEN": "E"}, clear=True):
            with patch("te_wrapper.ThousandEyesAuth") as A, \
                 patch("te_wrapper.ThousandEyesAPI") as B:

                te1 = ThousandEyes(api_token="A")
                A.assert_called_once_with(api_token="A")
                B.assert_called_once_with(A.return_value)

                te2 = ThousandEyes()
                A.assert_called_with(api_token=None)
                self.assertEqual(B.call_count, 2)