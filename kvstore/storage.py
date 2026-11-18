"""Record storage independent of HTTP and Coordinator routing."""

from copy import deepcopy
from threading import RLock
from typing import Any, Protocol


class RecordAlreadyExists(Exception):
    """The tuple (table_name, key) is already stored."""


class RecordNotFound(Exception):
    """The tuple (table_name, key) is not stored."""


class RecordStore(Protocol):
    def create(self, table_name: str, key: str, value: Any) -> Any: ...

    def read(self, table_name: str, key: str) -> Any: ...

    def exists(self, table_name: str, key: str) -> bool: ...

    def delete(self, table_name: str, key: str) -> None: ...


class InMemoryRecordStore:
    """Thread-safe, temporary storage keyed by logical table and record key."""

    def __init__(self) -> None:
        self.records: dict[tuple[str, str], Any] = {}
        # allows the same thread to acquire the lock multiple times without deadlocking
        self._lock = RLock()

    def create(self, table_name: str, key: str, value: Any) -> Any:
        record_id = (table_name, key)
        with self._lock:
            if record_id in self.records:
                raise RecordAlreadyExists
            stored_value = deepcopy(value) # creates an independent copy, including nested objects, to prevent unintended changes
            self.records[record_id] = stored_value
            return deepcopy(stored_value)

    def read(self, table_name: str, key: str) -> Any:
        record_id = (table_name, key)
        with self._lock:
            if record_id not in self.records:
                raise RecordNotFound
            return deepcopy(self.records[record_id])

    def exists(self, table_name: str, key: str) -> bool:
        with self._lock:
            return (table_name, key) in self.records

    def delete(self, table_name: str, key: str) -> None:
        with self._lock:
            self.records.pop((table_name, key), None)
