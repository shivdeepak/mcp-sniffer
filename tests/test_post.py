import json
import logging
from unittest.mock import patch

import pytest

from mcp_sniffer.config import AppConfig
from mcp_sniffer.connections import ConnectionManager
from mcp_sniffer.proxy import handle_client
from tests.utils.stream import MockStreamReader, MockStreamWriter

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_simple_post():
    client_reader = MockStreamReader("tests/fixtures/post/simple/request.txt")
    client_writer = MockStreamWriter()
    connection_manager = ConnectionManager()
    config = AppConfig(UPSTREAM_HOST="127.0.0.1", UPSTREAM_PORT=3001)

    response_reader = MockStreamReader("tests/fixtures/post/simple/response.txt")
    response_writer = MockStreamWriter()

    async def mock_open_connection(*args, **kwargs):
        return response_reader, response_writer

    with patch("asyncio.open_connection", mock_open_connection):
        await handle_client(
            client_reader=client_reader,
            client_writer=client_writer,
            connection_manager=connection_manager,
            config=config,
        )

        connections = connection_manager.get_connections()
        assert len(connections) == 1
        assert connections[0]["source_ip"] == "127.0.0.1"
        assert connections[0]["source_port"] == 12345
        assert connections[0]["destination_ip"] == "127.0.0.1"
        assert connections[0]["destination_port"] == 3001

        assert len(response_writer.written_data) == len(client_reader.data_lines)
        for actual, expected in zip(
            response_writer.written_data, client_reader.data_lines
        ):
            assert actual == expected

        expected_connection = json.load(
            open("tests/fixtures/post/simple/connection.json")
        )

        for key, value in expected_connection.items():
            if key not in ["created_at", "ended_at"]:
                assert connections[0][key] == value

        assert len(client_writer.written_data) == len(response_reader.data_lines)
        for actual, expected in zip(
            client_writer.written_data, response_reader.data_lines
        ):
            assert actual == expected

        assert client_writer.closed
        assert response_writer.closed
