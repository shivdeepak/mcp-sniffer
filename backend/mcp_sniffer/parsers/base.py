from email.message import Message
from email.parser import HeaderParser


class BaseParser:
    def parse_content_type(self, header: str):
        parser = HeaderParser()
        msg: Message = parser.parsestr(f"Content-Type: {header}")
        params = msg.get_params()
        return msg.get_content_type(), dict(params[1:] if params else [])
