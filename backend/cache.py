"""
Global Repository Cache
Singleton module that serves as the single source of truth for in-memory repository storage.

WHY THIS EXISTS:
  Python caches module objects by identity in sys.modules. By centralizing the
  `repository_cache` dict here, every module that imports it always gets a
  reference to the SAME dict object — even across uvicorn --reload cycles that
  re-execute individual modules but not the interpreter itself.

  Previously, `chat_service.py` did:
      from backend.api.repository import repository_cache
  That worked when modules were loaded in a single pass. But any scenario that
  caused `backend.api.repository` to be re-evaluated (e.g. reload, circular
  import resolution order) could give `chat_service` a stale reference to an
  *empty* dict while `repository.py` filled a *new* one.
"""

import threading
from typing import Dict, Any

# -----------------------------------------------------------------
# Thread-safe in-memory repository cache
# Key   : repo_id (str)
# Value : RepositoryAnalysis object
# -----------------------------------------------------------------
_lock = threading.Lock()
_store: Dict[str, Any] = {}


def get(repo_id: str):
    """Return analysis for repo_id, or None if not found."""
    with _lock:
        return _store.get(repo_id)


def set(repo_id: str, analysis) -> None:
    """Store analysis under repo_id."""
    with _lock:
        _store[repo_id] = analysis


def delete(repo_id: str) -> bool:
    """Remove repo_id from cache. Returns True if it existed."""
    with _lock:
        if repo_id in _store:
            del _store[repo_id]
            return True
        return False


def contains(repo_id: str) -> bool:
    """Check if repo_id exists in cache."""
    with _lock:
        return repo_id in _store


def keys():
    """Return snapshot list of all cached repo IDs."""
    with _lock:
        return list(_store.keys())


def size() -> int:
    """Return number of cached repositories."""
    with _lock:
        return len(_store)


def items():
    """Return snapshot list of (repo_id, analysis) tuples."""
    with _lock:
        return list(_store.items())


# ---------------------------------------------------------------------------
# Legacy compatibility shim
# Some older code does:  from backend.api.repository import repository_cache
# and then uses it like a plain dict. We expose a proxy object that delegates
# all dict operations to the thread-safe store so old code keeps working.
# ---------------------------------------------------------------------------
class _CacheProxy:
    """Thin dict-like proxy around the thread-safe store."""

    def __getitem__(self, key):
        with _lock:
            return _store[key]

    def __setitem__(self, key, value):
        with _lock:
            _store[key] = value

    def __delitem__(self, key):
        with _lock:
            del _store[key]

    def __contains__(self, key):
        with _lock:
            return key in _store

    def __len__(self):
        with _lock:
            return len(_store)

    def __iter__(self):
        with _lock:
            return iter(list(_store.keys()))

    def keys(self):
        with _lock:
            return list(_store.keys())

    def values(self):
        with _lock:
            return list(_store.values())

    def items(self):
        with _lock:
            return list(_store.items())

    def get(self, key, default=None):
        with _lock:
            return _store.get(key, default)


# Module-level proxy — import this anywhere that needs dict-like access
repository_cache = _CacheProxy()

# Made with Bob
