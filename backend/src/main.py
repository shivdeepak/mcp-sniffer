import asyncio
import os
import sys

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

sys.path.append(os.path.dirname(__file__))

from connections import Connection, ConnectionManager, RequestParser, ResponseParser

FRONTEND_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
FRONTEND_PORT = os.getenv("LISTEN_PORT", "3002")

BACKEND_HOST = os.getenv("UPSTREAM_HOST", "host.docker.internal")
BACKEND_PORT = os.getenv("UPSTREAM_PORT", "3001")

connection_manager = ConnectionManager()


async def handle_client(client_reader, client_writer):
    addr = client_writer.get_extra_info("peername")
    print(f"New connection from {addr}")

    try:
        server_reader, server_writer = await asyncio.open_connection(
            BACKEND_HOST, BACKEND_PORT
        )
    except (ConnectionRefusedError, OSError):
        print(
            f"Connection refused or failed with upstream server {BACKEND_HOST}:{BACKEND_PORT}"
        )
        client_writer.close()
        return

    print(f"Connected to {BACKEND_HOST}:{BACKEND_PORT}")

    connection = Connection(
        source_ip=addr[0],
        source_port=addr[1],
        destination_ip=BACKEND_HOST,
        destination_port=int(BACKEND_PORT),
        request_parser=RequestParser(),
        response_parser=ResponseParser(),
    )
    connection_manager.add_connection(connection)

    method_type = None
    try:
        headers = []
        count = 0
        while True:
            count += 1
            data = await client_reader.readline()
            connection.request_parser.parse_request(data)

            if method_type is None:
                if data.decode().strip() == "":
                    break
                method_type = data.decode().split()[0]

            server_writer.write(data)
            await server_writer.drain()

            raw_header = data.decode()
            if count > 1 and ":" in raw_header:
                first_colon_index = raw_header.index(":")
                headers.append(
                    [
                        raw_header[:first_colon_index].strip().lower(),
                        raw_header[first_colon_index + 1 :].strip(),
                    ]
                )

            if not data.strip():
                headers_dict = dict(headers)
                if method_type == "POST":
                    if "content-length" in headers_dict:
                        payload = await client_reader.read(
                            int(headers_dict["content-length"])
                        )
                        connection.request_parser.parse_request(payload)
                        # print(f"Received payload: {payload}")
                        server_writer.write(payload)
                        await server_writer.drain()

                if len(headers_dict) == 0:
                    print(f"Closing empty connection from {addr}")
                    server_writer.close()
                    client_writer.close()

                print(f"Received empty line from {method_type} {addr}")
                break

        while True:
            data = await server_reader.readline()
            connection.response_parser.parse_response(data)
            print(f"Received from server {addr}: {data}: {server_reader.at_eof()}")

            client_writer.write(data)
            await client_writer.drain()

            if (
                connection.response_parser.on_message_completed
                or server_reader.at_eof()
            ):
                print(f"Received on_message_completed from {addr}")
                try:
                    client_writer.write_eof()
                    await client_writer.drain()
                except OSError:
                    pass
                break

    except (ConnectionResetError, BrokenPipeError) as e:
        print(f"Connection closed by {addr}: {e}")
        connection.close()
        # break

    try:
        client_writer.close()
    except Exception as e:
        print(f"Error closing connection: {e}")
    finally:
        connection.close()

    try:
        server_writer.close()
    except Exception as e:
        print(f"Error closing connection: {e}")
    finally:
        connection.close()


async def main():
    await asyncio.gather(
        run_proxy_server(),
        run_starlette_server(),
    )


async def run_starlette_server():
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
                "source_ip": FRONTEND_HOST,
                "source_port": FRONTEND_PORT,
                "destination_ip": BACKEND_HOST,
                "destination_port": BACKEND_PORT,
                "version": "v0.1.0",
                "connections": connection_manager.get_connections(),
                "status": "ok",
            },
            status_code=200,
        )

    app.mount("/", StaticFiles(directory="../frontend/dist", html=True))

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(os.getenv("WEB_UI_PORT", "8888")),
        log_level="info",
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_proxy_server():
    server = await asyncio.start_server(handle_client, FRONTEND_HOST, FRONTEND_PORT)
    addr = server.sockets[0].getsockname()
    print(f"Listening on {addr}...")

    async with server:
        await server.serve_forever()


# Run it
asyncio.run(main())
