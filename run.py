from asyncio import create_task, Lock, Event, get_event_loop, CancelledError, sleep
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
    print(f'= Exited with asyncio.ancelledError. Cancelled Task: =\n{[t for t in app["queue"]]}')
    await app.cleanup()
    app.clear()


async def handle_tasks(app: 'web.Application'):
    try:
        while True:
            print('on_startup queue and wait')
            await app['start_queue'].wait()

            while app['pending_task']:
                # Set a gather and declare func(below actions) for parallel work
                async with app['pending_task_lock']:
                    app['pending_task'][0]['state'] = 'process'
                    app['pending_task'][0]['date_of_start'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

                    n = app['pending_task'][0].get('N')
                    n1 = app['pending_task'][0].get('N1')
                    d = app['pending_task'][0].get('D')
                    interval = app['pending_task'][0].get('interval')

                try:
                    for i in range(n1, n1 + n):
                        async with app['pending_task_lock']:
                            app['pending_task'][0]['current_value'] = n1 + (i - 1) * d
                            await sleep(interval)

                except CancelledError:
                    raise CancelledError
                except Exception:
                    print(print_exc())

                app['start_queue'].clear()
                async with app['pending_task_lock']:
                    app['pending_task'].pop(0)

                    for task in app['pending_task']:
                        task['number'] -= 1

    except CancelledError:
        pass
    except Exception as e:
        print(print_exc())


async def on_startup(app: 'web.Application'):
    app['handle_task'] = create_task(handle_tasks(app))


async def setup_server() -> 'web.Application':
    app = web.Application(middlewares=[check_header_request_data])

    app = add_self_route(app)

    app['pending_task'] = []
    app['pending_task_lock'] = Lock()
    app['start_queue'] = Event()

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
