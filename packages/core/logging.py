from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
    )


class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(
        self,
        msg: str,
        kwargs: MutableMapping[str, Any],
    ) -> tuple[str, MutableMapping[str, Any]]:
        kwargs.setdefault("extra", {})
        extra = self.extra or {}
        kwargs["extra"].setdefault("request_id", extra.get("request_id", "-"))
        return msg, kwargs
