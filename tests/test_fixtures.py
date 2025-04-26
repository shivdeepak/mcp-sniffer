import json
import logging
from unittest.mock import patch

import pytest

from mcp_sniffer.config import AppConfig
from mcp_sniffer.connections import ConnectionManager
from mcp_sniffer.proxy import handle_client
from tests.utils.stream import MockStreamReader, MockStreamWriter

logger = logging.getLogger(__name__)

testcases = [
    ["GET", "simple"],
    ["POST", "simple"],
    ["POST", "without_payload"],
    ["PUT", "simple"],
    ["PATCH", "simple"],
    ["DELETE", "simple"],
    ["DELETE", "with_payload"],
    ["OPTIONS", "simple"],
    ["OPTIONS", "with_payload"],
    ["HEAD", "simple"],
    ["GET", "sse_simple"],
    ["GET", "sse_chunked"],
    ["GET", "sse_chunked_with_id"],
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method, fixture", testcases)
async def test_simple_get(method, fixture):
    fixture_path = f"tests/fixtures/{method.lower()}/{fixture}"
    client_reader = MockStreamReader(f"{fixture_path}/request.txt")
    client_writer = MockStreamWriter()
    connection_manager = ConnectionManager()
    config = AppConfig(UPSTREAM_HOST="127.0.0.1", UPSTREAM_PORT=3001)

    response_reader = MockStreamReader(f"{fixture_path}/response.txt")
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

        expected_connection = json.load(open(f"{fixture_path}/connection.json"))

        for key, value in expected_connection.items():
            if key not in ["created_at", "ended_at", "response"]:
                assert connections[0][key] == value

        if "response" in expected_connection:
            for key, value in expected_connection["response"].items():
                if key not in ["sse_messages", "chunks"]:
                    assert connections[0]["response"][key] == value

            if "sse_messages" in expected_connection["response"]:
                for actual, expected in zip(
                    connections[0]["response"]["sse_messages"],
                    expected_connection["response"]["sse_messages"],
                ):
                    for key, value in expected.items():
                        if key not in ["start_time", "end_time"]:
                            assert actual[key] == value

            if "chunks" in expected_connection["response"]:
                for actual, expected in zip(
                    connections[0]["response"]["chunks"],
                    expected_connection["response"]["chunks"],
                ):
                    for key, value in expected.items():
                        if key not in ["start_time", "end_time"]:
                            assert actual[key] == value

        assert len(client_writer.written_data) == len(response_reader.data_lines)
        for actual, expected in zip(
            client_writer.written_data, response_reader.data_lines
        ):
            assert actual == expected

        assert client_writer.closed
        assert response_writer.closed
