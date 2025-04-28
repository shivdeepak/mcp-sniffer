import asyncio
import logging
from functools import partial

from mcp_sniffer.connection_logger import ConnectionLogger
from mcp_sniffer.connections import Connection
from mcp_sniffer.parsers.request import RequestParser
from mcp_sniffer.parsers.response import ResponseParser

logger = logging.getLogger(__package__)


async def handle_client(client_reader, client_writer, connection_manager, config):
    connection_id = await connection_manager.counter.get()
    (source_ip, source_port) = client_writer.get_extra_info("peername")
    connection_logger = ConnectionLogger(logger, source_ip, source_port, connection_id)
    connection_logger.info("New connection received!")

    try:
        server_reader, server_writer = await asyncio.open_connection(
            config.UPSTREAM_HOST, config.UPSTREAM_PORT
        )
    except (ConnectionRefusedError, OSError):
        connection_logger.error(
            "Connection refused or failed with upstream server %s:%s",
            config.UPSTREAM_HOST,
            config.UPSTREAM_PORT,
        )
        client_writer.close()
        return

    connection_logger.info(
        "Connected to %s:%s", config.UPSTREAM_HOST, config.UPSTREAM_PORT
    )

    connection = Connection(
        id=connection_id,
        source_ip=source_ip,
        source_port=source_port,
        destination_ip=config.UPSTREAM_HOST,
        destination_port=config.UPSTREAM_PORT,
        request_parser=RequestParser(connection_logger),
        response_parser=ResponseParser(connection_logger),
    )
    connection_manager.add_connection(connection)

    method_type = None
    try:
        while True:
            data = await client_reader.readline()
            if data == b"":
                break

            server_writer.write(data)
            await server_writer.drain()

            connection.request_parser.parse_request(data)

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
                        connection_logger.info("Closing empty connection")
                        server_writer.close()
                        client_writer.close()

                    connection_logger.info("Received empty line from %s", method_type)
                    break

        while True:
            if (
                connection.response_parser.on_message_completed
                or server_reader.at_eof()
            ):
                connection_logger.info("Received on_message_completed")
                try:
                    client_writer.write_eof()
                    await client_writer.drain()
                except OSError:
                    pass
                break
            data = await server_reader.readline()
            if data == b"":
                break

            client_writer.write(data)
            try:
                await client_writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                connection_logger.error("Connection closed by client")
                server_writer.close()
                break
            connection.response_parser.parse_response(data)

    except (ConnectionResetError, BrokenPipeError) as e:
        connection_logger.info("Connection closed by client", exc_info=e)
        connection.close()

    try:
        client_writer.close()
    except Exception as e:
        connection_logger.error("Error closing connection", exc_info=e)
    finally:
        connection.close()

    try:
        server_writer.close()
    except Exception as e:
        connection_logger.error("Error closing connection", exc_info=e)
    finally:
        connection.close()


async def run_proxy_server(connection_manager, config):
    server = await asyncio.start_server(
        partial(handle_client, connection_manager=connection_manager, config=config),
        config.LISTEN_HOST,
        config.LISTEN_PORT,
    )
    ip, port = server.sockets[0].getsockname()
    logger.info("Listening on %s:%s...", ip, port)

    async with server:
        await server.serve_forever()
