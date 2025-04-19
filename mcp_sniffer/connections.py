import logging
from dataclasses import dataclass, field
from datetime import datetime

from mcp_sniffer.parsers.request import RequestParser
from mcp_sniffer.parsers.response import ResponseParser

logger = logging.getLogger(__name__)


@dataclass
class Connection:
    created_at: datetime = field(default_factory=datetime.now)
    source_ip: str = field(default_factory=str)
    source_port: int = field(default_factory=int)
    destination_ip: str = field(default_factory=str)
    destination_port: int = field(default_factory=int)
    request_parser: RequestParser = field(default_factory=RequestParser)
    response_parser: ResponseParser = field(default_factory=ResponseParser)
    active: bool = field(default=True)
    ended_at: datetime | None = field(default=None)

    def close(self):
        if self.active:
            self.active = False
            self.ended_at = datetime.now()


class ConnectionManager:
    def __init__(self):
        self.connections: list[Connection] = []

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def get_connections(self) -> list[dict]:
        _connections = []
        for connection in self.connections:
            _connections.append(
                {
                    "active": connection.active,
                    "created_at": connection.created_at.isoformat(),
                    "ended_at": connection.ended_at.isoformat()
                    if connection.ended_at
                    else None,
                    "source_ip": connection.source_ip,
                    "source_port": connection.source_port,
                    "destination_ip": connection.destination_ip,
                    "destination_port": connection.destination_port,
                    "request": connection.request_parser.as_dict(),
                    "response": connection.response_parser.as_dict(),
                }
            )

        return _connections
