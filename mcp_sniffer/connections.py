import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

from mcp_sniffer.parsers.request import RequestParser
from mcp_sniffer.parsers.response import ResponseParser

logger = logging.getLogger(__package__)


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
    ended_at: Union[datetime, None] = field(default=None)

    def close(self):
        if self.active:
            self.active = False
            self.ended_at = datetime.now()

    def as_dict(self) -> dict:
        return {
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "source_ip": self.source_ip,
            "source_port": self.source_port,
            "destination_ip": self.destination_ip,
            "destination_port": self.destination_port,
            "request": self.request_parser.as_dict(),
            "response": self.response_parser.as_dict(),
        }


class ConnectionManager:
    def __init__(self):
        self.connections: list[Connection] = []

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def get_connections(self) -> list[dict]:
        return [connection.as_dict() for connection in self.connections]
