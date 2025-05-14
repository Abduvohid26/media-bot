import datetime
import logging
from pythonjsonlogger import jsonlogger

class MergingLoggerAdapter(logging.LoggerAdapter):
  def process(self, msg, kwargs):
    kwargs["extra"] = (self.extra or {}) | kwargs.get("extra", {}) # type: ignore
    return msg, kwargs

class CustomJsonFormatter(jsonlogger.JsonFormatter):
  def add_fields(self, log_record, record, message_dict):
    super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

    log_record["timestamp"] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    log_record["level"] = record.levelname
    log_record.pop("taskName", None)
