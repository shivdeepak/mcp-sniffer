import logging
from unittest.mock import MagicMock

logger = logging.getLogger(__package__)


class MockStreamReader:
    def __init__(self, data_file):
        with open(data_file, "rb") as f:
            self.data_lines = f.readlines()
        self.current_line = 0
        self.at_eof_flag = False

    async def readline(self):
        if len(self.data_lines) == 0:
            self.at_eof_flag = True
            return b""

        if self.current_line == len(self.data_lines) - 1:
            self.at_eof_flag = True
        line = self.data_lines[self.current_line]
        self.current_line += 1
        return line

    def at_eof(self):
        return self.at_eof_flag

    async def read(self, n=-1):
        lines = []
        bytes_read = 0

        while bytes_read < n:
            line = await self.readline()
            lines.append(line)
            bytes_read += len(line)

        return b"".join(lines)


class MockStreamWriter:
    def __init__(self):
        self.written_data = []
        self.closed = False
        self.transport = MagicMock()
        self.transport.get_extra_info.return_value = ("127.0.0.1", 12345)

    def write(self, data):
        self.written_data.append(data)

    def get_extra_info(self, name):
        return self.transport.get_extra_info(name)

    def close(self):
        self.closed = True

    async def drain(self):
        pass

    def write_eof(self):
        pass
