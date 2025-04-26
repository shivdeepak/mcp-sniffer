import asyncio
import logging
from functools import partial

from mcp_sniffer.connections import Connection
from mcp_sniffer.parsers.request import RequestParser
from mcp_sniffer.parsers.response import ResponseParser

logger = logging.getLogger(__name__)


async def handle_client(client_reader, client_writer, connection_manager, config):
    addr = client_writer.get_extra_info("peername")
    logger.info("New connection from %s", addr)

    try:
        server_reader, server_writer = await asyncio.open_connection(
            config.UPSTREAM_HOST, config.UPSTREAM_PORT
        )
    except (ConnectionRefusedError, OSError):
        logger.error(
            "Connection refused or failed with upstream server %s:%s",
            config.UPSTREAM_HOST,
            config.UPSTREAM_PORT,
        )
        client_writer.close()
        return

    logger.info("Connected to %s:%s", config.UPSTREAM_HOST, config.UPSTREAM_PORT)

    connection = Connection(
        source_ip=addr[0],
        source_port=addr[1],
        destination_ip=config.UPSTREAM_HOST,
        destination_port=config.UPSTREAM_PORT,
        request_parser=RequestParser(),
        response_parser=ResponseParser(),
    )
    connection_manager.add_connection(connection)

    method_type = None
    try:
        while True:
            data = await client_reader.readline()
            if data == b"":
                break
            connection.request_parser.parse_request(data)

            server_writer.write(data)
            await server_writer.drain()

            if connection.request_parser.on_headers_completed:
                if not data.strip():
                    headers = connection.request_parser.headers
                    if "content-length" in headers:
                        payload = await client_reader.read(
                            int(headers["content-length"])
                        )
                        connection.request_parser.parse_request(payload)
                        server_writer.write(payload)
                        await server_writer.drain()

                    if len(headers) == 0:
                        logger.info("Closing empty connection from %s", addr)
                        server_writer.close()
                        client_writer.close()

                    logger.info("Received empty line from %s %s", method_type, addr)
                    break

        while True:
            if (
                connection.response_parser.on_message_completed
                or server_reader.at_eof()
            ):
                logger.info("Received on_message_completed from %s", addr)
                try:
                    client_writer.write_eof()
                    await client_writer.drain()
                except OSError:
                    pass
                break
            data = await server_reader.readline()
            if data == b"":
                break
            connection.response_parser.parse_response(data)

            client_writer.write(data)
            await client_writer.drain()

    except (ConnectionResetError, BrokenPipeError) as e:
        logger.info("Connection closed by %s", addr, exc_info=e)
        connection.close()
        # break

    try:
        client_writer.close()
    except Exception as e:
        logger.error("Error closing connection", exc_info=e)
    finally:
        connection.close()

    try:
        server_writer.close()
    except Exception as e:
        logger.error("Error closing connection", exc_info=e)
    finally:
        connection.close()


async def run_proxy_server(connection_manager, config):
    server = await asyncio.start_server(
        partial(handle_client, connection_manager=connection_manager, config=config),
        config.LISTEN_HOST,
        config.LISTEN_PORT,
    )
    addr = server.sockets[0].getsockname()
    logger.info("Listening on %s...", addr)

    async with server:
        await server.serve_forever()
