from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Union

from dacite import from_dict, Config

from konduto.api.clients import KondutoHttpClient
from konduto.api.resources.order_status import OrderStatus
from konduto.api.resources.requests.order_request import OrderRequest
from konduto.api.resources.requests.order_status_request import OrderStatusRequest
from konduto.api.resources.response.error import Error
from konduto.api.resources.response.order_response import OrderResponse, Recommendation
from konduto import KONDUTO_DOMAIN

ENDPOINT = f'{KONDUTO_DOMAIN}v1/orders'.strip('/')


def _date_str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def _float_to_decimal(float_number):
    return Decimal(str(float_number))


def _datetime_str_to_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')


class OrderClientKonduto(KondutoHttpClient):

    def create(self, payload: OrderRequest) -> Union[OrderResponse, Error]:
        result = self.post(ENDPOINT, payload.json)

        if result.is_right:
            response_order = result.value['order']
            order_response = OrderResponse(id=response_order['id'], score=response_order['score'],
                                           recommendation=Recommendation(response_order['recommendation']),
                                           status=OrderStatus(str(response_order['status']).upper()))
            return order_response

        return result.value

    def change_status(self, order_id: str, payload: OrderStatusRequest) -> Union[dict, Error]:
        result = self.put(f'{ENDPOINT}/{order_id}', payload.json)

        if result.is_right:
            return result.value

        return result.value

    def load(self, order_id: str) -> Union[OrderResponse, Error]:
        result = self.get(f'{ENDPOINT}/{order_id}')

        if result.is_right:
            return from_dict(data_class=OrderResponse, data=result.value,
                             config=Config(cast=[Enum],
                                           type_hooks={date: _date_str_to_date,
                                                       Decimal: _float_to_decimal,
                                                       datetime: _datetime_str_to_datetime}))

        return result.value
