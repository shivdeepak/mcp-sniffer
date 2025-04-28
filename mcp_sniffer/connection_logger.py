import logging
import sys


class ConnectionLogger(logging.LoggerAdapter):
    def __init__(
        self,
        logger,
        source_ip,
        source_port,
        connection_id,
        extra=None,
        merge_extra=False,
    ):
        if sys.version_info >= (3, 13):
            super().__init__(logger, extra=extra, merge_extra=merge_extra)
        else:
            super().__init__(logger, extra=extra)
        self.source_ip = source_ip
        self.source_port = source_port
        self.connection_id = connection_id

    def process(self, msg, kwargs):
        return (
            f"{self.source_ip}:{self.source_port}[{self.connection_id}] {msg}",
            kwargs,
        )
