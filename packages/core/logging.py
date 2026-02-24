from __future__ import annotations

import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
    )


class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        kwargs.setdefault("extra", {})
        kwargs["extra"].setdefault("request_id", self.extra.get("request_id", "-"))
        return msg, kwargs
