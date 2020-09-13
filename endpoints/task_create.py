from asyncio import create_task

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

        create_task(self.prepare_task(task=request))

        return json_response(request)

    async def prepare_task(self, task: {}):
        async with self.request.app['counter_tasks_lock']:
            self.request.app['counter_tasks'] += 1
        convert_data = {
            'number': self.request.app['counter_tasks'],
            'state': 'pending',
            'N': task.get('n'),
            'D': task.get('d'),
            'N1': task.get('n1'),
            'interval': task.get('interval'),
            'current_value': None,
            'date_of_start': None
        }
        async with self.request.app['task_in_process_lock']:
            self.request.app['task_in_pending'].append(convert_data)
        async with self.request.app['process_queue']:
            self.request.app['process_queue'].notify()
