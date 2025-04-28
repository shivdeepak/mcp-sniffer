import json

from httptools import HttpRequestParser  # type: ignore

from mcp_sniffer.parsers.base import BaseParser


class RequestParser(BaseParser):
    parser: HttpRequestParser

    def __init__(self, connection_logger):
        self.parser = HttpRequestParser(self)
        self.logger = connection_logger

        self.method = None
        self.path = None
        self.http_version = None

        self.headers = {}

        self.body = None
        self.raw_body: list[str] = []

        self.content_type = None
        self.content_type_params = {}
        self.on_headers_completed = False
        self.message_began = False

    def parse_request(self, data: bytes):
        if data.decode().strip() != "":
            self.logger.debug("parse_request %s", data)
        self.raw_body.append(data.decode())
        self.parser.feed_data(data)

    def on_message_begin(self):
        self.logger.debug("on_message_begin")
        self.message_began = True

    def on_url(self, url: bytes):
        self.logger.debug("on_url %s", url)
        self.method = self.parser.get_method().decode()
        self.path = url.decode()

    def on_header(self, name: bytes, value: bytes):
        self.logger.debug("on_header %s %s", name, value)
        if name.decode().lower() == "content-type":
            mime, params = self.parse_content_type(value.decode())
            self.content_type = mime
            self.content_type_params = params
        self.headers[name.decode().lower()] = value.decode()

    def on_headers_complete(self):
        self.logger.debug("on_headers_complete")
        self.http_version = self.parser.get_http_version()
        self.on_headers_completed = True

    def on_body(self, body: bytes):
        self.logger.debug("on_body %s", body)
        self.body = body.decode()

    def on_message_complete(self):
        self.logger.debug("on_message_complete")

    def on_chunk_header(self):
        self.logger.debug("on_chunk_header")

    def on_chunk_complete(self):
        self.logger.debug("on_chunk_complete")

    def on_status(self, status: bytes):
        self.logger.debug("on_status %s", status)

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
