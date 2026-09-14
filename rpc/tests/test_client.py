from unittest import TestCase
from unittest.mock import MagicMock

from rpc.client import JsonRpcClient
from rpc.exceptions import JsonRpcTransportError, JsonRpcResponseError
from rpc.transport import Transport


class JsonRpcClientTest(TestCase):

    def setUp(self):
        self.transport = MagicMock(spec=Transport)
        self.client = JsonRpcClient(
            endpoint='https://example.com/rpc',
            transport=self.transport,
        )

    def test_call_returns_result(self):
        response = MagicMock()
        response.status = 200
        response.reason = 'OK'
        response.read.return_value = b'{"jsonrpc": "2.0", "id": 1, "result": 1}'
        self.transport.request.return_value = response

        result = self.client.call(
            method='test',
            params={'au': 'th'},
        )

        self.assertEqual(result, 1)

    def test_call_raises_response_error(self):
        response = MagicMock()
        response.status = 200
        response.reason = 'OK'
        response.read.return_value = b'abc'
        self.transport.request.return_value = response

        with self.assertRaises(JsonRpcResponseError):
            self.client.call('test')

    def test_call_raises_transport_error(self):
        response = MagicMock()
        response.status = 500
        self.transport.request.return_value = response

        with self.assertRaises(JsonRpcTransportError):
            self.client.call('test')
