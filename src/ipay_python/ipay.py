import json
import requests
from requests.auth import HTTPBasicAuth
from requests import Response
from .exceptions import BadCredentials, UnexpectedStatusCode


class IPayClient:

    BASE_URL = 'https://ipay.ge/opay/api/v1/'

    def __init__(self, client_id: str, secret_key: str) -> None:
        self.client_id = client_id
        self.secret_key = secret_key

    def _authenticate(self) -> Response:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'client_credentials'
        }

        response = requests.post(
            f'{self.BASE_URL}oauth2/token',
            headers=headers,
            data=data,
            auth=HTTPBasicAuth(username=self.client_id, password=self.secret_key)
        )

        if response.status_code == 200:
            return response
        elif response.status_code == 404:
            raise BadCredentials(response.json().get('error_message'))
        else:
            raise UnexpectedStatusCode('POST', 'oauth2/token', response.status_code, response.text)

    def _make_request(
        self,
        method: str = None,
        endpoint: str = None,
        headers: dict = None,
        data: dict = None
    ) -> Response:
        access_token = self._authenticate().json().get('access_token')

        headers['Authorization'] = f'Bearer {access_token}'

        if (content_type := headers.get('Content-Type')) and content_type == 'application/json':
            data = json.dumps(data)

        response = requests.request(method, f'{self.BASE_URL}{endpoint}', headers=headers, data=data)

        return response

    def create_order(
        self,
        intent: str = None,
        items: list = None,  # marked as optional in docs but it's required
        redirect_url: str = None,
        capture_method: str = None,  # marked as optional in docs but it's required
        purchase_units: list = None,
        **kwargs
    ) -> Response:
        payload = {
            'intent': intent,
            'items': items,
            'redirect_url': redirect_url,
            'capture_method': capture_method,
            'purchase_units': purchase_units
        }

        if len(kwargs) > 0:
            payload.update(kwargs)

        response = self._make_request(
            method='POST',
            endpoint='checkout/orders',
            headers={'Content-Type': 'application/json'},
            data=payload
        )

        if response.status_code == 200:
            return response
        else:
            raise UnexpectedStatusCode('POST', 'checkout/orders', response.status_code, response.text)

    def details(self, order_id: str) -> Response:
        response = self._make_request(
            method='GET',
            endpoint=f'checkout/payment/{order_id}',
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            return response
        else:
            raise UnexpectedStatusCode('GET', f'checkout/payment/{order_id}', response.status_code, response.text)

    def refund(self, order_id: str = None, **kwargs) -> Response:
        payload = {
            'order_id': order_id
        }

        if len(kwargs) > 0:
            payload.update(kwargs)

        response = self._make_request(
            method='POST',
            endpoint='checkout/refund',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=payload
        )

        if response.status_code == 200:
            return response
        else:
            raise UnexpectedStatusCode('POST', 'checkout/refund', response.status_code, response.text)

    def subscribe(
        self,
        order_id: str = None,
        amount: dict = None,
        **kwargs
    ) -> Response:
        payload = {
            'order_id': order_id,
            'amount': amount
        }

        if len(kwargs) > 0:
            payload.update(kwargs)

        response = self._make_request(
            method='POST',
            endpoint='checkout/payment/subscription',
            headers={'Content-Type': 'application/json'},
            data=payload
        )

        if response.status_code == 200:
            return response
        else:
            raise UnexpectedStatusCode('POST', 'checkout/payment/subscription', response.status_code, response.text)
