import os
import sys

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

sys.path.append(os.path.dirname(__file__))

from config import config

host_mapping = {
    "127.0.0.1": "localhost",
    "0.0.0.0": "localhost",
    "host.docker.internal": "localhost",
}


async def run_webui(connection_manager):
    app = Starlette(debug=True)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.route("/connections")
    async def connections(request):
        return JSONResponse(
            content={
                "source_ip": host_mapping[config.LISTEN_HOST]
                if config.LISTEN_HOST in host_mapping
                else config.LISTEN_HOST,
                "source_port": config.LISTEN_PORT,
                "destination_ip": host_mapping[config.UPSTREAM_HOST]
                if config.UPSTREAM_HOST in host_mapping
                else config.UPSTREAM_HOST,
                "destination_port": config.UPSTREAM_PORT,
                "version": "v0.1.0",
                "connections": connection_manager.get_connections(),
                "status": "ok",
            },
            status_code=200,
        )

    app.mount("/", StaticFiles(directory="../frontend/dist", html=True))

    uvicorn_config = uvicorn.Config(
        app,
        host=config.WEB_UI_HOST,
        port=config.WEB_UI_PORT,
        log_level="info",
        loop="asyncio",
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()
