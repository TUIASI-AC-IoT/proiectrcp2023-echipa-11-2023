from enum import IntEnum

class EventType(IntEnum):
    FILE_LIST = 0
    FILE_CONTENT = 1
    FILE_HEADER = 2
    CREATED_FOLDER = 4
    RENAMED_FILE = 5
    DELETED_FILE = 6
    FAILED_REQUEST = 7
    REQUEST_TIMEOUT = 8


class Event:
    def __init__(self, eventType: EventType, data=None):
        self.eventType = eventType
        self.data = data

