import json
import os
import sys

from httptools import HttpRequestParser  # type: ignore

sys.path.append(os.path.dirname(__file__))

from parsers.base import BaseParser


class RequestParser(BaseParser):
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
            mime, params = self.parse_content_type(value.decode())
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
