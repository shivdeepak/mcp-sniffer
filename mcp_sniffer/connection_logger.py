import logging


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
        super().__init__(logger, extra, merge_extra)
        self.source_ip = source_ip
        self.source_port = source_port
        self.connection_id = connection_id

    def process(self, msg, kwargs):
        return (
            f"{self.source_ip}:{self.source_port}[{self.connection_id}] {msg}",
            kwargs,
        )
