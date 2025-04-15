import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from email.message import Message
from email.parser import HeaderParser

from httptools import HttpRequestParser, HttpResponseParser

logger = logging.getLogger(__name__)


def parse_content_type(header: str):
    parser = HeaderParser()
    msg: Message = parser.parsestr(f"Content-Type: {header}")
    params = msg.get_params()
    return msg.get_content_type(), dict(params[1:] if params else [])


class Chunk:
    def __init__(self):
        self.start_time = datetime.now()
        self.data = []
        self.end_time = None

    def end(self):
        self.end_time = datetime.now()

    def as_dict(self):
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "data": self.data,
        }


class SSEMessage:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None

        self.event = None
        self.data = []
        self.id = None
        self.retry = None
        self.comments = []

    def ended(self):
        return self.end_time is not None

    def parse_line(self, line: str):
        if line.strip() == "":
            self.end_time = datetime.now()
            return

        delim_loc = line.index(":")
        if delim_loc == 0:
            self.comments.append(line)
            return

        if delim_loc == -1:
            logger.warning(f"Unknown SSE line: {line}")
            return

        field = line[:delim_loc].strip()
        if field == "event":
            self.event = line[delim_loc + 1 :].strip()
        elif field == "data":
            self.data.append(line[delim_loc + 1 :].strip())
        elif field == "id":
            self.id = line[delim_loc + 1 :].strip()
        elif field == "retry":
            self.retry = line[delim_loc + 1 :].strip()
        else:
            logger.warning(f"Unknown SSE field: {field}")
            raise ValueError(f"Unknown field: {field}")

    def as_dict(self):
        result = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }

        if self.data:
            if self.data[0][0] == "{":
                try:
                    result["data"] = json.loads("\n".join(self.data))
                except json.JSONDecodeError:
                    result["data"] = self.data
            else:
                result["data"] = self.data

        if self.comments:
            result["comments"] = self.comments

        if self.event:
            result["event"] = self.event

        if self.id:
            result["id"] = self.id

        if self.retry:
            result["retry"] = self.retry

        return result


class RequestParser:
    parser: HttpRequestParser

    def __init__(self):
        self.parser = HttpRequestParser(self)

        self.method = None
        self.path = None
        self.http_version = None

        self.headers = {}

        self.body = None
        self.raw_body: list[str] = []

        self.content_type = None
        self.content_type_params = {}

    def parse_request(self, data: bytes):
        if data.decode().strip() != "":
            print("parse_response", data)
        self.raw_body.append(data.decode())
        self.parser.feed_data(data)

    def on_message_begin(self):
        print("on_message_begin")

    def on_url(self, url: bytes):
        self.method = self.parser.get_method().decode()
        self.path = url.decode()

    def on_header(self, name: bytes, value: bytes):
        if name.decode().lower() == "content-type":
            mime, params = parse_content_type(value.decode())
            self.content_type = mime
            self.content_type_params = params
        self.headers[name.decode().lower()] = value.decode()

    def on_headers_complete(self):
        self.http_version = self.parser.get_http_version()

    def on_body(self, body: bytes):
        self.body = body.decode()

    def on_message_complete(self):
        print("on_message_complete")

    def on_chunk_header(self):
        print("on_chunk_header")

    def on_chunk_complete(self):
        print("on_chunk_complete")

    def on_status(self, status: bytes):
        print("on_status", status)

    def as_dict(self):
        result = {
            "method": self.method,
            "path": self.path,
            "http_version": self.http_version,
            "headers": self.headers,
            "raw_body": self.raw_body,
        }

        if self.method == "POST":
            if self.headers.get("content-type") == "application/json":
                if self.body:
                    result["body"] = json.loads(self.body)
            elif self.body:
                result["body"] = self.body

        return result


class ResponseParser:
    parser: HttpResponseParser

    def __init__(self):
        self.parser = HttpResponseParser(self)

        self.http_version = None
        self.status_code = None
        self.status_message = None

        self.headers: dict[str, str] = {}

        self.body = None
        self.chunks: list[Chunk] = []

        self.sse_messages: list[SSEMessage] = []

        self.raw_body: list[str] = []

        self.content_type = None
        self.content_type_params = {}

    def parse_response(self, data: bytes):
        if data.decode().strip() != "":
            print("parse_response", data)
        self.raw_body.append(data.decode())
        self.parser.feed_data(data)

    def on_message_begin(self):
        print("on_message_begin")

    def on_url(self, url: bytes):
        print("on_url", url)

    def on_header(self, name: bytes, value: bytes):
        if name.decode().lower() == "content-type":
            mime, params = parse_content_type(value.decode())
            self.content_type = mime
            self.content_type_params = params

        self.headers[name.decode().lower()] = value.decode()

    def on_headers_complete(self):
        if self.content_type == "text/event-stream":
            self.sse_messages.append(SSEMessage())
        print("on_headers_complete")

    def on_body(self, body: bytes):
        if self.headers.get("transfer-encoding") == "chunked":
            self.chunks[-1].data.append(body.decode())
        else:
            self.body = body.decode()

        if self.content_type == "text/event-stream":
            if self.sse_messages[-1].ended():
                self.sse_messages.append(SSEMessage())

            self.sse_messages[-1].parse_line(body.decode())

    def on_message_complete(self):
        print("on_message_complete")

    def on_chunk_header(self):
        self.chunks.append(Chunk())
        print("on_chunk_header")

    def on_chunk_complete(self):
        self.chunks[-1].end()
        print("on_chunk_complete")

    def on_status(self, status: bytes):
        self.status_message = status.decode()
        self.status_code = self.parser.get_status_code()
        self.http_version = self.parser.get_http_version()

    def as_dict(self):
        result = {
            "http_version": self.http_version,
            "status_code": self.status_code,
            "status_message": self.status_message,
            "headers": self.headers,
            "raw_body": self.raw_body,
        }

        if self.headers.get("transfer-encoding") == "chunked" and self.chunks:
            result["chunks"] = [chunk.as_dict() for chunk in self.chunks]

        elif self.body:
            result["body"] = self.body

        if self.content_type == "text/event-stream":
            result["sse_messages"] = [
                sse_message.as_dict() for sse_message in self.sse_messages
            ]

        return result


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
