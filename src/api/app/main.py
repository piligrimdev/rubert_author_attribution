import asyncio
from .core.database import *
from .core.dependencies import *
from .core.workers import celery
from .core.services import *
from .core.server import *
from .core.entities import *

#from .core.server import api


def main():

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(api.server.serve())
    loop.run_forever()
