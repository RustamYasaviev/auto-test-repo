from aiohttp import web
from aiohttp.web import View


class StateTask(View):
    async def get(self):

        async with self.request.app['pending_task_lock']:
            pending_task = self.request.app['pending_task']
        return web.json_response({'Tasks': pending_task})
