from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.test import RequestFactory

from rpc.exceptions import JsonRpcError
from web.views import GetIndexView


class GetIndexViewTest(TestCase):

    @staticmethod
    def get_form():
        return MagicMock(
            cleaned_data={
                'method_name': 'test',
                'parameters': {'au': 'th'}
            }
        )

    def setUp(self):
        self.factory = RequestFactory()

    @patch('web.views.create_json_rpc_client')
    def test_returns_result(self, create_client):
        client = create_client.return_value.__enter__.return_value
        client.call.return_value = {'result': 'ok'}

        form = self.get_form()
        view = GetIndexView()
        view.request = self.factory.post('/')
        view.render_to_response = MagicMock()
        view.form_valid(form)

        context = view.render_to_response.call_args.args
        self.assertGreater(len(context), 0)
        self.assertEqual(context[0]['result'], {'result': 'ok'})
        self.assertIsNone(context[0]['error'])

    @patch('web.views.create_json_rpc_client')
    def test_returns_error(self, create_client):
        client = create_client.return_value.__enter__.return_value
        client.call.side_effect = JsonRpcError('RPC error')

        form = self.get_form()
        view = GetIndexView()
        view.request = self.factory.post('/')
        view.render_to_response = MagicMock()
        view.form_valid(form)

        context = view.render_to_response.call_args.args
        self.assertGreater(len(context), 0)
        self.assertIsNone(context[0]['result'])
        self.assertEqual(context[0]['error'], 'RPC error')
