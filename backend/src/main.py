import asyncio
import os
import sys

import coloredlogs

sys.path.append(os.path.dirname(__file__))

from connections import ConnectionManager
from proxy import run_proxy_server
from webui import run_webui


async def main():
    connection_manager = ConnectionManager()
    await asyncio.gather(
        run_proxy_server(connection_manager),
        run_webui(connection_manager),
    )


coloredlogs.install(level="DEBUG")

asyncio.run(main())
