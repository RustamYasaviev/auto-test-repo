from aiohttp import web
from aiohttp.web import View


class StateTask(View):
    async def get(self):

        # async with self.request.app['pending_task_lock']:
        task_in_pending = self.request.app['task_in_pending']
        # async with self.request.app['task_in_process_lock']:
        task_in_process = self.request.app['task_in_process']

        return web.json_response({'Tasks': task_in_process + task_in_pending})
