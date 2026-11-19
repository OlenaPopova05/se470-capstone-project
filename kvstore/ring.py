"""Deterministic consistent hashing for record placement."""

from bisect import bisect_left
from hashlib import sha256
from typing import Iterable


VIRTUAL_NODES_PER_SHARD = 100


def encode_pair(first: str, second: str) -> bytes:
    """Prefix each UTF-8 string with its four-byte big-endian byte length."""

    first_bytes = first.encode("utf-8")
    second_bytes = second.encode("utf-8")
    # Add the length before each string to keep pairs unique.
    # Example: ("ab", "c") must differ from ("a", "bc").
    # "big" means the most significant byte comes first.
    return (
        len(first_bytes).to_bytes(4, "big")
        + first_bytes
        + len(second_bytes).to_bytes(4, "big")
        + second_bytes
    )


def hash_position(first: str, second: str) -> int:
    """Return a SHA-256 ring position for a record or virtual node."""
    # encode_pair() converts the strings into bytes.
    # sha256() creates a fixed 256-bit hash.
    # digest() returns the hash as bytes.
    # int.from_bytes() converts these bytes into an integer.
    return int.from_bytes(sha256(encode_pair(first, second)).digest(), "big")


class ConsistentHashRing:
    """Map a record to the first virtual node clockwise from its hash."""

    def __init__(self, shard_ids: Iterable[str]) -> None:
        # Create 100 virtual nodes for each physical shard.
        # Each node is a tuple: (hash_position, shard_id, node_index).
        self._nodes = sorted(
            (hash_position(shard_id, str(index)), shard_id, index)
            for shard_id in set(shard_ids)
            for index in range(VIRTUAL_NODES_PER_SHARD)
        )
        # Keep only the positions for fast searching.
        self._positions = [position for position, _, _ in self._nodes]

    @property
    def virtual_node_count(self) -> int:
        return len(self._nodes)

    def shard_for_position(self, position: int) -> str:
        """Wrap to the first virtual node when the position passes the last."""

        if not self._nodes:
            raise LookupError("No shards registered")
        # bisect_left() finds the index of the first position >= our hash.
        index = bisect_left(self._positions, position)
        # If the hash is after the last node, go back to the first node.
        if index == len(self._nodes):
            index = 0
        return self._nodes[index][1]

    def owner(self, table_name: str, record_key: str) -> str:
        return self.shard_for_position(hash_position(table_name, record_key))
