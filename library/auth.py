import logging

logger = logging.getLogger(__name__)

def some_function():
  try:
    logger.info("Some info here")
    logger.debug("My debug message")
    raise ValueError("Raised exception")
  except Exception as e:
    logger.exception(e)


def some_audit_function(audit_logger):
  audit_logger.info("This is an an audit log")
  
