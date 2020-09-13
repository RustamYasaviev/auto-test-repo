from json import dumps
from json.decoder import JSONDecodeError
from typing import Callable, Any

from aiohttp.web import json_response
from aiohttp.web import middleware
from aiohttp.web_request import Request

from utils import ValidRequestExceptions


@middleware
async def check_header_request_data(request: 'Request', handler: Callable) -> Any:

    if request.headers.get('Content-Type') == 'application/json':
        try:

            response = await handler(request)

        except JSONDecodeError:
            response = json_response(data=dumps({'bad_json': request.text()}), status=400)
        except ValidRequestExceptions as param:
            response = json_response(data=dumps({'please_correct_param': param.args}), status=400)
    else:
        response = json_response(data=dumps({'header': 'please set Content-Type: application/json'}), status=400)

    return response
