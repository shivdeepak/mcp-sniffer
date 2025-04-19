from datetime import datetime


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
