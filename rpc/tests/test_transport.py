from unittest import TestCase
from unittest.mock import MagicMock, patch

from rpc.exceptions import TransportError
from rpc.transport import HttpsTransport


class HttpsTransportTest(TestCase):

    @staticmethod
    def create_transport():
        return HttpsTransport(
            endpoint='https://example.com/rpc',
            certificate='cert',
            key='key',
        )

    @patch('rpc.transport.http.client.HTTPSConnection')
    @patch('rpc.transport.ssl.create_default_context')
    def test_request(self, _, https_conn):
        conn = https_conn.return_value
        response = MagicMock()
        conn.getresponse.return_value = response

        transport = self.create_transport()
        result = transport.request(
            method='POST',
            url='/rpc',
            body='{"au": "th"}',
            headers={
                'Content-Type': 'application/json',
            },
        )
        conn.request.assert_called_once_with(
            method='POST',
            url='/rpc',
            body='{"au": "th"}',
            headers={
                'Content-Type': 'application/json',
            },
        )

        conn.getresponse.assert_called_once_with()
        self.assertIs(result, response)
        transport.close()

    @patch('rpc.transport.http.client.HTTPSConnection')
    @patch('rpc.transport.ssl.create_default_context')
    def test_request_raises_error(self, _, https_conn):
        conn = https_conn.return_value
        conn.request.side_effect = OSError('Отказано в подключении')

        transport = self.create_transport()

        with self.assertRaises(TransportError):
            transport.request(
                method='POST',
                url='/rpc',
                body='{}',
                headers={},
            )
        transport.close()

    @patch('rpc.transport.http.client.HTTPSConnection')
    @patch('rpc.transport.ssl.create_default_context')
    def test_close(self, _, https_conn):
        transport = self.create_transport()
        certificate = transport._certificate
        key = transport._key

        with patch('rpc.transport.os.unlink') as unlink:
            transport.close()

        https_conn.return_value.close.assert_called_once_with()
        unlink.assert_any_call(key)
        unlink.assert_any_call(certificate)
        self.assertEqual(unlink.call_count, 2)
