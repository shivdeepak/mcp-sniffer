import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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
