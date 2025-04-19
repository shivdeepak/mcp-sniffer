import asyncio
import logging
from typing import Optional

import coloredlogs

from mcp_sniffer.config import AppConfig
from mcp_sniffer.connections import ConnectionManager
from mcp_sniffer.proxy import run_proxy_server
from mcp_sniffer.webui import run_webui

logger = logging.getLogger(__name__)


async def mcp_sniffer(config: Optional[AppConfig] = None):
    if config is None:
        config = AppConfig()

    coloredlogs.install(level=config.LOG_LEVEL)
    connection_manager = ConnectionManager()
    try:
        await asyncio.gather(
            run_proxy_server(connection_manager, config),
            run_webui(connection_manager, config),
        )
    except asyncio.exceptions.CancelledError:
        logger.info("Stopped")
