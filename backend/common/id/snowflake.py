from __future__ import annotations

import time
from threading import Lock

from backend.common.constants.snowflake import MAX_WORKER_ID, MAX_SEQUENCE, MAX_TIMESTAMP, TIMESTAMP_SHIFT, \
    SEQUENCE_BITS


class SnowflakeIdGenerator:
    def __init__(self, worker_id: int, epoch_ms: int, sequence_wait_timeout_ms: int = 100) -> None:

        # this is checking the info
        if not 0 <= worker_id <= MAX_WORKER_ID:
            raise ValueError(f"worker_id must be between 0 and {MAX_WORKER_ID}")
        if epoch_ms < 0:
            raise ValueError("epoch_ms must be non-negative")
        if sequence_wait_timeout_ms <= 0:
            raise ValueError("sequence_wait_timeout_ms must be positive")

        self._worker_id = worker_id
        self._epoch_ms = epoch_ms
        self._wait_timeout_seconds = sequence_wait_timeout_ms / 1000

        self._last_timestamp_ms = -1
        self._sequence = 0
        self._lock = Lock()

    def generate_next_id(self) -> int:
        with self._lock:
            timestamp_ms = self._current_timestamp_ms()
            if timestamp_ms < self._last_timestamp_ms:
                raise RuntimeError("Clock moved backwards; ID generation stopped")
            elif timestamp_ms == self._last_timestamp_ms:
                sequence = self._sequence + 1
                if sequence > MAX_SEQUENCE:
                    timestamp_ms = self._with_next_millisecond(timestamp_ms)
                    sequence = 0
            else:
                sequence = 0
            elapsed_ms = timestamp_ms - self._epoch_ms
            if not 0 <= elapsed_ms <= MAX_TIMESTAMP:
                raise RuntimeError("Current time is outside the configured Snowflake range")
            if elapsed_ms == 0 and self._worker_id == 0 and sequence == 0:
                sequence = 1
            generated_id = (
                    (elapsed_ms << TIMESTAMP_SHIFT) | (self._worker_id << SEQUENCE_BITS) | sequence
            )
            self._last_timestamp_ms = timestamp_ms
            self._sequence = sequence
            return generated_id

    @staticmethod
    def _current_timestamp_ms() -> int:
        return time.time_ns() // 1_000_000

    def _with_next_millisecond(self, previous_timestamp_ms):
        deadline = time.monotonic() + self._wait_timeout_seconds

        while True:
            timestamp_ms = self._current_timestamp_ms()
            if timestamp_ms < previous_timestamp_ms:
                raise RuntimeError("Clock moved backwards; ID generation stopped")

            if timestamp_ms > previous_timestamp_ms:
                return timestamp_ms

            if time.monotonic() >= deadline:
                raise TimeoutError("Timed out waiting for the next millisecond")

            time.sleep(0.0001)
