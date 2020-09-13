from asyncio import Lock, get_event_loop, CancelledError, sleep, create_task, gather, Condition
from datetime import datetime
from traceback import print_exc

from aiohttp import web

from middlewares import check_header_request_data
from routes import routes_dev


def add_self_route(app: 'web.Application') -> 'web.Application':
    for route in routes_dev:
        app.router.add_view(route[1], route[2], name=route[3])

    return app


async def on_shutdown(app: 'web.Application'):
    print(f'= Exited | Cancelled Task:'
          f'=\n{[t for t in app["task_in_pending"] + app["task_in_process"]]}')
    await app.cleanup()
    app.clear()


async def worker(app: 'web.Application', worker: int):
    while True:
        try:
            while True:
                async with app['task_in_pending_lock']:
                    task = app['task_in_pending'].pop(0)

                async with app['task_in_process_lock']:
                    app['task_in_process'].append(task)

                task['state'] = 'process'
                task['date_of_start'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                n = task.get('N')
                n1 = task.get('N1')
                d = task.get('D')
                interval = task.get('interval')

                try:
                    for i in range(n1, n1 + n):
                        async with app['task_in_process_lock']:
                            task['current_value'] = n1 + (i - 1) * d
                            await sleep(interval)

                except CancelledError:
                    raise CancelledError
                except Exception:
                    print(print_exc())

                async with app['task_in_process_lock']:
                    app['task_in_process'].remove(task)

        except IndexError:
            print("Queue is empty from", worker)
            async with app['process_queue']:
                await app['process_queue'].wait()


async def create_workers_for_handle_tasks(app: 'web.Application'):
    await gather(*[worker(app, worker=num) for num in range(0, app['number_of_queues'])])


async def on_startup(app: 'web.Application'):
    app['gather_with_queues'] = create_task(create_workers_for_handle_tasks(app))


async def setup_server() -> 'web.Application':
    app = web.Application(middlewares=[check_header_request_data])

    app = add_self_route(app)
    app['number_of_queues'] = 5  # Set it
    app['process_queue'] = Condition()

    app['task_in_process'] = []
    app['task_in_process_lock'] = Lock()

    app['task_in_pending'] = []
    app['task_in_pending_lock'] = Lock()

    app['counter_tasks'] = 0
    app['counter_tasks_lock'] = Lock()

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == '__main__':
    loop = get_event_loop()
    try:
        loop.run_until_complete(web.run_app(app=setup_server(), host='0.0.0.0', port=8888))
    except Exception as e:
        print(e)
    finally:
        loop.close()
