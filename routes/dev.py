from endpoints import CreateTask, StateTask


routes = [
    ('POST', '/create_task', CreateTask, 'create_task'),
    ('GET', '/status_task', StateTask, 'status_task'),
]