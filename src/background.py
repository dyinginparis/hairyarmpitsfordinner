from __future__ import annotations

from datetime import UTC, datetime
import logging
import threading
from typing import Any

from src.services import RuntimeServices


LOGGER = logging.getLogger(__name__)


class WatchlistMonitor:
    def __init__(self, services: RuntimeServices, interval_seconds: int) -> None:
        self.services = services
        self.interval_seconds = max(1, int(interval_seconds))
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._state: dict[str, Any] = {
            "enabled": True,
            "running": False,
            "intervalSeconds": self.interval_seconds,
            "lastRunAt": None,
            "lastResult": None,
            "lastError": None,
        }

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._state["enabled"] = True
            self._state["running"] = True
            self._thread = threading.Thread(target=self._run, name="watchlist-monitor", daemon=True)
            self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        with self._lock:
            thread = self._thread
            self._stop_event.set()
        if thread and thread.is_alive():
            thread.join(timeout=timeout)
        with self._lock:
            self._state["running"] = False

    def disable(self) -> None:
        with self._lock:
            self._state["enabled"] = False
            self._state["running"] = False

    def status(self) -> dict[str, Any]:
        with self._lock:
            state = dict(self._state)
            state["running"] = bool(self._thread and self._thread.is_alive())
            return state

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                result = self.services.refresh_watchlist_trades(trades_per_wallet=20)
                self.services.reconcile_paper_trading()
                self.services.record_open_position_marks()
                self._update_state(
                    {
                        "running": True,
                        "lastRunAt": datetime.now(UTC).isoformat(),
                        "lastResult": result,
                        "lastError": None,
                    }
                )
            except Exception as error:  # pragma: no cover - defensive background loop
                LOGGER.exception("Watchlist monitor refresh failed")
                self._update_state(
                    {
                        "running": True,
                        "lastRunAt": datetime.now(UTC).isoformat(),
                        "lastError": str(error),
                    }
                )
            self._stop_event.wait(self.interval_seconds)
        self._update_state({"running": False})

    def _update_state(self, updates: dict[str, Any]) -> None:
        with self._lock:
            self._state.update(updates)
