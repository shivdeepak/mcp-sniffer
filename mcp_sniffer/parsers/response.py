import logging

from httptools import HttpResponseParser  # type: ignore

from mcp_sniffer.parsers.base import BaseParser
from mcp_sniffer.parsers.chunk import Chunk
from mcp_sniffer.parsers.sse_message import SSEMessage

logger = logging.getLogger(__name__)


class ResponseParser(BaseParser):
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

        self.on_message_completed: bool = False

    def parse_response(self, data: bytes):
        if data.decode().strip() != "":
            logger.debug("parse_response %s", data)
        self.raw_body.append(data.decode())
        self.parser.feed_data(data)

    def on_message_begin(self):
        logger.debug("on_message_begin")

    def on_url(self, url: bytes):
        logger.debug("on_url %s", url)

    def on_header(self, name: bytes, value: bytes):
        logger.debug("on_header %s %s", name, value)
        if name.decode().lower() == "content-type":
            mime, params = self.parse_content_type(value.decode())
            self.content_type = mime
            self.content_type_params = params

        self.headers[name.decode().lower()] = value.decode()

    def on_headers_complete(self):
        logger.debug("on_headers_complete")
        if self.content_type == "text/event-stream":
            self.sse_messages.append(SSEMessage())

    def on_body(self, body: bytes):
        logger.debug("on_body %s", body)
        if self.headers.get("transfer-encoding") == "chunked":
            self.chunks[-1].data.append(body.decode())
        else:
            self.body = body.decode()

        if self.content_type == "text/event-stream":
            if self.sse_messages[-1].ended():
                self.sse_messages.append(SSEMessage())

            self.sse_messages[-1].parse_line(body.decode())

    def on_message_complete(self):
        logger.debug("on_message_complete")
        self.on_message_completed = True

    def on_chunk_header(self):
        logger.debug("on_chunk_header")
        self.chunks.append(Chunk())

    def on_chunk_complete(self):
        logger.debug("on_chunk_complete")
        self.chunks[-1].end()

    def on_status(self, status: bytes):
        logger.debug("on_status %s", status)
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
