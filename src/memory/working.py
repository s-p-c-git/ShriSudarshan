"""
Working Memory module for Project Shri Sudarshan.

Working memory stores short-term state for ongoing analysis.
Data persists only for the duration of the analysis session.
"""

from datetime import datetime, timedelta
from typing import Any, Optional


class WorkingMemory:
    """
    In-memory storage for current analysis state.

    This is a simple implementation using a dictionary.
    For distributed systems, consider using Redis.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize working memory.

        Args:
            ttl_seconds: Time-to-live for entries in seconds
        """
        self._store: dict[str, dict[str, Any]] = {}
        self._ttl_seconds = ttl_seconds

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in working memory.

        Args:
            key: Storage key
            value: Value to store
            ttl: Optional custom TTL in seconds
        """
        expiry_time = datetime.now() + timedelta(
            seconds=ttl if ttl is not None else self._ttl_seconds
        )

        self._store[key] = {
            "value": value,
            "timestamp": datetime.now(),
            "expiry": expiry_time,
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from working memory.

        Args:
            key: Storage key

        Returns:
            Stored value or None if not found or expired
        """
        if key not in self._store:
            return None

        entry = self._store[key]

        # Check if expired
        if datetime.now() > entry["expiry"]:
            del self._store[key]
            return None

        return entry["value"]

    def delete(self, key: str) -> bool:
        """
        Delete a value from working memory.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if not found
        """
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from working memory."""
        self._store.clear()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [key for key, entry in self._store.items() if now > entry["expiry"]]

        for key in expired_keys:
            del self._store[key]

        return len(expired_keys)

    def get_all_keys(self) -> list:
        """
        Get all non-expired keys.

        Returns:
            List of active keys
        """
        self.cleanup_expired()
        return list(self._store.keys())

    def __len__(self) -> int:
        """Return number of non-expired entries."""
        self.cleanup_expired()
        return len(self._store)

    def __repr__(self) -> str:
        return f"WorkingMemory(entries={len(self)}, ttl={self._ttl_seconds}s)"


# Global working memory instance
working_memory = WorkingMemory()
