from aiohttp.web import View, json_response

from utils.exceptions import ValidRequestExceptions


class CreateTask(View):
    async def post(self):

        request = await self.request.json()

        if type(request.get('n')) is not int: raise ValidRequestExceptions('n')
        if type(request.get('d')) is not float: raise ValidRequestExceptions('d')
        if type(request.get('n1')) is not int: raise ValidRequestExceptions('n1')
        if type(request.get('interval')) is not float: raise ValidRequestExceptions('interval')

        if request['n'] <= 0: raise ValidRequestExceptions('Please set n > 0')
        if request['d'] <= 0: raise ValidRequestExceptions('Please set d > 0')

        convert_data = {
            'number': len(self.request.app['pending_task']) + 1,
            'state': 'pending',
            'N': request.get('n'),
            'D': request.get('d'),
            'N1': request.get('n1'),
            'interval': request.get('interval'),
            'current_value': None,
            'date_of_start': None
        }

        async with self.request.app['pending_task_lock']:
            self.request.app['pending_task'].append(convert_data)

        self.request.app['start_queue'].set()
        return json_response(request)
