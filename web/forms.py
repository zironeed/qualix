from django import forms


class RequestCallJsonRpcForm(forms.Form):
    method_name = forms.CharField(max_length=255, label='Имя метода')
    parameters = forms.JSONField(label='Параметры', required=False)
