from django.views.generic import FormView

from config import settings
from rpc.exceptions import JsonRpcError
from rpc.factory import create_json_rpc_client
from web.forms import RequestCallJsonRpcForm


class GetIndexView(FormView):
    form_class = RequestCallJsonRpcForm
    template_name = 'web/index.html'

    def form_valid(self, form):
        cleaned_data = form.cleaned_data

        try:
            with create_json_rpc_client(
                settings.JSON_RPC_ENDPOINT,
                settings.JSON_RPC_CERTIFICATE,
                settings.JSON_RPC_PRIVATE_KEY
            ) as client:
                result = client.call(cleaned_data['method_name'], cleaned_data['parameters'])
        except JsonRpcError as e:
            context = self.get_context_data(
                form=form,
                result=None,
                error=str(e),
            )
        else:
            context = self.get_context_data(
                form=form,
                result=result,
                error=None,
            )

        return self.render_to_response(context)
